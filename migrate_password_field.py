#!/usr/bin/env python3
"""
Migration script to rename 'password' column to 'password_hash' in the User table
"""

from app import app
from models import db
import sqlite3

def migrate_password_field():
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print(f"Migrating database: {db_path}")
        
        try:
            # For SQLite, we need to recreate the table
            # Get connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if password column exists
            cursor.execute("PRAGMA table_info(user)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'password' in column_names and 'password_hash' not in column_names:
                print("Found 'password' column, migrating to 'password_hash'...")
                
                # Create new table with correct schema
                cursor.execute("""
                    CREATE TABLE user_new (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(200) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        patient_id INTEGER,
                        created_at DATETIME,
                        FOREIGN KEY (patient_id) REFERENCES patient(id)
                    )
                """)
                
                # Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO user_new (id, name, email, password_hash, role, patient_id, created_at)
                    SELECT id, name, email, password, role, patient_id, created_at
                    FROM user
                """)
                
                # Drop old table
                cursor.execute("DROP TABLE user")
                
                # Rename new table
                cursor.execute("ALTER TABLE user_new RENAME TO user")
                
                # Recreate indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON user (email)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_role ON user (role)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_patient_id ON user (patient_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_created_at ON user (created_at)")
                
                conn.commit()
                print("✓ Migration completed successfully!")
                print("✓ Column 'password' renamed to 'password_hash'")
                
            elif 'password_hash' in column_names:
                print("✓ Database already has 'password_hash' column. No migration needed.")
            else:
                print("✗ Unexpected database schema. Please check manually.")
            
            conn.close()
            
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            conn.rollback()
            conn.close()
            raise

if __name__ == '__main__':
    migrate_password_field()
