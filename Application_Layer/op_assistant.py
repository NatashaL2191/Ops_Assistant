import sqlite3
class OpAssistant:
    def __init__(self, db_path= 'location_data.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        pass

    def parse_time_window():
        pass
    def classify_query():
        pass
    def generate_sql():
        pass
    def format_answer():
        pass
    def process_query(self, user_query):
        sql = self.generate_sql(user_query)
        results = self.execute_query(sql)
        answer = self.format_answer(results)
    def close(self):
        self.conn.close()