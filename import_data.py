#!/usr/bin/env python3

import sqlite3
import pandas as pd
import json
import re
from pathlib import Path

class PhilmontDataImporter:
    def __init__(self, db_path='philmont_selection.db', excel_path='treks.xlsm'):
        self.db_path = db_path
        self.excel_path = excel_path
        self.conn = None
        
    def connect_db(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
        
    def create_schema(self):
        """Execute the schema creation script"""
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split on semicolons and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for stmt in statements:
            try:
                self.conn.execute(stmt)
            except Exception as e:
                print(f"Error executing statement: {e}")
                print(f"Statement: {stmt[:100]}...")
        
        self.conn.commit()
        print("Database schema created successfully")
        
    def import_programs(self):
        """Import programs from Programs sheet"""
        print("Importing programs...")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Programs')
            
            programs = []
            for _, row in df.iterrows():
                if pd.notna(row.get('Programs (56)', '')) and row.get('Programs (56)', '') != 'Programs (56)':
                    name = str(row['Programs (56)']).strip()
                    if name and not name.startswith('Programs'):
                        # Extract category from name (e.g., "Climbing: Bouldering Gym" -> category="Climbing")
                        category = name.split(':')[0] if ':' in name else 'General'
                        
                        # Generate a code
                        code = re.sub(r'[^A-Za-z0-9]', '_', name.replace(':', '_').replace(' ', '_'))[:20]
                        
                        old_name = str(row.get('Old Program Name/Comments', '')) if pd.notna(row.get('Old Program Name/Comments', '')) else None
                        
                        programs.append((code, name, category, old_name))
            
            # Insert programs
            self.conn.executemany('''
                INSERT OR IGNORE INTO programs (code, name, category, old_name_comments)
                VALUES (?, ?, ?, ?)
            ''', programs)
            
            self.conn.commit()
            print(f"Imported {len(programs)} programs")
            
        except Exception as e:
            print(f"Error importing programs: {e}")
    
    def import_camps(self):
        """Import camps from Camp Elevations sheet"""
        print("Importing camps...")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Camp Elevations')
            
            camps = []
            for _, row in df.iterrows():
                name = str(row.get('CAMP NAME', '')).strip()
                if name and name != 'CAMP NAME' and name != 'nan':
                    country = str(row.get('Country', '')) if pd.notna(row.get('Country', '')) else None
                    easting = int(row['Easting']) if pd.notna(row.get('Easting')) else None
                    northing = int(row['Northing']) if pd.notna(row.get('Northing')) else None
                    elevation = int(row['ELEVATION ']) if pd.notna(row.get('ELEVATION ')) else None
                    
                    # Boolean fields
                    has_commissary = str(row.get('Commissary', '')).upper() == 'Y'
                    has_trading_post = str(row.get('Trading Post', '')).upper() == 'Y'
                    is_staffed = str(row.get('Staffed', '')).upper() == 'Y'
                    is_trail_camp = str(row.get('Trail Camp', '')).upper() == 'Y'
                    is_dry_camp = str(row.get('Dry Camp', '')).upper() == 'Y'
                    has_showers = str(row.get('Showers', '')).upper() == 'Y'
                    
                    camp_map = str(row.get('campMap', '')) if pd.notna(row.get('campMap', '')) else None
                    added_year = int(row['Added']) if pd.notna(row.get('Added')) and str(row.get('Added')).isdigit() else None
                    
                    camps.append((
                        name, country, easting, northing, elevation,
                        has_commissary, has_trading_post, is_staffed, 
                        is_trail_camp, is_dry_camp, has_showers,
                        camp_map, added_year
                    ))
            
            # Insert camps
            self.conn.executemany('''
                INSERT OR IGNORE INTO camps 
                (name, country, easting, northing, elevation, has_commissary, has_trading_post, 
                 is_staffed, is_trail_camp, is_dry_camp, has_showers, camp_map, added_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', camps)
            
            self.conn.commit()
            print(f"Imported {len(camps)} camps")
            
        except Exception as e:
            print(f"Error importing camps: {e}")
    
    def import_itineraries(self):
        """Import itineraries from multiple sheets"""
        print("Importing itineraries...")
        
        try:
            # Read from Itineraries sheet for basic info
            itineraries_df = pd.read_excel(self.excel_path, sheet_name='Itineraries')
            
            # Read from itineraryCamps for detailed info
            camps_df = pd.read_excel(self.excel_path, sheet_name='itineraryCamps')
            
            # Read descriptions
            desc_df = pd.read_excel(self.excel_path, sheet_name='Descriptions')
            
            itineraries = []
            
            # Process each itinerary
            for idx, row in itineraries_df.iterrows():
                if idx == 0:  # Skip header
                    continue
                    
                itinerary_code = str(row.get('Unnamed: 0', '')).strip()
                if not itinerary_code or itinerary_code == 'Itinerary' or 'nan' in itinerary_code:
                    continue
                
                # Get corresponding row from camps sheet
                camps_row = None
                for _, camp_row in camps_df.iterrows():
                    camp_itin = str(camp_row.get('(Enter Red columns manually)\n\n\nItinerary', '')).strip()
                    if camp_itin == itinerary_code:
                        camps_row = camp_row
                        break
                
                # Get description
                description = None
                for _, desc_row in desc_df.iterrows():
                    if str(desc_row.get('Itinerary', '')).strip() == itinerary_code:
                        description = str(desc_row.get('Description', ''))[:1000]  # Limit length
                        break
                
                # Extract basic data
                days_food = int(row['Unnamed: 1']) if pd.notna(row.get('Unnamed: 1')) else None
                max_days_food = int(row['Unnamed: 2']) if pd.notna(row.get('Unnamed: 2')) else None
                staffed_camps = int(row['Unnamed: 3']) if pd.notna(row.get('Unnamed: 3')) else None
                trail_camps = int(row['Unnamed: 4']) if pd.notna(row.get('Unnamed: 4')) else None
                layovers = int(row['Unnamed: 5']) if pd.notna(row.get('Unnamed: 5')) else None
                total_camps = int(row['Unnamed: 6']) if pd.notna(row.get('Unnamed: 6')) else None
                dry_camps = int(row['Unnamed: 7']) if pd.notna(row.get('Unnamed: 7')) else None
                min_altitude = int(row['Unnamed: 8']) if pd.notna(row.get('Unnamed: 8')) else None
                max_altitude = int(row['Unnamed: 9']) if pd.notna(row.get('Unnamed: 9')) else None
                
                # Get additional data from camps sheet if available
                difficulty = None
                distance = None
                if camps_row is not None:
                    difficulty = str(camps_row.get('Unnamed: 1', '')).strip() if pd.notna(camps_row.get('Unnamed: 1')) else None
                    distance = int(camps_row.get('Unnamed: 2')) if pd.notna(camps_row.get('Unnamed: 2')) else None
                
                # Regional coverage (from Itineraries sheet columns)
                covers_south = str(row.get('Region', '')).strip().upper() == 'Y' if 'Region' in row else False
                covers_central = str(row.get('Unnamed: 16', '')).strip().upper() == 'Y' if pd.notna(row.get('Unnamed: 16')) else False
                covers_north = str(row.get('Unnamed: 17', '')).strip().upper() == 'Y' if pd.notna(row.get('Unnamed: 17')) else False
                covers_valle_vidal = str(row.get('Unnamed: 18', '')).strip().upper() == 'Y' if pd.notna(row.get('Unnamed: 18')) else False
                
                itineraries.append((
                    itinerary_code, None, difficulty, distance, days_food, max_days_food,
                    staffed_camps, trail_camps, layovers, total_camps, dry_camps,
                    min_altitude, max_altitude, None, None, description,
                    None, None, False, False, None, None,  # Various other fields
                    False, False, False, False, False, False,  # Peak flags
                    covers_south, covers_central, covers_north, covers_valle_vidal
                ))
            
            # Insert itineraries
            self.conn.executemany('''
                INSERT OR IGNORE INTO itineraries 
                (itinerary_code, expedition_number, difficulty, distance, days_food_from_base, max_days_food,
                 staffed_camps, trail_camps, layovers, total_camps, dry_camps, min_altitude, max_altitude,
                 total_elevation_gain, avg_daily_elevation_change, description, starts_at, ends_at,
                 via_tooth, crosses_us64, us64_crossing_day, us64_crossing_direction,
                 baldy_mountain, inspiration_point, mount_phillips, mountaineering, tooth_of_time, trail_peak,
                 covers_south, covers_central, covers_north, covers_valle_vidal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', itineraries)
            
            self.conn.commit()
            print(f"Imported {len(itineraries)} itineraries")
            
        except Exception as e:
            print(f"Error importing itineraries: {e}")
            import traceback
            traceback.print_exc()
    
    def import_itinerary_camps(self):
        """Import daily camp assignments for each itinerary"""
        print("Importing itinerary camps...")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name='itineraryCamps')
            
            itinerary_camps = []
            
            for idx, row in df.iterrows():
                if idx < 2:  # Skip headers
                    continue
                
                itinerary_code = str(row.get('(Enter Red columns manually)\n\n\nItinerary', '')).strip()
                if not itinerary_code or 'nan' in itinerary_code:
                    continue
                
                # Get itinerary ID
                cursor = self.conn.execute('SELECT id FROM itineraries WHERE itinerary_code = ?', (itinerary_code,))
                itin_result = cursor.fetchone()
                if not itin_result:
                    continue
                itinerary_id = itin_result[0]
                
                # Process each day (columns represent days 2-11)
                day_columns = [col for col in df.columns if isinstance(col, int) and 2 <= col <= 11]
                
                for day_num in day_columns:
                    camp_name = str(row.get(day_num, '')).strip()
                    if camp_name and camp_name != 'nan':
                        # Get camp ID
                        cursor = self.conn.execute('SELECT id FROM camps WHERE name = ?', (camp_name,))
                        camp_result = cursor.fetchone()
                        if camp_result:
                            camp_id = camp_result[0]
                            itinerary_camps.append((itinerary_id, day_num, camp_id, False, False))
            
            # Insert itinerary camps
            if itinerary_camps:
                self.conn.executemany('''
                    INSERT OR IGNORE INTO itinerary_camps 
                    (itinerary_id, day_number, camp_id, is_layover, food_pickup)
                    VALUES (?, ?, ?, ?, ?)
                ''', itinerary_camps)
            
            self.conn.commit()
            print(f"Imported {len(itinerary_camps)} itinerary camp assignments")
            
        except Exception as e:
            print(f"Error importing itinerary camps: {e}")
            import traceback
            traceback.print_exc()
    
    def create_sample_crew(self):
        """Create a sample crew for testing"""
        print("Creating sample crew...")
        
        # Insert sample crew
        self.conn.execute('''
            INSERT OR IGNORE INTO crews (id, crew_name, crew_size)
            VALUES (1, 'Sample Crew', 9)
        ''')
        
        # Insert sample crew members
        for i in range(1, 10):
            self.conn.execute('''
                INSERT OR IGNORE INTO crew_members (crew_id, member_number, name, age, skill_level)
                VALUES (1, ?, ?, ?, ?)
            ''', (i, f'Crewmember {i}', 16, 3))
        
        # Insert default preferences
        self.conn.execute('''
            INSERT OR IGNORE INTO crew_preferences 
            (crew_id, area_important, difficulty_challenging, difficulty_rugged, difficulty_strenuous, difficulty_super_strenuous)
            VALUES (1, TRUE, TRUE, TRUE, TRUE, TRUE)
        ''')
        
        self.conn.commit()
        print("Sample crew created")
    
    def run_full_import(self):
        """Run complete data import process"""
        print("Starting Philmont data import...")
        
        self.connect_db()
        
        try:
            self.create_schema()
            self.import_programs()
            self.import_camps()
            self.import_itineraries()
            self.import_itinerary_camps()
            self.create_sample_crew()
            
            print("\nData import completed successfully!")
            
            # Print summary statistics
            cursor = self.conn.execute('SELECT COUNT(*) FROM programs')
            print(f"Programs: {cursor.fetchone()[0]}")
            
            cursor = self.conn.execute('SELECT COUNT(*) FROM camps')
            print(f"Camps: {cursor.fetchone()[0]}")
            
            cursor = self.conn.execute('SELECT COUNT(*) FROM itineraries')
            print(f"Itineraries: {cursor.fetchone()[0]}")
            
            cursor = self.conn.execute('SELECT COUNT(*) FROM itinerary_camps')
            print(f"Itinerary camp assignments: {cursor.fetchone()[0]}")
            
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    importer = PhilmontDataImporter()
    importer.run_full_import()