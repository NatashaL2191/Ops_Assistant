#!/usr/bin/env python3
"""Generate sample indoor location data"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Create database and load schema
conn = sqlite3.connect('location_data.db')
with open('schema.sql', 'r') as f:
    conn.executescript(f.read())

# Insert zones
zones = [
    ('Z1-101', 'Lobby', 1, 'common', 'Main entrance'),
    ('Z1-102', 'Break Room', 1, 'common', 'Employee break room'),
    ('Z2-201', 'Engineering Office', 2, 'office', 'Engineering dept'),
    ('Z2-202', 'Sales Office', 2, 'office', 'Sales dept'),
    ('Z2-203', 'Meeting Room', 2, 'meeting_room', 'Meeting room'),
    ('Z2-205', 'Lab', 2, 'lab', 'Testing lab'),
    ('Z3-301', 'Executive Office', 3, 'office', 'Executive offices'),
]
conn.executemany('INSERT INTO zones VALUES (?, ?, ?, ?, ?)', zones)

# Insert entities
entities = [
    ('E001', 'Alice Johnson', 'person', 'Engineering', 1),
    ('E002', 'Bob Smith', 'person', 'Engineering', 1),
    ('E003', 'Carol Davis', 'person', 'Sales', 1),
    ('E004', 'David Brown', 'person', 'Sales', 1),
    ('E005', 'Eve Wilson', 'person', 'Executive', 1),
]
conn.executemany('INSERT INTO entities VALUES (?, ?, ?, ?, ?)', entities)

# Generate pings and events
pings = []
events = []
start = datetime.now() - timedelta(hours=48)
end = datetime.now()

for entity_id, name, _, dept, _ in entities:
    time = start
    zone = None
    enter_time = None
    
    while time < end:
        # Skip nights
        if time.hour < 7 or time.hour >= 19:
            if zone:
                events.append((entity_id, zone, 'exit', time.isoformat(), int((time - enter_time).total_seconds())))
                zone = None
            time = time + timedelta(hours=1)
            continue
        
        # Pick zone based on department and time
        if time.hour < 9:
            new_zone = 'Z1-101'  # Lobby
        elif 12 <= time.hour < 13:
            new_zone = 'Z1-102'  # Break room
        elif random.random() < 0.1:
            new_zone = 'Z2-203'  # Meeting
        else:
            # Work zones
            if dept == 'Engineering':
                new_zone = random.choice(['Z2-201', 'Z2-205'])
            elif dept == 'Sales':
                new_zone = 'Z2-202'
            else:
                new_zone = 'Z3-301'
        
        # Zone change
        if new_zone != zone:
            if zone:
                events.append((entity_id, zone, 'exit', time.isoformat(), int((time - enter_time).total_seconds())))
            events.append((entity_id, new_zone, 'enter', time.isoformat(), None))
            zone = new_zone
            enter_time = time
        
        # Generate pings
        for _ in range(random.randint(2, 4)):
            rssi = random.randint(-70, -40) if random.random() > 0.05 else random.randint(-90, -80)
            pings.append((entity_id, zone, time.isoformat(), rssi, random.uniform(1, 5)))
            time = time + timedelta(seconds=random.randint(30, 120))
        
        time = time + timedelta(minutes=random.randint(5, 15))

# Insert data
conn.executemany('INSERT INTO pings (entity_id, zone_id, timestamp, rssi, accuracy_meters) VALUES (?, ?, ?, ?, ?)', pings)
conn.executemany('INSERT INTO zone_events (entity_id, zone_id, event_type, timestamp, dwell_seconds) VALUES (?, ?, ?, ?, ?)', events)
conn.commit()

# Print summary
print(f"Created {len(zones)} zones")
print(f"Created {len(entities)} entities")
print(f"Created {len(pings)} pings")
print(f"Created {len(events)} zone events")
print(f"\nDatabase saved to: location_data.db")

conn.close()