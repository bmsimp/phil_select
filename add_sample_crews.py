#!/usr/bin/env python3

import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('philmont_selection.db')
conn.row_factory = sqlite3.Row

# Add some sample crews if they don't exist
sample_crews = [
    ("Eagle Scout Troop 123", 8),
    ("Adventure Crew 456", 10),
    ("Mountain Hikers 789", 9)
]

for crew_name, crew_size in sample_crews:
    existing = conn.execute('SELECT id FROM crews WHERE crew_name = ?', (crew_name,)).fetchone()
    if not existing:
        conn.execute('''
            INSERT INTO crews (crew_name, crew_size) 
            VALUES (?, ?)
        ''', (crew_name, crew_size))

conn.commit()
print("Sample crews added successfully!")

# Show all crews
crews = conn.execute('SELECT * FROM crews ORDER BY crew_name').fetchall()
print("\nCurrent crews:")
for crew in crews:
    print(f"- ID: {crew['id']}, Name: {crew['crew_name']}, Size: {crew['crew_size']}")

conn.close()