import sqlite3
import random
from datetime import datetime, timedelta
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'location_data.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

# Load schema
with open(SCHEMA_PATH, 'r') as f:
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

conn.executemany(
    'INSERT OR IGNORE INTO zones (zone_ID, zone_name, floor, zone_type, description) VALUES (?, ?, ?, ?, ?)',
    zones
)

# Insert entities
entities = [
    ('E001', 'Alice Johnson', 'person', 'Engineering', 1),
    ('E002', 'Bob Smith', 'person', 'Engineering', 1),
    ('E003', 'Carol Davis', 'person', 'Sales', 1),
    ('E004', 'David Brown', 'person', 'Sales', 1),
    ('E005', 'Eve Wilson', 'person', 'Executive', 1),
]

conn.executemany(
    'INSERT OR IGNORE INTO entities (entity_ID, entity_name, entity_type, department, active) VALUES (?, ?, ?, ?, ?)',
    entities
)

# Generate data
pings = []
events = []

start = datetime.now() - timedelta(hours=48)
end = datetime.now()

for entity_ID, name, _, dept, _ in entities:
    time = start
    zone = None
    enter_time = None

    while time < end:
        if time.hour < 7 or time.hour >= 19:
            if zone:
                events.append((entity_ID, zone, 'exit', time.isoformat(), int((time - enter_time).total_seconds())))
                zone = None
            time += timedelta(hours=1)
            continue

        if time.hour < 9:
            new_zone = 'Z1-101'
        elif 12 <= time.hour < 13:
            new_zone = 'Z1-102'
        elif random.random() < 0.1:
            new_zone = 'Z2-203'
        else:
            if dept == 'Engineering':
                new_zone = random.choice(['Z2-201', 'Z2-205'])
            elif dept == 'Sales':
                new_zone = 'Z2-202'
            else:
                new_zone = 'Z3-301'

        if new_zone != zone:
            if zone:
                events.append((entity_ID, zone, 'exit', time.isoformat(), int((time - enter_time).total_seconds())))
            events.append((entity_ID, new_zone, 'enter', time.isoformat(), None))
            zone = new_zone
            enter_time = time

        for _ in range(random.randint(2, 4)):
            rssi = random.randint(-70, -40) if random.random() > 0.05 else random.randint(-90, -80)
            pings.append((entity_ID, zone, time.isoformat(), rssi, random.uniform(1, 5)))
            time += timedelta(seconds=random.randint(30, 120))

        time += timedelta(minutes=random.randint(5, 15))

# Insert data
conn.executemany(
    'INSERT INTO pings (entity_ID, zone_ID, timestamp, rssi, accuracy) VALUES (?, ?, ?, ?, ?)',
    pings
)

conn.executemany(
    'INSERT INTO zone_events (entity_ID, zone_ID, event_type, timestamp, dwell_seconds) VALUES (?, ?, ?, ?, ?)',
    events
)

conn.commit()

print(f"Created {len(zones)} zones")
print(f"Created {len(entities)} entities")
print(f"Created {len(pings)} pings")
print(f"Created {len(events)} zone events")
print(f"Database saved to: {DB_PATH}")

conn.close()
