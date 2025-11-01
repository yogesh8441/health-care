#!/usr/bin/env python3
"""
Script to create patient accounts for testing the patient dashboard
"""

from app import app, db
from models import User, Patient
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

def create_patient_accounts():
    with app.app_context():
        # Get all patients without user accounts
        patients_without_accounts = db.session.query(Patient).outerjoin(User, Patient.id == User.patient_id).filter(User.id.is_(None)).all()
        
        print(f"Found {len(patients_without_accounts)} patients without accounts")
        
        created_accounts = 0
        
        for patient in patients_without_accounts[:5]:  # Create accounts for first 5 patients
            # Generate email based on patient name
            email = f"{patient.name.lower().replace(' ', '.')}@patient.hospital.com"
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"Email {email} already exists, skipping {patient.name}")
                continue
            
            # Create user account
            new_user = User(
                name=patient.name,
                email=email,
                password_hash=generate_password_hash('patient123'),  # Default password
                role='patient',
                patient_id=patient.id,
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(new_user)
            created_accounts += 1
            
            print(f"Created account for {patient.name} - Email: {email}, Password: patient123")
        
        if created_accounts > 0:
            db.session.commit()
            print(f"\nSuccessfully created {created_accounts} patient accounts!")
        else:
            print("No new accounts were created.")
        
        # Display all patient accounts
        print("\n=== All Patient Accounts ===")
        patient_users = User.query.filter_by(role='patient').all()
        for user in patient_users:
            patient = Patient.query.get(user.patient_id)
            print(f"Name: {user.name}, Email: {user.email}, Patient ID: {user.patient_id}")

if __name__ == '__main__':
    create_patient_accounts()
