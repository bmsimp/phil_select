# Philmont Trek Selection System

A Python web application that helps Scout crews evaluate and rank Philmont Scout Ranch trek itineraries based on their preferences and activity interests. This system replicates the functionality of the original Excel-based selection tool in an easy-to-use web interface.

## 🚀 Quick Start

**New to this app?** → Read the **[Getting Started Guide](GETTING_STARTED.md)**

**Need quick commands?** → Check the **[Quick Reference](QUICK_REFERENCE.md)**

### Fastest Setup
```bash
git clone https://github.com/bcox-ctv/phil_select.git
cd phil_select
python -m venv phil_select
source phil_select/bin/activate  # On macOS/Linux
pip install -r requirements.txt
python app.py
```
Then open: http://127.0.0.1:5002

## Features

- **Complete Trek Database**: All 36 Philmont itineraries with detailed information
- **Smart Scoring System**: Multi-factor algorithm considering preferences, programs, difficulty, and logistics
- **Flexible Preferences**: Configure area preferences, difficulty levels, altitude factors, and peak climbing goals
- **Program Rating**: Score 56+ activity programs for each crew member (0-20 scale)
- **Multiple Calculation Methods**: Total, Average, Median, and Mode scoring
- **Detailed Results**: Ranked itinerary list with complete scoring breakdown
- **Trek Details**: Day-by-day schedules, camps, elevation profiles, and available programs

## Database Contents

- **36 Trek Itineraries** (12-day and 9-day options)
- **56+ Activity Programs** (climbing, historical, STEM, nature, crafts, etc.)
- **169 Backcountry Camps** with elevation and facility data
- **700+ Program Assignments** linking itineraries to available activities

## How It Works

1. **Set Preferences**: Configure your crew's difficulty acceptance, area preferences, altitude considerations, and peak climbing goals
2. **Score Programs**: Rate each activity program (0-20) based on your crew's interests
3. **View Results**: Get ranked itinerary recommendations with detailed scoring breakdown
4. **Explore Details**: Click any itinerary to see day-by-day schedules and available programs

## Understanding Scores

The application uses a sophisticated scoring algorithm with multiple weighted components:

- **Program Score**: Based on your activity ratings × 1.5 multiplier (typically 200-800+ points)
- **Camp Score**: Optimized scoring for camp types and counts (100-600 points)
- **Difficulty Score**: Full points if trek matches accepted difficulty levels (0 or 2000+ points)
- **Distance Score**: Preference-based distance optimization (4000-6000 points)
- **Area Score**: Regional preference bonuses if enabled (0-1000 points)
- **Peak Score**: Bonuses for desired peak climbs (0-500+ points)

Higher total scores indicate better matches for your crew's preferences.

## Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- ~100MB disk space (including virtual environment)

## File Structure

```
phil_select/
├── app.py                    # Main Flask application (85KB)
├── philmont_selection.db     # SQLite database with all trek data (2MB)
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
├── phil_select/             # Python virtual environment
├── GETTING_STARTED.md       # Detailed setup and usage guide
└── QUICK_REFERENCE.md       # Command reference and tips
```

## Technology Stack

- **Backend**: Python Flask web framework
- **Database**: SQLite with pre-loaded Philmont data
- **Frontend**: Bootstrap 5 + HTML/CSS/JavaScript
- **Data**: Comprehensive Philmont trek and program database

## Original Excel Features Replicated

✅ **Complete Data Import**: All worksheets and data tables  
✅ **Preference System**: Area, difficulty, altitude, and peak preferences  
✅ **Program Scoring**: Individual crew member activity ratings  
✅ **Complex Calculations**: Multi-factor scoring with weighted components  
✅ **Multiple Methods**: Total, Average, Median, Mode calculations  
✅ **Results Ranking**: Sorted itinerary list with detailed scores  
✅ **Itinerary Details**: Daily schedules, camps, and statistics  
✅ **Regional Coverage**: South, Central, North, Valle Vidal classification  
✅ **Difficulty Levels**: Challenging, Rugged, Strenuous, Super Strenuous  

## Development

This application was created to replace the Excel-based system while maintaining all original functionality. The scoring algorithms have been carefully replicated to ensure consistent results with the original spreadsheet.

### Key Implementation Details:
- Excel named ranges converted to database relationships
- Complex formulas implemented as Python functions  
- VBA macro logic recreated in Flask routes
- User interface adapted for web with improved usability

## Support and Contributing

- **Issues**: Report bugs or feature requests via GitHub issues
- **Questions**: Check the [Getting Started Guide](GETTING_STARTED.md) first
- **Contributing**: Fork the repository and submit pull requests

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Acknowledgments

Created to help Scout crews make informed decisions about their Philmont adventure. This tool provides recommendations only - final trek selection is handled through Philmont Scout Ranch's official reservation system.