import sqlite3

def create_database(db_path="location_data.db"):
    conn= sqlite3.connect(db_path)
    with open('schema_sql', 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    return conn

def generate_zones(conn):
    zones = [('Z1-101', 'Lobby', 1, 'common', 'Main entrance lobby'),
        ('Z1-102', 'Reception', 1, 'office', 'Reception desk area'),]
    conn.executemany()
    conn.commit()

def generate_entities(conn):
    entities = []
    conn.executemany()
    conn.commit()

def generate_pings_and_events(conn):
    pings = []
    conn.executemany()
    conn.commit()
