import sqlite3
from datetime import datetime
import os
import json

class DatabaseManager:
    def __init__(self, config_path='../config.json'):
        self.config = self.load_config(config_path)
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.config['database']['file']))
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def get_all_vehicles(self):
        try:
            self.cursor.execute("SELECT * FROM vehicles")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving all vehicles: {e}")
            return []

    def load_config(self, config_path):
        with open(config_path, 'r') as config_file:
            return json.load(config_file)

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_tables(self):
        try:
            # Check if tables exist before creating them
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='vehicles' OR name='entry_exit')")
            existing_tables = self.cursor.fetchall()
            existing_table_names = [table[0] for table in existing_tables]

            tables_created = []

            if 'vehicles' not in existing_table_names:
                self.cursor.execute('''
                    CREATE TABLE vehicles (
                        vehicle_number TEXT PRIMARY KEY,
                        vehicle_type TEXT,
                        vehicle_color TEXT,
                        owner_name TEXT,
                        owner_aadhar TEXT,
                        affiliation TEXT,
                        image_path TEXT
                    )
                ''')
                tables_created.append('vehicles')

            if 'entry_exit' not in existing_table_names:
                self.cursor.execute('''
                    CREATE TABLE entry_exit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vehicle_number TEXT,
                        in_time TIMESTAMP,
                        out_time TIMESTAMP,
                        FOREIGN KEY (vehicle_number) REFERENCES vehicles (vehicle_number)
                    )
                ''')
                tables_created.append('entry_exit')

            self.conn.commit()

            if tables_created:
                print(f"Tables created: {', '.join(tables_created)}")
            else:
                print("All required tables already exist")

        except sqlite3.Error as e:
            print(f"Error handling tables: {e}")

    def get_vehicle(self, vehicle_number):
        try:
            self.cursor.execute("SELECT * FROM vehicles WHERE vehicle_number = ?", (vehicle_number,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving vehicle: {e}")
            return None

    def add_vehicle(self, vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, image_path):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO vehicles 
                (vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, image_path))
            self.conn.commit()
            print(f"Vehicle {vehicle_number} added/updated successfully")
            return True
        except sqlite3.Error as e:
            print(f"Error adding/updating vehicle: {e}")
            return False

    def edit_vehicle(self, vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, image_path):
        try:
            self.cursor.execute('''
                UPDATE vehicles 
                SET vehicle_type = ?, vehicle_color = ?, owner_name = ?, 
                    owner_aadhar = ?, affiliation = ?, image_path = ?
                WHERE vehicle_number = ?
            ''', (vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, image_path, vehicle_number))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Vehicle {vehicle_number} updated successfully")
                return True
            else:
                print(f"Vehicle {vehicle_number} not found")
                return False
        except sqlite3.Error as e:
            print(f"Error updating vehicle: {e}")
            return False

    def delete_vehicle(self, vehicle_number):
        try:
            # First, delete related entry_exit records
            self.cursor.execute("DELETE FROM entry_exit WHERE vehicle_number = ?", (vehicle_number,))
            
            # Then delete the vehicle
            self.cursor.execute("DELETE FROM vehicles WHERE vehicle_number = ?", (vehicle_number,))
            
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Vehicle {vehicle_number} and its records deleted successfully")
                return True
            else:
                print(f"Vehicle {vehicle_number} not found")
                return False
        except sqlite3.Error as e:
            print(f"Error deleting vehicle: {e}")
            return False

    def log_entry_exit(self, vehicle_number):
        try:
            current_time = datetime.now()
            
            # Check if there's an open entry (no exit time)
            self.cursor.execute("""
                SELECT id FROM entry_exit 
                WHERE vehicle_number = ? AND out_time IS NULL 
                ORDER BY in_time DESC LIMIT 1
            """, (vehicle_number,))
            open_entry = self.cursor.fetchone()

            if open_entry:
                # Vehicle is exiting
                self.cursor.execute("""
                    UPDATE entry_exit SET out_time = ? WHERE id = ?
                """, (current_time, open_entry[0]))
                print(f"Exit logged for vehicle {vehicle_number}")
            else:
                # Vehicle is entering
                self.cursor.execute("""
                    INSERT INTO entry_exit (vehicle_number, in_time) VALUES (?, ?)
                """, (vehicle_number, current_time))
                print(f"Entry logged for vehicle {vehicle_number}")

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error logging entry/exit: {e}")
            return False

    def get_entry_exit_logs(self, vehicle_number=None, start_date=None, end_date=None):
        try:
            query = "SELECT * FROM entry_exit"
            params = []
            conditions = []

            if vehicle_number:
                conditions.append("vehicle_number = ?")
                params.append(vehicle_number)
            if start_date:
                conditions.append("in_time >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("in_time <= ?")
                params.append(end_date)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY in_time DESC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving entry/exit logs: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed")

def get_database_manager(config_path='../config.json'):
    return DatabaseManager(config_path)