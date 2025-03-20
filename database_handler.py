import sqlite3
import os

# Ensure database directory exists
if not os.path.exists('./Database'):
    os.makedirs('./Database')

# Connect to SQLite database
connections_db = sqlite3.connect('./Database/plate_detected.db', check_same_thread=False)
cursor = connections_db.cursor()

# Create table for number plates if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS number_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate BLOB NOT NULL,
    entry_time TEXT NOT NULL,
    exit_time TEXT
);
''')
connections_db.commit()

def insert_plate(plate_blob, entry_time):
    """Insert a detected plate into the database."""
    cursor.execute('INSERT INTO number_plates (plate, entry_time, exit_time) VALUES (?, ?, ?)', 
                   (plate_blob, entry_time, None))
    connections_db.commit()

def update_exit_time(entry_time, exit_time):
    """Update the exit time when a plate leaves the frame."""
    cursor.execute('UPDATE number_plates SET exit_time = ? WHERE entry_time = ?', (exit_time, entry_time))
    connections_db.commit()

def get_all_plates():
    """Retrieve all plates from the database."""
    cursor.execute('SELECT id, plate, entry_time, exit_time FROM number_plates')
    return cursor.fetchall()
