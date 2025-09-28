#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import json
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'philmont-trek-selection-2025'

def get_db_connection():
    conn = sqlite3.connect('philmont_selection.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# ===================================
# Helper Functions
# ===================================

def get_crew_info(crew_id=1):
    """Get crew information"""
    conn = get_db_connection()
    
    crew = conn.execute('SELECT * FROM crews WHERE id = ?', (crew_id,)).fetchone()
    crew_members = conn.execute(
        'SELECT * FROM crew_members WHERE crew_id = ? ORDER BY member_number', 
        (crew_id,)
    ).fetchall()
    preferences = conn.execute(
        'SELECT * FROM crew_preferences WHERE crew_id = ?', 
        (crew_id,)
    ).fetchone()
    
    conn.close()
    return crew, crew_members, preferences

def get_programs():
    """Get all programs"""
    conn = get_db_connection()
    programs = conn.execute('SELECT * FROM programs ORDER BY category, name').fetchall()
    conn.close()
    return programs

def get_existing_scores(crew_id=1):
    """Get existing program scores for a crew"""
    conn = get_db_connection()
    scores = conn.execute('''
        SELECT crew_member_id, program_id, score 
        FROM program_scores 
        WHERE crew_id = ?
    ''', (crew_id,)).fetchall()
    conn.close()
    
    score_dict = {}
    for score in scores:
        key = f"{score['crew_member_id']}_{score['program_id']}"
        score_dict[key] = score['score']
    
    return score_dict

# ===================================
# Scoring Logic (Replicated from Excel)
# ===================================

class PhilmontScorer:
    def __init__(self, crew_id):
        self.crew_id = crew_id
        
    def get_program_scores(self, method='Total'):
        """Calculate program scores using specified method (Total, Average, Median, Mode)"""
        conn = get_db_connection()
        
        # Get all program scores for the crew
        scores = conn.execute('''
            SELECT p.id, p.name, ps.score
            FROM programs p
            JOIN program_scores ps ON p.id = ps.program_id
            WHERE ps.crew_id = ?
            ORDER BY p.id, ps.crew_member_id
        ''', (self.crew_id,)).fetchall()
        
        program_scores = {}
        current_program = None
        current_scores = []
        
        for score in scores:
            program_id = score['id']
            score_value = score['score']
            
            if current_program != program_id:
                if current_program is not None and current_scores:
                    program_scores[current_program] = self._calculate_aggregate(current_scores, method)
                current_program = program_id
                current_scores = [score_value]
            else:
                current_scores.append(score_value)
        
        # Don't forget the last program
        if current_program is not None and current_scores:
            program_scores[current_program] = self._calculate_aggregate(current_scores, method)
        
        conn.close()
        return program_scores
    
    def _calculate_aggregate(self, scores, method):
        """Calculate aggregate score using specified method"""
        if method == 'Total':
            return sum(scores)
        elif method == 'Average':
            return sum(scores) / len(scores)
        elif method == 'Median':
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            if n % 2 == 0:
                return (sorted_scores[n//2-1] + sorted_scores[n//2]) / 2
            else:
                return sorted_scores[n//2]
        elif method == 'Mode':
            from collections import Counter
            counter = Counter(scores)
            return counter.most_common(1)[0][0]
        else:
            return sum(scores)  # Default to total
    
    def calculate_itinerary_scores(self, method='Total'):
        """Calculate total scores for all itineraries"""
        program_scores = self.get_program_scores(method)
        crew_prefs = self._get_crew_preferences()
        
        conn = get_db_connection()
        
        # Get all itineraries
        itineraries = conn.execute('SELECT * FROM itineraries ORDER BY itinerary_code').fetchall()
        
        results = []
        
        for itin in itineraries:
            score_components = {
                'program_score': self._calculate_program_score(itin['id'], program_scores, conn),
                'difficulty_score': self._calculate_difficulty_score(itin, crew_prefs),
                'area_score': self._calculate_area_score(itin, crew_prefs),
                'altitude_score': self._calculate_altitude_score(itin, crew_prefs),
                'distance_score': self._calculate_distance_score(itin, crew_prefs)
            }
            
            total_score = sum(score_components.values())
            
            results.append({
                'itinerary': dict(itin),
                'total_score': total_score,
                'components': score_components
            })
        
        # Sort by total score (descending)
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add rankings
        for i, result in enumerate(results, 1):
            result['ranking'] = i
        
        conn.close()
        return results
    
    def _get_crew_preferences(self):
        """Get crew preferences"""
        conn = get_db_connection()
        prefs = conn.execute('SELECT * FROM crew_preferences WHERE crew_id = ?', (self.crew_id,)).fetchone()
        conn.close()
        
        return dict(prefs) if prefs else {}
    
    def _calculate_program_score(self, itinerary_id, program_scores, conn):
        """Calculate program score for an itinerary"""
        # Get programs available for this itinerary
        available_programs = conn.execute('''
            SELECT ip.program_id 
            FROM itinerary_programs ip 
            WHERE ip.itinerary_id = ? AND ip.is_available = 1
        ''', (itinerary_id,)).fetchall()
        
        # Sum scores for available programs
        total_score = 0
        for prog in available_programs:
            program_id = prog['program_id']
            if program_id in program_scores:
                total_score += program_scores[program_id]
        
        # Apply program factor (typically 1.5x)
        program_factor = 1.5
        return total_score * program_factor
    
    def _calculate_difficulty_score(self, itinerary, crew_prefs):
        """Calculate difficulty-based score"""
        difficulty = itinerary['difficulty']
        
        # Check if crew accepts this difficulty level
        difficulty_accepted = False
        if difficulty == 'C' and crew_prefs.get('difficulty_challenging', True):
            difficulty_accepted = True
        elif difficulty == 'R' and crew_prefs.get('difficulty_rugged', True):
            difficulty_accepted = True
        elif difficulty == 'S' and crew_prefs.get('difficulty_strenuous', True):
            difficulty_accepted = True
        elif difficulty == 'SS' and crew_prefs.get('difficulty_super_strenuous', True):
            difficulty_accepted = True
        
        return 100 if difficulty_accepted else 0
    
    def _calculate_area_score(self, itinerary, crew_prefs):
        """Calculate area preference score"""
        if not crew_prefs.get('area_important', False):
            return 0
        
        area_scores = {
            'covers_south': crew_prefs.get('area_rank_south', 0),
            'covers_central': crew_prefs.get('area_rank_central', 0),
            'covers_north': crew_prefs.get('area_rank_north', 0),
            'covers_valle_vidal': crew_prefs.get('area_rank_valle_vidal', 0)
        }
        
        score = 0
        for area_field, rank in area_scores.items():
            if itinerary[area_field] and rank:
                # Higher rank (1-4) gives more points
                score += (5 - rank) * 25
        
        return score
    
    def _calculate_altitude_score(self, itinerary, crew_prefs):
        """Calculate altitude-based score"""
        score = 0
        
        max_altitude = itinerary['max_altitude'] or 0
        if crew_prefs.get('max_altitude_important', False):
            threshold = crew_prefs.get('max_altitude_threshold', 10000)
            if max_altitude <= threshold:
                score += 50
        
        return score
    
    def _calculate_distance_score(self, itinerary, crew_prefs):
        """Calculate distance-based score"""
        distance = itinerary['distance'] or 50
        return max(0, 100 - abs(distance - 50))  # Prefer distances around 50 miles

# ===================================
# Helper Functions for Score Management
# ===================================

def recalculate_crew_scores(crew_id):
    """Recalculate and cache crew program scores for faster access"""
    conn = get_db_connection()
    
    try:
        # Calculate aggregate scores for each program using different methods
        scorer = PhilmontScorer(crew_id)
        
        methods = ['Total', 'Average', 'Median']
        
        for method in methods:
            program_scores = scorer.get_program_scores(method)
            
            # Store or update cached scores (you could create a crew_program_scores table)
            # For now, we'll just ensure the calculation works and log it
            print(f"Recalculated {method} scores for crew {crew_id}: {len(program_scores)} programs")
        
        # Update crew preferences if needed (mark that scores have been updated)
        conn.execute('''
            UPDATE crews 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (crew_id,))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error recalculating scores for crew {crew_id}: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def invalidate_crew_cache(crew_id):
    """Invalidate any cached calculations for a crew"""
    # This function can be used if we implement caching in the future
    pass

# ===================================
# Routes
# ===================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/preferences')
def preferences():
    """Crew preferences page"""
    crew_id = 1  # Default to sample crew
    crew, crew_members, preferences = get_crew_info(crew_id)
    
    return render_template('preferences.html', 
                         crew=crew, 
                         crew_members=crew_members, 
                         preferences=preferences)

@app.route('/preferences', methods=['POST'])
def save_preferences():
    """Save crew preferences"""
    crew_id = 1  # Default to sample crew
    conn = get_db_connection()
    
    def safe_int(value):
        """Safely convert form value to int or None"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    # Check if preferences exist
    existing = conn.execute('SELECT id FROM crew_preferences WHERE crew_id = ?', (crew_id,)).fetchone()
    
    if existing:
        # Update existing preferences
        conn.execute('''
            UPDATE crew_preferences SET
                area_important = ?,
                area_rank_south = ?,
                area_rank_central = ?,
                area_rank_north = ?,
                area_rank_valle_vidal = ?,
                max_altitude_important = ?,
                max_altitude_threshold = ?,
                difficulty_challenging = ?,
                difficulty_rugged = ?,
                difficulty_strenuous = ?,
                difficulty_super_strenuous = ?,
                climb_baldy = ?,
                climb_phillips = ?,
                climb_tooth = ?,
                climb_inspiration_point = ?,
                programs_important = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE crew_id = ?
        ''', (
            'area_important' in request.form,
            safe_int(request.form.get('area_rank_south')),
            safe_int(request.form.get('area_rank_central')),
            safe_int(request.form.get('area_rank_north')),
            safe_int(request.form.get('area_rank_valle_vidal')),
            'max_altitude_important' in request.form,
            safe_int(request.form.get('max_altitude_threshold')),
            'difficulty_challenging' in request.form,
            'difficulty_rugged' in request.form,
            'difficulty_strenuous' in request.form,
            'difficulty_super_strenuous' in request.form,
            'climb_baldy' in request.form,
            'climb_phillips' in request.form,
            'climb_tooth' in request.form,
            'climb_inspiration_point' in request.form,
            'programs_important' in request.form,
            crew_id
        ))
    else:
        # Insert new preferences
        conn.execute('''
            INSERT INTO crew_preferences 
            (crew_id, area_important, area_rank_south, area_rank_central, area_rank_north, area_rank_valle_vidal,
             max_altitude_important, max_altitude_threshold, difficulty_challenging, difficulty_rugged, 
             difficulty_strenuous, difficulty_super_strenuous, climb_baldy, climb_phillips, climb_tooth, 
             climb_inspiration_point, programs_important)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            crew_id,
            'area_important' in request.form,
            safe_int(request.form.get('area_rank_south')),
            safe_int(request.form.get('area_rank_central')),
            safe_int(request.form.get('area_rank_north')),
            safe_int(request.form.get('area_rank_valle_vidal')),
            'max_altitude_important' in request.form,
            safe_int(request.form.get('max_altitude_threshold')),
            'difficulty_challenging' in request.form,
            'difficulty_rugged' in request.form,
            'difficulty_strenuous' in request.form,
            'difficulty_super_strenuous' in request.form,
            'climb_baldy' in request.form,
            'climb_phillips' in request.form,
            'climb_tooth' in request.form,
            'climb_inspiration_point' in request.form,
            'programs_important' in request.form
        ))
    
    conn.commit()
    conn.close()
    flash('Preferences saved successfully!', 'success')
    
    return redirect(url_for('preferences'))

@app.route('/scores')
def scores():
    """Program scoring page"""
    crew_id = 1  # Default to sample crew
    
    crew, crew_members, _ = get_crew_info(crew_id)
    programs = get_programs()
    existing_scores = get_existing_scores(crew_id)
    
    return render_template('scores.html', 
                         crew=crew, 
                         crew_members=crew_members, 
                         programs=programs,
                         existing_scores=existing_scores)

@app.route('/scores', methods=['POST'])
def save_scores():
    """Save program scores"""
    crew_id = 1  # Default to sample crew
    conn = get_db_connection()
    
    # Delete existing scores for this crew
    conn.execute('DELETE FROM program_scores WHERE crew_id = ?', (crew_id,))
    
    # Save new scores
    for key, value in request.form.items():
        if key.startswith('score_') and value and value.strip():
            parts = key.split('_')
            if len(parts) == 3:
                try:
                    member_id = int(parts[1])
                    program_id = int(parts[2])
                    score_value = int(value)
                except (ValueError, TypeError):
                    continue  # Skip invalid values
                
                conn.execute('''
                    INSERT INTO program_scores (crew_id, crew_member_id, program_id, score)
                    VALUES (?, ?, ?, ?)
                ''', (crew_id, member_id, program_id, score_value))
    
    conn.commit()
    conn.close()
    flash('Scores saved successfully!', 'success')
    
    return redirect(url_for('scores'))

@app.route('/results')
def results():
    """Results and rankings page"""
    crew_id = 1  # Default to sample crew
    method = request.args.get('method', 'Total')
    
    scorer = PhilmontScorer(crew_id)
    results = scorer.calculate_itinerary_scores(method)
    
    return render_template('results.html', 
                         results=results, 
                         calculation_method=method)

@app.route('/api/calculate')
def api_calculate():
    """API endpoint to recalculate scores"""
    crew_id = request.args.get('crew_id', 1, type=int)
    method = request.args.get('method', 'Total')
    
    scorer = PhilmontScorer(crew_id)
    results = scorer.calculate_itinerary_scores(method)
    
    # Convert to JSON-friendly format
    json_results = []
    for result in results:
        json_results.append({
            'itinerary_code': result['itinerary']['itinerary_code'],
            'total_score': result['total_score'],
            'ranking': result['ranking'],
            'components': result['components']
        })
    
    return jsonify(json_results)

@app.route('/api/crew_members/<int:crew_id>')
def api_crew_members(crew_id):
    """API endpoint to get crew members for a specific crew"""
    conn = get_db_connection()
    
    crew_members = conn.execute('''
        SELECT id, name, email, age, skill_level
        FROM crew_members 
        WHERE crew_id = ? 
        ORDER BY member_number
    ''', (crew_id,)).fetchall()
    
    conn.close()
    
    # Convert to JSON-friendly format
    members = []
    for member in crew_members:
        members.append({
            'id': member['id'],
            'name': member['name'],
            'email': member['email'],
            'age': member['age'],
            'skill_level': member['skill_level']
        })
    
    return jsonify(members)

@app.route('/itinerary/<code>')
def itinerary_detail(code):
    """Detailed view of a specific itinerary"""
    conn = get_db_connection()
    
    itinerary = conn.execute('SELECT * FROM itineraries WHERE itinerary_code = ?', (code,)).fetchone()
    if not itinerary:
        flash(f'Itinerary {code} not found', 'error')
        return redirect(url_for('results'))
    
    # Get camps for this itinerary
    camps = conn.execute('''
        SELECT ic.day_number, c.name, c.elevation, c.country, c.is_staffed, c.is_trail_camp
        FROM itinerary_camps ic
        JOIN camps c ON ic.camp_id = c.id
        WHERE ic.itinerary_id = ?
        ORDER BY ic.day_number
    ''', (itinerary['id'],)).fetchall()
    
    conn.close()
    
    return render_template('itinerary_detail.html', 
                         itinerary=itinerary, 
                         camps=camps)

@app.route('/survey')
def survey():
    """Crew member program survey page"""
    # Get all programs organized by category
    programs = get_programs()
    
    # Get all crews for the dropdown
    conn = get_db_connection()
    crews = conn.execute('SELECT * FROM crews ORDER BY crew_name').fetchall()
    conn.close()
    
    return render_template('survey.html', programs=programs, crews=crews)

@app.route('/survey', methods=['POST'])
def submit_survey():
    """Process crew member program survey submission"""
    conn = get_db_connection()
    
    def safe_int(value):
        """Safely convert form value to int or None"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    # Get form data
    member_type = request.form.get('member_type', 'new')
    existing_member_id = safe_int(request.form.get('existing_member_id'))
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    crew_id = safe_int(request.form.get('crew_id'))
    age = safe_int(request.form.get('age'))
    skill_level = safe_int(request.form.get('skill_level', 3))
    
    # Validate required fields based on member type
    if not crew_id:
        flash('Please select a crew.', 'error')
        return redirect(url_for('survey'))
    
    if member_type == 'existing':
        if not existing_member_id:
            flash('Please select an existing crew member.', 'error')
            return redirect(url_for('survey'))
    else:
        if not name or not email:
            flash('Please fill in all required fields (Name and Email).', 'error')
            return redirect(url_for('survey'))
    
    try:
        if member_type == 'existing' and existing_member_id:
            # Use existing crew member
            member_id = existing_member_id
            # Update their info if provided
            if name or email or age or skill_level:
                conn.execute('''
                    UPDATE crew_members 
                    SET name = COALESCE(?, name), 
                        email = COALESCE(?, email), 
                        age = COALESCE(?, age), 
                        skill_level = COALESCE(?, skill_level)
                    WHERE id = ? AND crew_id = ?
                ''', (name or None, email or None, age, skill_level, member_id, crew_id))
        else:
            # Handle new member creation or update existing member by email/name match
            existing_member = None
            if email:
                existing_member = conn.execute(
                    'SELECT * FROM crew_members WHERE crew_id = ? AND email = ?', 
                    (crew_id, email)
                ).fetchone()
            
            if not existing_member and name:
                # Check by name and crew if no email match
                existing_member = conn.execute(
                    'SELECT * FROM crew_members WHERE crew_id = ? AND name = ?', 
                    (crew_id, name)
                ).fetchone()
            
            if existing_member:
                member_id = existing_member['id']
                # Update existing crew member info including email
                conn.execute('''
                    UPDATE crew_members 
                    SET name = ?, email = ?, age = ?, skill_level = ?
                    WHERE id = ?
                ''', (name, email, age, skill_level, member_id))
            else:
                # Get next member number for this crew
                max_member = conn.execute(
                    'SELECT MAX(member_number) as max_num FROM crew_members WHERE crew_id = ?', 
                    (crew_id,)
                ).fetchone()
                member_number = (max_member['max_num'] or 0) + 1
                
                # Insert new crew member with email
                cursor = conn.execute('''
                    INSERT INTO crew_members (crew_id, member_number, name, email, age, skill_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (crew_id, member_number, name, email, age, skill_level))
                member_id = cursor.lastrowid
        
        # Process program scores
        programs = get_programs()
        
        # Delete existing scores for this crew member
        conn.execute('DELETE FROM program_scores WHERE crew_member_id = ?', (member_id,))
        
        # Insert new scores
        for program in programs:
            score_value = safe_int(request.form.get(f'program_{program["id"]}', 10))
            if score_value is not None:
                conn.execute('''
                    INSERT INTO program_scores (crew_id, crew_member_id, program_id, score)
                    VALUES (?, ?, ?, ?)
                ''', (crew_id, member_id, program['id'], score_value))
        
        conn.commit()
        
        # Recalculate crew program scores after survey update
        try:
            recalculate_crew_scores(crew_id)
            flash(f'Survey submitted successfully for {name}! Crew scores have been updated.', 'success')
        except Exception as e:
            flash(f'Survey submitted for {name}, but there was an issue updating crew scores: {str(e)}', 'warning')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error submitting survey: {str(e)}', 'error')
        return redirect(url_for('survey'))
    finally:
        conn.close()
    
    return redirect(url_for('survey'))

@app.route('/admin')
def admin():
    """Admin page for managing crew members"""
    selected_crew_id = request.args.get('crew_id', type=int)
    
    conn = get_db_connection()
    
    # Get all crews
    crews = conn.execute('SELECT * FROM crews ORDER BY crew_name').fetchall()
    
    selected_crew = None
    crew_members = []
    
    if selected_crew_id:
        # Get selected crew info
        selected_crew = conn.execute('SELECT * FROM crews WHERE id = ?', (selected_crew_id,)).fetchone()
        
        if selected_crew:
            # Get crew members with survey completion status
            crew_members = conn.execute('''
                SELECT cm.*, 
                       CASE 
                           WHEN EXISTS (
                               SELECT 1 FROM program_scores ps 
                               WHERE ps.crew_member_id = cm.id
                           ) THEN 1 
                           ELSE 0 
                       END as survey_completed
                FROM crew_members cm 
                WHERE cm.crew_id = ? 
                ORDER BY cm.member_number
            ''', (selected_crew_id,)).fetchall()
    
    conn.close()
    
    return render_template('admin.html', 
                         crews=crews, 
                         selected_crew=selected_crew,
                         selected_crew_id=selected_crew_id,
                         crew_members=crew_members)

@app.route('/admin/add_crew', methods=['POST'])
def add_crew():
    """Add a new crew"""
    crew_name = request.form.get('crew_name', '').strip()
    crew_size = request.form.get('crew_size', 9, type=int)
    
    if not crew_name:
        flash('Crew name is required.', 'error')
        return redirect(url_for('admin'))
    
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            INSERT INTO crews (crew_name, crew_size) 
            VALUES (?, ?)
        ''', (crew_name, crew_size))
        
        conn.commit()
        flash(f'Crew "{crew_name}" created successfully!', 'success')
        return redirect(url_for('admin', crew_id=cursor.lastrowid))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error creating crew: {str(e)}', 'error')
        return redirect(url_for('admin'))
    finally:
        conn.close()

@app.route('/admin/add_member', methods=['POST'])
def add_member():
    """Add a new crew member"""
    crew_id = request.form.get('crew_id', type=int)
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    age = request.form.get('age', type=int)
    skill_level = request.form.get('skill_level', 3, type=int)
    
    if not crew_id or not name:
        flash('Crew and name are required.', 'error')
        return redirect(url_for('admin', crew_id=crew_id))
    
    conn = get_db_connection()
    
    try:
        # Get next member number for this crew
        max_member = conn.execute(
            'SELECT MAX(member_number) as max_num FROM crew_members WHERE crew_id = ?', 
            (crew_id,)
        ).fetchone()
        member_number = (max_member['max_num'] or 0) + 1
        
        # Insert new crew member with email
        conn.execute('''
            INSERT INTO crew_members (crew_id, member_number, name, email, age, skill_level)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (crew_id, member_number, name, email, age, skill_level))
        
        # If email is provided, we could store it in a separate table or extend the crew_members table
        # For now, let's extend the crew_members table to include email
        
        conn.commit()
        flash(f'Crew member "{name}" added successfully!', 'success')
        
        # Note: No need to recalculate scores here since new member has no program scores yet
        
    except Exception as e:
        conn.rollback()
        flash(f'Error adding crew member: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin', crew_id=crew_id))

@app.route('/admin/edit_member', methods=['POST'])
def edit_member():
    """Edit an existing crew member"""
    member_id = request.form.get('member_id', type=int)
    crew_id = request.form.get('crew_id', type=int)
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    age = request.form.get('age', type=int)
    skill_level = request.form.get('skill_level', 3, type=int)
    
    if not member_id or not name:
        flash('Member ID and name are required.', 'error')
        return redirect(url_for('admin', crew_id=crew_id))
    
    conn = get_db_connection()
    
    try:
        conn.execute('''
            UPDATE crew_members 
            SET name = ?, email = ?, age = ?, skill_level = ?
            WHERE id = ?
        ''', (name, email, age, skill_level, member_id))
        
        conn.commit()
        
        # Recalculate crew scores after member info update (in case skill level affects scoring)
        try:
            recalculate_crew_scores(crew_id)
            flash(f'Crew member "{name}" updated successfully! Crew scores have been updated.', 'success')
        except Exception as e:
            flash(f'Crew member "{name}" updated, but there was an issue updating crew scores: {str(e)}', 'warning')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating crew member: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin', crew_id=crew_id))

@app.route('/admin/delete_member', methods=['POST'])
def delete_member():
    """Delete a crew member and all associated data"""
    member_id = request.form.get('member_id', type=int)
    crew_id = request.form.get('crew_id', type=int)
    
    if not member_id:
        flash('Member ID is required.', 'error')
        return redirect(url_for('admin', crew_id=crew_id))
    
    conn = get_db_connection()
    
    try:
        # Delete program scores first (foreign key constraint)
        conn.execute('DELETE FROM program_scores WHERE crew_member_id = ?', (member_id,))
        
        # Delete the crew member
        cursor = conn.execute('DELETE FROM crew_members WHERE id = ?', (member_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            
            # Recalculate crew scores after member deletion
            try:
                recalculate_crew_scores(crew_id)
                flash('Crew member deleted successfully! Crew scores have been updated.', 'success')
            except Exception as e:
                flash(f'Crew member deleted, but there was an issue updating crew scores: {str(e)}', 'warning')
        else:
            flash('Crew member not found.', 'error')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting crew member: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin', crew_id=crew_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)