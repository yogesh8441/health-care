from flask import Flask
from models import db, User, Ward, Bed, Patient, Oxygen, ActivityLog, MedicalRecord, Medication, Inventory, Shift, Notification, Appointment, EmergencyAlert

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created successfully!")
    
    # Check what tables were created
    import sqlite3
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [table[0] for table in cursor.fetchall()]
    print("Created tables:", tables)
    
    # Check MedicalRecord table structure
    if 'medical_record' in tables:
        cursor.execute("PRAGMA table_info(medical_record)")
        columns = cursor.fetchall()
        print("MedicalRecord table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()
