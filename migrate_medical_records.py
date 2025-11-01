#!/usr/bin/env python3
"""
Migration script to add missing fields to MedicalRecord table
"""

import sqlite3
from datetime import datetime, timezone

def migrate_medical_records():
    """Add status, discharge_date, and discharge_summary fields to medical_record table"""
    
    # Connect to the database
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(medical_record)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add status column if it doesn't exist
        if 'status' not in columns:
            print("Adding 'status' column to medical_record table...")
            cursor.execute("ALTER TABLE medical_record ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            print("Added 'status' column")
        else:
            print("'status' column already exists")
        
        # Add discharge_date column if it doesn't exist
        if 'discharge_date' not in columns:
            print("Adding 'discharge_date' column to medical_record table...")
            cursor.execute("ALTER TABLE medical_record ADD COLUMN discharge_date DATETIME")
            print("Added 'discharge_date' column")
        else:
            print("'discharge_date' column already exists")
        
        # Add discharge_summary column if it doesn't exist
        if 'discharge_summary' not in columns:
            print("Adding 'discharge_summary' column to medical_record table...")
            cursor.execute("ALTER TABLE medical_record ADD COLUMN discharge_summary TEXT")
            print("Added 'discharge_summary' column")
        else:
            print("'discharge_summary' column already exists")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting MedicalRecord table migration...")
    migrate_medical_records()
    print("Migration finished!")
