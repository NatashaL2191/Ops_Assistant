
import sqlite3
import re
from datetime import datetime, timedelta
import os

class OpsAssistant:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, '..', 'Data_Layer', 'location_data.db')
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def ask(self, query):
        q = query.lower()
        
        # Parse time
        start, end = self.parse_time(q)
        
        # Extract names
        entities = [e for e in ['alice', 'bob', 'carol', 'david', 'eve'] if e in q]
        zones = [z for z in ['lobby', 'break', 'engineering', 'sales', 'meeting', 'lab', 'executive'] if z in q]
        
        # Generate SQL based on keywords
        sql = None
        
        # List queries
        if 'list' in q and 'zone' in q:
            sql = "SELECT zone_name, floor FROM zones ORDER BY floor"
        
        elif 'list' in q or 'show all' in q:
            sql = "SELECT entity_name, entity_type, department FROM entities"
        
        # Where is X?
        elif ('where' in q or 'find' in q) and entities:
            if start:
                sql = f"""
                    SELECT e.entity_name, z.zone_name, ze.timestamp, ze.event_type 
                    FROM zone_events ze 
                    JOIN entities e ON ze.entity_ID = e.entity_ID
                    JOIN zones z ON ze.zone_ID = z.zone_ID 
                    WHERE e.entity_name LIKE '%{entities[0]}%' 
                      AND ze.timestamp >= '{start}' AND ze.timestamp <= '{end}'
                    ORDER BY ze.timestamp
                """
            else:
                sql = f"""
                    SELECT e.entity_name, z.zone_name, ze.timestamp 
                    FROM zone_events ze 
                    JOIN entities e ON ze.entity_ID = e.entity_ID
                    JOIN zones z ON ze.zone_ID = z.zone_ID
                    WHERE e.entity_name LIKE '%{entities[0]}%' 
                      AND ze.event_type = 'enter' 
                    ORDER BY ze.timestamp DESC LIMIT 1
                """
        
        # How long / dwell time
        elif ('how long' in q or 'spent' in q) and zones:
            time_filter = f"AND ze.timestamp >= '{start}' AND ze.timestamp <= '{end}'" if start else ""
            sql = f"""
                SELECT e.entity_name, z.zone_name, SUM(ze.dwell_seconds) / 60.0 as minutes 
                FROM zone_events ze 
                JOIN entities e ON ze.entity_ID = e.entity_ID
                JOIN zones z ON ze.zone_ID = z.zone_ID
                WHERE z.zone_name LIKE '%{zones[0]}%' 
                  AND ze.event_type = 'exit' 
                  {time_filter} 
                GROUP BY e.entity_name
                ORDER BY minutes DESC
            """
        
        # Who was in zone?
        elif 'who' in q and zones:
            time_filter = f"AND ze.timestamp >= '{start}' AND ze.timestamp <= '{end}'" if start else ""
            sql = f"""
                SELECT DISTINCT e.entity_name, MIN(ze.timestamp) as first_seen 
                FROM zone_events ze 
                JOIN entities e ON ze.entity_ID = e.entity_ID
                JOIN zones z ON ze.zone_ID = z.zone_ID
                WHERE z.zone_name LIKE '%{zones[0]}%' 
                  {time_filter} 
                GROUP BY e.entity_name
            """
        
        # Movement tracking
        elif ('movement' in q or 'track' in q or 'path' in q) and entities:
            time_filter = f"AND ze.timestamp >= '{start}' AND ze.timestamp <= '{end}'" if start else ""
            sql = f"""
                SELECT z.zone_name, z.floor, ze.event_type, ze.timestamp 
                FROM zone_events ze 
                JOIN entities e ON ze.entity_ID = e.entity_ID
                JOIN zones z ON ze.zone_ID = z.zone_Id
                WHERE e.entity_name LIKE '%{entities[0]}%' 
                  {time_filter} 
                ORDER BY ze.timestamp
            """
        
        # Floor jumps
        elif 'floor jump' in q:
            sql = """
                SELECT p1.entity_ID, e.entity_name, 
                       z1.floor as floor1, z2.floor as floor2, 
                       p1.timestamp as time1, 
                       (julianday(p2.timestamp) - julianday(p1.timestamp)) * 86400 as seconds
                FROM pings p1
                JOIN pings p2 ON p2.ping_ID = (
                    SELECT ping_ID FROM pings 
                    WHERE entity_ID = p1.entity_ID AND ping_ID > p1.ping_ID 
                    LIMIT 1
                )
                JOIN zones z1 ON p1.zone_ID = z1.zone_ID
                JOIN zones z2 ON p2.zone_Id = z2.zone_ID
                JOIN entities e ON p1.entity_ID = e.entity_ID
                WHERE z1.floor != z2.floor 
                  AND (julianday(p2.timestamp) - julianday(p1.timestamp)) * 86400 < 300
                LIMIT 20
            """
        
        # Low RSSI
        elif 'low rssi' in q or 'signal' in q:
            time_filter = f"WHERE p.timestamp >= '{start}' AND p.timestamp <= '{end}'" if start else "WHERE 1=1"
            sql = f"""
                SELECT e.entity_name, z.zone_name, p.rssi, p.timestamp
                FROM pings p
                JOIN entities e ON p.entity_ID = e.entity_ID
                JOIN zones z ON p.zone_ID = z.zone_ID
                {time_filter} AND p.rssi < -75
                ORDER BY p.rssi LIMIT 20
            """
        
        # Execute query
        if not sql:
            return None, "I don't understand. Try 'where is alice?' or 'list zones'"
        
        cursor = self.conn.cursor()
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
        
        # Format answer
        if not results:
            return sql, "No data found."
        
        answer = self.format(results, q)
        return sql, answer
    
    def parse_time(self, query):
        """Parse time window from query"""
        now = datetime.now()
        
        if 'today' in query:
            start = now.replace(hour=0, minute=0, second=0)
            return start.isoformat(), now.isoformat()
        
        if 'yesterday' in query:
            day = now - timedelta(days=1)
            start = day.replace(hour=0, minute=0, second=0)
            end = day.replace(hour=23, minute=59, second=59)
            return start.isoformat(), end.isoformat()
        
        match = re.search(r'last (\d+) (minute|hour)', query)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            delta = timedelta(minutes=num) if unit == 'minute' else timedelta(hours=num)
            return (now - delta).isoformat(), now.isoformat()
        
        return None, None
    
    def format(self, results, query):
        """Format results as text"""
        
        # Lists
        if 'list' in query:
            if 'zone' in query:
                return "\n".join([f"• {r['zone_name']} (Floor {r['floor']})" for r in results])
            else:
                return "\n".join([f"• {r['entity_name']} ({r['entity_type']})" for r in results])
        
        # Location
        if 'where' in query or 'find' in query:
            if 'event_type' in results[0]:
                lines = []
                for r in results:
                    action = "→ entered" if r['event_type'] == 'enter' else "← exited"
                    lines.append(f"{r['timestamp']}: {action} {r['zone_name']}")
                return "\n".join(lines)
            else:
                r = results[0]
                return f"{r['entity_name']} is in {r['zone_name']} (last seen: {r['timestamp']})"
        
        # Dwell time
        if 'how long' in query or 'spent' in query:
            return "\n".join([f"• {r['entity_name']}: {r['minutes']:.1f} minutes" for r in results])
        
        # Who in zone
        if 'who' in query:
            return "\n".join([f"• {r['entity_name']} (first seen: {r['first_seen']})" for r in results])
        
        # Movement
        if 'movement' in query or 'track' in query:
            lines = []
            for r in results:
                action = "→" if r['event_type'] == 'enter' else "←"
                lines.append(f"{action} {r['timestamp']}: {r['zone_name']} (Floor {r['floor']})")
            return "\n".join(lines)
        
        # Floor jumps
        if 'floor' in query:
            return "\n".join([f"• {r['entity_name']}: Floor {r['floor1']}→{r['floor2']} in {r['seconds']:.0f}s" for r in results])
        
        # RSSI
        if 'rssi' in query or 'signal' in query:
            return "\n".join([f"• {r['entity_name']} in {r['zone_name']}: {r['rssi']} dBm" for r in results])
        
        return f"Found {len(results)} results"
    
    def close(self):
        self.conn.close()


# CLI
def main():
    print("="*60)
    print("OPS ASSISTANT")
    print("="*60)
    print("Examples: 'where is alice?', 'list zones', 'quit'\n")
    
    assistant = OpsAssistant()
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        sql, answer = assistant.ask(query)
        
        print("\n" + "-"*60)
        if sql:
            print(f"SQL: {sql[:200]}{'...' if len(sql) > 200 else ''}\n")
        print(answer)
        print("-"*60 + "\n")
    
    assistant.close()
    print("Goodbye!")


if __name__ == '__main__':
    main()