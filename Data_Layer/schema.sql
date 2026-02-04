CREATE TABLE zones(
    zone_ID TEXT PRIMARY KEY,
    zone_name TEXT NOT NULL,
    floor INTEGER NOT NULL,
    zone_type TEXT,
    description TEXT
);
CREATE TABLE entities(
    entity_ID TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT,
    department TEXT,
    active BOOLEAN DEFAULT 1

);

CREATE TABLE pings(
    ping_ID INTEGER PRIMARY KEY,
    entity_ID TEXT NOT NULL,
    zone_ID TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    rssi INTEGER,
    accuracy REAL NOT NULL,
    FOREIGN KEY zone_ID REFERENCES zones(zone_ID),
    FOREIGN KEY entity_ID REFERENCES entities(entity_ID)
);

CREATE TABLE derived_zones(
    event_id TEXT PRIMARY KEY,
    entity_ID TEXT NOT NULL,
    zone_ID TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    dwell_seconds INTEGER,
    FOREIGN KEY zone_ID REFERENCES zones(zone_ID),
    FOREIGN KEY entity_ID REFERENCES entities(entity_ID)

);