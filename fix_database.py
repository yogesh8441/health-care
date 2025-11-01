#!/usr/bin/env python3
"""
Script to manually create and populate the database with proper structure
"""

import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

def create_database():
    """Create database with proper structure"""
    
    # Delete existing database
    import os
    if os.path.exists('hospital.db'):
        os.remove('hospital.db')
        print("Removed existing database")
    
    # Connect to new database
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    try:
        # Create User table
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Ward table
        cursor.execute('''
            CREATE TABLE ward (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                capacity INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL
            )
        ''')
        
        # Create Bed table
        cursor.execute('''
            CREATE TABLE bed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ward_id INTEGER NOT NULL,
                bed_number VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'empty',
                patient_id INTEGER,
                notes TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ward_id) REFERENCES ward (id),
                FOREIGN KEY (patient_id) REFERENCES patient (id)
            )
        ''')
        
        # Create Patient table
        cursor.execute('''
            CREATE TABLE patient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                gender VARCHAR(10) NOT NULL,
                admitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
                discharged_on DATETIME,
                oxygen_required BOOLEAN DEFAULT 0,
                oxygen_flow_rate FLOAT
            )
        ''')
        
        # Create MedicalRecord table with status field
        cursor.execute('''
            CREATE TABLE medical_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_name VARCHAR(100) NOT NULL,
                diagnosis TEXT NOT NULL,
                treatment TEXT NOT NULL,
                medications TEXT,
                notes TEXT,
                status VARCHAR(20) DEFAULT 'active',
                discharge_date DATETIME,
                discharge_summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patient (id)
            )
        ''')
        
        # Create Medication table
        cursor.execute('''
            CREATE TABLE medication (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                medication_name VARCHAR(100) NOT NULL,
                dosage VARCHAR(50) NOT NULL,
                frequency VARCHAR(50) NOT NULL,
                route VARCHAR(20) NOT NULL,
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_date DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                prescribed_by VARCHAR(100) NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patient (id)
            )
        ''')
        
        # Create other necessary tables
        cursor.execute('''
            CREATE TABLE oxygen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cylinders_in_stock INTEGER DEFAULT 0,
                cylinders_in_use INTEGER DEFAULT 0,
                next_refill_date DATETIME,
                last_refill_date DATETIME,
                notes TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action VARCHAR(100) NOT NULL,
                target VARCHAR(200) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        # Insert sample data
        print("Creating sample data...")
        
        # Users
        admin_hash = generate_password_hash('admin123')
        staff_hash = generate_password_hash('nurse123')
        
        cursor.execute("INSERT INTO user (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      ('Admin User', 'admin@hospital.com', admin_hash, 'admin'))
        cursor.execute("INSERT INTO user (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      ('Nurse Smith', 'nurse@hospital.com', staff_hash, 'staff'))
        cursor.execute("INSERT INTO user (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                      ('Nurse Johnson', 'nurse2@hospital.com', staff_hash, 'staff'))
        
        # Wards
        wards = [
            ('General Ward A', 15, 'general'),
            ('General Ward B', 15, 'general'),
            ('ICU', 10, 'icu'),
            ('Emergency', 8, 'emergency'),
            ('Pediatric', 12, 'pediatric'),
            ('Maternity', 8, 'maternity')
        ]
        
        for ward in wards:
            cursor.execute("INSERT INTO ward (name, capacity, type) VALUES (?, ?, ?)", ward)
        
        # Beds
        bed_id = 1
        for ward_id in range(1, 7):  # 6 wards
            ward_capacity = [15, 15, 10, 8, 12, 8][ward_id - 1]
            for bed_num in range(1, ward_capacity + 1):
                bed_number = f"{'GABIEPM'[ward_id-1]}{bed_num:02d}"
                status = ['empty', 'occupied', 'cleaning', 'reserved', 'maintenance'][bed_id % 5]
                cursor.execute("INSERT INTO bed (ward_id, bed_number, status) VALUES (?, ?, ?)",
                              (ward_id, bed_number, status))
                bed_id += 1
        
        # Patients
        patients = [
            ('Alice Brown', 45, 'female', True, 2.5),
            ('Bob Davis', 62, 'male', True, 4.0),
            ('Carol Wilson', 34, 'female', False, None),
            ('David Miller', 28, 'male', False, None),
            ('Emma Garcia', 55, 'female', True, 1.5),
            ('Frank Johnson', 71, 'male', True, 3.0)
        ]
        
        for i, (name, age, gender, oxygen_req, flow_rate) in enumerate(patients, 1):
            cursor.execute('''
                INSERT INTO patient (name, age, gender, oxygen_required, oxygen_flow_rate) 
                VALUES (?, ?, ?, ?, ?)
            ''', (name, age, gender, oxygen_req, flow_rate))
            
            # Assign to occupied beds
            cursor.execute("UPDATE bed SET patient_id = ?, status = 'occupied' WHERE id = ?", (i, i))
        
        # Medical Records
        medical_records = [
            (1, 'Dr. Sarah Johnson', 'Pneumonia with respiratory complications', 'Antibiotic therapy, oxygen support', 'active'),
            (2, 'Dr. Michael Chen', 'COPD exacerbation', 'Bronchodilators, corticosteroids', 'active'),
            (3, 'Dr. Lisa Wang', 'Gastroenteritis', 'IV fluids, anti-nausea medication', 'active'),
            (4, 'Dr. Robert Kim', 'Post-operative recovery', 'Pain management, wound care', 'active'),
            (5, 'Dr. Maria Rodriguez', 'Type 2 Diabetes management', 'Insulin therapy, dietary control', 'active'),
            (6, 'Dr. James Wilson', 'Hypertension monitoring', 'Blood pressure medication', 'active')
        ]
        
        for record in medical_records:
            cursor.execute('''
                INSERT INTO medical_record (patient_id, doctor_name, diagnosis, treatment, status) 
                VALUES (?, ?, ?, ?, ?)
            ''', record)
        
        # Medications
        medications = [
            (1, 'Amoxicillin', '500mg', 'three times daily', 'oral', 'Dr. Sarah Johnson', 'active'),
            (1, 'Albuterol', '2 puffs', 'every 4 hours', 'inhaler', 'Dr. Sarah Johnson', 'active'),
            (2, 'Prednisone', '20mg', 'once daily', 'oral', 'Dr. Michael Chen', 'active'),
            (2, 'Ipratropium Bromide', '2 puffs', 'four times daily', 'inhaler', 'Dr. Michael Chen', 'active'),
            (3, 'Ondansetron', '4mg', 'every 8 hours', 'oral', 'Dr. Lisa Wang', 'active'),
            (4, 'Morphine', '10mg', 'every 4 hours as needed', 'IV', 'Dr. Robert Kim', 'active'),
            (5, 'Metformin', '500mg', 'twice daily', 'oral', 'Dr. Maria Rodriguez', 'active')
        ]
        
        for med in medications:
            cursor.execute('''
                INSERT INTO medication (patient_id, medication_name, dosage, frequency, route, prescribed_by, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', med)
        
        # Oxygen inventory
        cursor.execute('''
            INSERT INTO oxygen (cylinders_in_stock, cylinders_in_use, notes) 
            VALUES (?, ?, ?)
        ''', (25, 8, 'Regular maintenance scheduled'))
        
        conn.commit()
        print("Database created successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Created tables: {tables}")
        
        # Check MedicalRecord structure
        cursor.execute("PRAGMA table_info(medical_record)")
        columns = cursor.fetchall()
        print("MedicalRecord table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
    print("Database setup complete!")
