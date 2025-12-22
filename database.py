# File: database.py
import sqlite3
import datetime

DB_NAME = "glocarbon.db"

def init_db():
    """
    Creates the table if it doesn't exist yet.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create a table to store Verified Projects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            name TEXT NOT NULL,
            ecosystem_type TEXT,
            credits REAL NOT NULL,
            status TEXT DEFAULT 'Listed',
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("💽 DATABASE: Connected and ready.")

def save_project(project_data, total_credits):
    """
    Saves a newly verified project into the ledger.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # For simplicity, we grab the type of the first ecosystem in the list
    primary_type = project_data.ecosystems[0].type if project_data.ecosystems else "Unknown"
    timestamp = str(datetime.datetime.now())

    cursor.execute('''
        INSERT INTO projects (owner, name, ecosystem_type, credits, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_data.project_owner, project_data.project_name, primary_type, total_credits, timestamp))
    
    conn.commit()
    conn.close()
    print(f"💾 DATABASE: Saved '{project_data.project_name}' to the ledger.")

def get_marketplace_listings():
    """
    Retrieves all projects for the marketplace feed.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, ecosystem_type, credits, status FROM projects")
    rows = cursor.fetchall()
    
    conn.close()
    return rows