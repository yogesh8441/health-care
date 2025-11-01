#!/usr/bin/env python3
"""
Database migration script to add new patient fields and patient_id to User model
"""

import sqlite3
from datetime import datetime

def migrate_database():
    # Connect to the database
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        # Add new columns to Patient table
        patient_columns = [
            ('phone', 'VARCHAR(20)'),
            ('address', 'TEXT'),
            ('emergency_contact', 'VARCHAR(100)'),
            ('blood_group', 'VARCHAR(5)'),
            ('allergies', 'TEXT'),
            ('medical_history', 'TEXT')
        ]
        
        for column_name, column_type in patient_columns:
            try:
                cursor.execute(f'ALTER TABLE patient ADD COLUMN {column_name} {column_type}')
                print(f"Added column '{column_name}' to patient table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column '{column_name}' already exists in patient table")
                else:
                    print(f"Error adding column '{column_name}': {e}")
        
        # Add patient_id column to User table
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN patient_id INTEGER')
            print("Added column 'patient_id' to user table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column 'patient_id' already exists in user table")
            else:
                print(f"Error adding column 'patient_id': {e}")
        
        # Create foreign key constraint (SQLite doesn't support adding foreign keys to existing tables)
        # This would need to be handled by recreating the table, but for now we'll just note it
        print("Note: Foreign key constraint for patient_id should be added manually if needed")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
        # Display current table schemas
        print("\n=== Current Patient Table Schema ===")
        cursor.execute("PRAGMA table_info(patient)")
        patient_columns = cursor.fetchall()
        for column in patient_columns:
            print(f"  {column[1]} ({column[2]})")
        
        print("\n=== Current User Table Schema ===")
        cursor.execute("PRAGMA table_info(user)")
        user_columns = cursor.fetchall()
        for column in user_columns:
            print(f"  {column[1]} ({column[2]})")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
