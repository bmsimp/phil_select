# Quick Reference Guide

## Application Structure

```
phil_select/
├── app.py                    # Main Flask application
├── philmont_selection.db     # SQLite database (contains all trek data)
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   ├── base.html            # Base layout
│   ├── index.html           # Home page
│   ├── preferences.html     # Crew preferences
│   ├── scores.html          # Program scoring
│   ├── results.html         # Results dashboard
│   └── itinerary_detail.html # Trek details
└── phil_select/             # Python virtual environment
```

## Quick Commands

### Setup (One Time)
```bash
# Clone and setup
git clone https://github.com/bcox-ctv/phil_select.git
cd phil_select
python -m venv phil_select
source phil_select/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Daily Use
```bash
# Start application
cd phil_select
source phil_select/bin/activate  # macOS/Linux
python app.py

# Stop application
# Press Ctrl+C in terminal
```

### Windows Commands
```bash
# Activate virtual environment (Windows)
phil_select\Scripts\activate

# Everything else is the same
```

## Navigation Menu

- **Home** → Main dashboard
- **Preferences** → Set crew preferences and manage members
- **Program Scores** → Rate activity programs (0-20 scale)
- **Results** → View ranked itinerary results
- **Program Chart** → See which programs your crew scored highest
- **Survey** → Alternative scoring interface

## Key URLs

- Main application: `http://127.0.0.1:5002`
- Results: `http://127.0.0.1:5002/results`
- Preferences: `http://127.0.0.1:5002/preferences`
- Program scores: `http://127.0.0.1:5002/scores`

## Scoring Scale

- **Program Scores**: 0-20 (20 = highest interest)
- **Skill Level**: 1-10 (10 = most experienced)
- **Area Ranking**: 1-4 (1 = most preferred)

## Calculation Methods

- **Total** → Sum of all crew member scores
- **Average** → Mean score across all members
- **Median** → Middle score when sorted
- **Mode** → Most frequently occurring score

## Score Components (Typical Ranges)

- **Program Score**: 200-800+ points
- **Camp Score**: 100-600 points  
- **Difficulty Score**: 0 or 2000+ points
- **Distance Score**: 4000-6000 points
- **Area Score**: 0-1000 points (if enabled)
- **Peak Score**: 0-500+ points

## File Sizes (Approximate)

- `app.py`: ~85KB (main application code)
- `philmont_selection.db`: ~2MB (all trek data)
- `requirements.txt`: ~1KB (dependency list)
- Virtual environment: ~50MB (Python packages)

## Common Port Numbers

- Default: `5002` (app.py runs on this port)
- Alternative: `5000` (Flask default)
- Custom: Use `python app.py --port 8080` for port 8080

## Database Contents

- **36 Trek Itineraries** (12-day and 9-day options)
- **56+ Activity Programs** across multiple categories
- **169 Backcountry Camps** with elevation and facility data
- **700+ Program Assignments** linking itineraries to activities

## Backup Your Work

Your preferences and scores are stored in `philmont_selection.db`. To backup:

```bash
# Create backup
cp philmont_selection.db philmont_selection_backup.db

# Restore backup
cp philmont_selection_backup.db philmont_selection.db
```

## Performance Notes

- Initial page load: ~1-2 seconds
- Results calculation: ~2-3 seconds
- Program scoring saves: Immediate
- Database size growth: Minimal (scores are small)

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ Internet Explorer: Not supported