import sqlite3

def create_database(db_path="location_data.db"):
    conn= sqlite3.connect(db_path)
    with open('schema_sql', 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    return conn

#Zones defined as areas: Lobby, office, etc
def generate_zones(conn):
    zones = [('Z1-101', 'Lobby', 1, 'common', 'Main entrance lobby'),
        ('Z1-102', 'Reception', 1, 'office', 'Reception desk area'),]
    conn.executemany(
        zones
    )
    conn.commit()
#Entities defined as: people, places, etc
def generate_entities(conn):
    entities = [('E100', 'Alice','Person','Engineering'), ('E101', 'Product Cart', 'Object', 'IT')]
    conn.executemany(
        entities
    )
    conn.commit()

def generate_pings_and_events(conn):
    pings = []
    conn.executemany(
        pings
    )
    conn.commit()

def inject_quality_issues():
