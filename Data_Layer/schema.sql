CREATE TABLE IF NOT EXISTS zones(
    zone_ID TEXT PRIMARY KEY,
    zone_name TEXT NOT NULL,
    floor INTEGER NOT NULL,
    zone_type TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS entities(
    entity_ID TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT,
    department TEXT,
    active BOOLEAN DEFAULT 1

);
CREATE TABLE IF NOT EXISTS pings(
    ping_ID INTEGER PRIMARY KEY,
    entity_ID TEXT NOT NULL,
    zone_ID TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    rssi INTEGER,
    accuracy REAL NOT NULL,
    FOREIGN KEY (zone_ID) REFERENCES zones(zone_ID),
    FOREIGN KEY (entity_ID) REFERENCES entities(entity_ID)
);

CREATE TABLE IF NOT EXISTS zone_events (
    event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_ID INTEGER,
    zone_ID INTEGER,
    event_type TEXT CHECK(event_type IN ('enter', 'exit')),
    timestamp TEXT,
    dwell_seconds INTEGER,
    FOREIGN KEY (entity_ID) REFERENCES entities(entity_ID),
    FOREIGN KEY (zone_ID) REFERENCES zones(zone_ID)
);