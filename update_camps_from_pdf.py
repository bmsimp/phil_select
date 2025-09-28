#!/usr/bin/env python3
"""
Update itinerary camps based on PDF data from pages 17-18
This script corrects the missing Days 2 and 3 data and ensures all 10 camps are listed for each itinerary
"""

import sqlite3
import sys

# Itinerary camp data extracted from PDF pages 17-18
ITINERARY_CAMPS = {
    '12-1': [
        'Toothache Springs', 'Crater Lake', 'Lower Bonito', 'Buck Creek', 
        'Apache Springs', 'Apache Springs', 'Fish Camp', 'Abreu', 'Urraca', 'Stockade Ridge'
    ],
    '12-2': [
        'Trail Canyon', 'Dean Cow', 'New Dean', 'Bluestem', 'Pueblano', 
        'Ewells Park', 'Ewells Park', 'Touch-Me-Not Creek', 'Head of Dean', 'Mistletoe'
    ],
    '12-3': [
        'Trail Canyon', 'Elkhorn', 'Head of Dean', 'Rich Cabins', 'Middle Ponil', 
        'Ring Place', 'Whiteman Vega', 'Dan Beard', 'Cottonwood', 'House Canyon'
    ],
    '12-4': [
        'Flume Canyon', 'Pueblano Ruins', 'Baldy Town', 'Baldy Town', 'Maxwell', 
        'Head of Dean', 'Ponil', 'Metcalf Station', 'Cottonwood', 'House Canyon'
    ],
    '12-5': [
        'Abreu', 'Carson Meadows', 'Fish Camp', 'Lost Cabins', 'Crooked Creek', 
        'Clear Creek', 'Divide', 'Phillips Junction', 'Lookout Meadow', 'Bear Caves'
    ],
    '12-6': [
        'Herradura', 'Miners Park', 'Ponderosa Park', 'Cimarroncito', 'Cimarroncita', 
        'Cimarroncita', 'Upper Dean Cow', 'Ewells Park', 'Ewells Park', 'Miranda'
    ],
    '12-7': [
        'Sioux', 'Rich Cabins', 'Beatty Lakes', 'Whiteman Vega', 'Ring Place', 
        'Iris Park', 'Greenwood Canyon', 'Copper Park', 'Copper Park', 'Miranda'
    ],
    '12-8': [
        'House Canyon', 'Indian Writings', 'Horse Canyon', 'Dean Skyline', 'Pueblano', 
        'Placer', 'Placer', 'Head of Dean', 'New Dean', 'Cimarron River'
    ],
    '12-9': [
        'Dean Cow', 'New Dean', 'Ponil', 'Flume Canyon', 'Miranda', 
        'Santa Claus', 'Cimarroncita', 'Cimarroncito', 'Hunting Lodge', 'Shaefers Pass'
    ],
    '12-10': [
        'Cimarron River', 'Black Jacks', 'Elkhorn', 'Ponil', 'Metcalf Station', 
        'Dan Beard', 'Pueblano Ruins', 'Ewells Park', 'Ewells Park', 'Miranda'
    ],
    '12-11': [
        'Abreu', 'Crater Lake', 'Beaubien', 'Beaubien', 'Bear Creek', 
        'Crooked Creek', 'Divide', 'Hunting Lodge', 'Clarks Fork', 'Tooth Ridge'
    ],
    '12-12': [
        'Rimrock Park', 'Carson Meadows', 'Fish Camp', 'Crooked Creek', 'Comanche Peak', 
        'Beaubien', 'Beaubien', 'Bear Caves', 'Miners Park', 'Shaefers Pass'
    ],
    '12-13': [
        'Toothache Springs', 'Magpie', 'Miners Park', 'Black Mountain', 'Divide', 
        'Lamberts Mine', 'Cimarroncito', 'Cimarroncito', 'Clarks Fork', 'Tooth Ridge'
    ],
    '12-14': [
        'Sioux', 'Dan Beard', 'Ring Place', 'Whiteman Vega', 'Iris Park', 
        'Rich Cabins', 'Dean Skyline', 'Dean Cow', 'Harlan', 'Hunting Lodge'
    ],
    '12-15': [
        'Lovers Leap', 'Miners Park', 'Beaubien', 'Beaubien', 'Comanche Creek', 
        'Comanche Peak', 'Sawmill', 'Cyphers Mine', 'Cimarroncito', 'Shaefers Pass'
    ],
    '12-16': [
        'Carson Meadows', 'Lower Bonito', 'Fish Camp', 'Apache Springs', 'Comanche Creek', 
        'Red Hills', 'Beaubien', 'Beaubien', 'Miners Park', 'Tooth Ridge'
    ],
    '12-17': [
        'Minnette Meadows', 'Cimarroncito', 'Cyphers Mine', 'Mount Phillips', 'Wild Horse', 
        'Apache Springs', 'Phillips Junction', 'Crater Lake', 'Miners Park', 'Tooth Ridge'
    ],
    '12-18': [
        'Deer Lake', 'Minnette Meadows', 'Mistletoe', 'Head of Dean', 'Baldy Town', 
        'Baldy Town', 'Pueblano', 'Elkhorn', 'Ponil', 'Coyote Howl'
    ],
    '12-19': [
        'Magpie', 'Urraca', 'Lower Bonito', 'Apache Springs', 'Wild Horse', 
        'Mount Phillips', 'Whistle Punk', 'Sawmill', 'Clarks Fork', 'Tooth Ridge'
    ],
    '12-20': [
        'Horse Canyon', 'Dan Beard', 'Ring Place', 'Whiteman Vega', 'Iris Park', 
        'Copper Park', 'Copper Park', 'Miranda', 'Baldy Skyline', 'Ponil'
    ],
    '12-21': [
        'Magpie', 'Abreu', 'Miners Park', 'Black Mountain', 'Crooked Creek', 
        'Mount Phillips', 'Cyphers Mine', 'Cimarroncito', 'Cimarroncito', 'Ponderosa Park'
    ],
    '12-22': [
        'Deer Lake', 'Harlan', 'Dean Cow', 'Ponil', 'Pueblano', 
        'Azurite', 'Azurite', 'Miranda', 'Head of Dean', 'Mistletoe'
    ],
    '12-23': [
        'Herradura', 'Miners Park', 'Clarks Fork', 'Vaca', 'Cimarroncita', 
        'Head of Dean', 'Black Horse Creek', 'Black Horse Creek', 'Pueblano', 'Trail Canyon'
    ],
    '12-24': [
        'Bluestem', 'Pueblano', 'Placer', 'Placer', 'Mistletoe', 
        'Cimarron River', 'Sawmill', 'Cyphers Mine', 'Cimarroncito', 'Shaefers Pass'
    ]
}

def update_camps_from_pdf():
    """Update the itinerary_camps table with correct data from the PDF"""
    
    conn = sqlite3.connect('philmont_selection.db')
    cursor = conn.cursor()
    
    # Get all unique camp names from the PDF data
    all_camp_names = set()
    for camps in ITINERARY_CAMPS.values():
        all_camp_names.update(camps)
    
    print(f"Found {len(all_camp_names)} unique camp names in PDF data")
    
    # Check which camps might be missing from our camps table
    missing_camps = []
    for camp_name in sorted(all_camp_names):
        cursor.execute('SELECT id FROM camps WHERE name = ?', (camp_name,))
        if not cursor.fetchone():
            missing_camps.append(camp_name)
    
    if missing_camps:
        print(f"Missing camps that need to be added: {missing_camps}")
        # Add missing camps with basic information
        for camp_name in missing_camps:
            cursor.execute('''
                INSERT OR IGNORE INTO camps (name, country, is_staffed, is_trail_camp) 
                VALUES (?, 'Unknown', FALSE, FALSE)
            ''', (camp_name,))
        print(f"Added {len(missing_camps)} missing camps")
    
    # Update itinerary camps
    updated_itineraries = 0
    total_camps_added = 0
    
    for itinerary_code, camps in ITINERARY_CAMPS.items():
        # Get itinerary ID
        cursor.execute('SELECT id FROM itineraries WHERE itinerary_code = ?', (itinerary_code,))
        result = cursor.fetchone()
        if not result:
            print(f"Warning: Itinerary {itinerary_code} not found in database")
            continue
        
        itinerary_id = result[0]
        
        # Clear existing camps for this itinerary
        cursor.execute('DELETE FROM itinerary_camps WHERE itinerary_id = ?', (itinerary_id,))
        
        # Add all camps for days 2-11
        camps_added = 0
        for day_num, camp_name in enumerate(camps, start=2):
            cursor.execute('SELECT id FROM camps WHERE name = ?', (camp_name,))
            camp_result = cursor.fetchone()
            if camp_result:
                camp_id = camp_result[0]
                cursor.execute('''
                    INSERT INTO itinerary_camps 
                    (itinerary_id, day_number, camp_id, is_layover, food_pickup, year)
                    VALUES (?, ?, ?, FALSE, FALSE, 2025)
                ''', (itinerary_id, day_num, camp_id))
                camps_added += 1
            else:
                print(f"Warning: Camp '{camp_name}' not found for itinerary {itinerary_code}, day {day_num}")
        
        print(f"Updated itinerary {itinerary_code}: added {camps_added} camps")
        updated_itineraries += 1
        total_camps_added += camps_added
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\nSummary:")
    print(f"- Updated {updated_itineraries} itineraries")
    print(f"- Added {total_camps_added} total camp assignments")
    print(f"- Each itinerary should now have 10 camps (days 2-11)")

def verify_update():
    """Verify that all itineraries now have 10 camps"""
    conn = sqlite3.connect('philmont_selection.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT i.itinerary_code, COUNT(ic.id) as camp_count
        FROM itineraries i
        LEFT JOIN itinerary_camps ic ON i.id = ic.itinerary_id
        WHERE i.itinerary_code LIKE '12-%'
        GROUP BY i.id, i.itinerary_code
        ORDER BY i.itinerary_code
    ''')
    
    results = cursor.fetchall()
    print("\nVerification - Camp counts per itinerary:")
    
    issues = []
    for itinerary_code, camp_count in results:
        if camp_count != 10:
            issues.append(f"{itinerary_code}: {camp_count} camps (should be 10)")
        else:
            print(f"{itinerary_code}: ✓ {camp_count} camps")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("\n✅ All itineraries have correct number of camps (10 each)")
    
    conn.close()

if __name__ == '__main__':
    print("Updating itinerary camps from PDF data...")
    update_camps_from_pdf()
    print("\nVerifying update...")
    verify_update()