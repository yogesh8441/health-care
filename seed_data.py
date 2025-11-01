from app import app
from models import db, User, Ward, Bed, Patient, Oxygen, ActivityLog, MedicalRecord, Medication, Inventory, Notification
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
import random

def create_seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        admin_user = User(
            name='Dr. Sarah Johnson',
            email='admin@hospital.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        
        staff_user = User(
            name='Nurse Mary Wilson',
            email='nurse@hospital.com',
            password=generate_password_hash('nurse123'),
            role='staff'
        )
        
        staff_user2 = User(
            name='Nurse John Smith',
            email='nurse2@hospital.com',
            password=generate_password_hash('nurse123'),
            role='staff'
        )
        
        db.session.add_all([admin_user, staff_user, staff_user2])
        db.session.commit()
        
        # Create wards
        wards = [
            Ward(name='General Ward A', type='general'),
            Ward(name='General Ward B', type='general'),
            Ward(name='ICU', type='icu'),
            Ward(name='Emergency', type='emergency'),
            Ward(name='Pediatric', type='pediatric'),
            Ward(name='Maternity', type='maternity')
        ]
        
        db.session.add_all(wards)
        db.session.commit()
        
        # Create patients
        patients = [
            Patient(name='Alice Brown', age=45, gender='female', admitted_on=datetime.now(timezone.utc) - timedelta(days=2), oxygen_required=True, oxygen_flow_rate=2.5),
            Patient(name='Bob Davis', age=62, gender='male', admitted_on=datetime.now(timezone.utc) - timedelta(days=1), oxygen_required=True, oxygen_flow_rate=4.0),
            Patient(name='Carol Wilson', age=38, gender='female', admitted_on=datetime.now(timezone.utc) - timedelta(hours=12)),
            Patient(name='David Miller', age=29, gender='male', admitted_on=datetime.now(timezone.utc) - timedelta(hours=6), oxygen_required=True, oxygen_flow_rate=1.5),
            Patient(name='Emma Garcia', age=55, gender='female', admitted_on=datetime.now(timezone.utc) - timedelta(hours=3)),
            Patient(name='Frank Rodriguez', age=41, gender='male', admitted_on=datetime.now(timezone.utc) - timedelta(hours=1))
        ]
        
        db.session.add_all(patients)
        db.session.commit()
        
        # Create medical records
        medical_records = [
            MedicalRecord(
                patient_id=patients[0].id,  # Alice Brown
                doctor_name='Dr. Sarah Johnson',
                diagnosis='Pneumonia with respiratory complications',
                treatment='Antibiotic therapy, oxygen support, chest physiotherapy',
                medications='Amoxicillin 500mg, Albuterol inhaler',
                notes='Patient responding well to treatment. Monitor oxygen levels closely.'
            ),
            MedicalRecord(
                patient_id=patients[1].id,  # Bob Davis
                doctor_name='Dr. Michael Chen',
                diagnosis='Chronic Obstructive Pulmonary Disease (COPD) exacerbation',
                treatment='Bronchodilators, corticosteroids, oxygen therapy',
                medications='Prednisone, Ipratropium bromide, Oxygen therapy',
                notes='Long-term COPD patient. Requires continuous monitoring.'
            ),
            MedicalRecord(
                patient_id=patients[2].id,  # Carol Wilson
                doctor_name='Dr. Emily Rodriguez',
                diagnosis='Acute gastroenteritis',
                treatment='IV fluid replacement, antiemetics, dietary management',
                medications='Ondansetron, Oral rehydration solution',
                notes='Dehydration resolved. Patient stable.'
            ),
            MedicalRecord(
                patient_id=patients[3].id,  # David Miller
                doctor_name='Dr. James Wilson',
                diagnosis='Post-operative recovery - Appendectomy',
                treatment='Pain management, wound care, gradual mobilization',
                medications='Morphine, Antibiotics prophylaxis',
                notes='Surgery successful. Recovery progressing normally.'
            )
        ]
        
        db.session.add_all(medical_records)
        db.session.commit()
        
        # Create medications
        medications = [
            # Alice Brown's medications
            Medication(
                patient_id=patients[0].id,
                medication_name='Amoxicillin',
                dosage='500mg',
                frequency='Three times daily',
                route='oral',
                prescribed_by='Dr. Sarah Johnson',
                notes='Take with food to reduce stomach upset'
            ),
            Medication(
                patient_id=patients[0].id,
                medication_name='Albuterol',
                dosage='2 puffs',
                frequency='Every 4 hours as needed',
                route='inhaler',
                prescribed_by='Dr. Sarah Johnson',
                notes='For breathing difficulties'
            ),
            # Bob Davis's medications
            Medication(
                patient_id=patients[1].id,
                medication_name='Prednisone',
                dosage='20mg',
                frequency='Once daily',
                route='oral',
                prescribed_by='Dr. Michael Chen',
                notes='Take in the morning with food'
            ),
            Medication(
                patient_id=patients[1].id,
                medication_name='Ipratropium Bromide',
                dosage='2 puffs',
                frequency='Four times daily',
                route='inhaler',
                prescribed_by='Dr. Michael Chen',
                notes='Bronchodilator for COPD management'
            ),
            # Carol Wilson's medications
            Medication(
                patient_id=patients[2].id,
                medication_name='Ondansetron',
                dosage='4mg',
                frequency='Every 8 hours as needed',
                route='oral',
                prescribed_by='Dr. Emily Rodriguez',
                notes='For nausea and vomiting'
            ),
            # David Miller's medications
            Medication(
                patient_id=patients[3].id,
                medication_name='Morphine',
                dosage='10mg',
                frequency='Every 4 hours as needed',
                route='IV',
                prescribed_by='Dr. James Wilson',
                notes='For post-operative pain management'
            ),
            Medication(
                patient_id=patients[3].id,
                medication_name='Cefazolin',
                dosage='1g',
                frequency='Every 8 hours',
                route='IV',
                prescribed_by='Dr. James Wilson',
                notes='Antibiotic prophylaxis post-surgery'
            ),
            # Emma Garcia's medications
            Medication(
                patient_id=patients[4].id,
                medication_name='Metformin',
                dosage='500mg',
                frequency='Twice daily',
                route='oral',
                prescribed_by='Dr. Lisa Park',
                notes='For diabetes management'
            )
        ]
        
        db.session.add_all(medications)
        db.session.commit()
        
        # Create beds
        bed_statuses = ['empty', 'occupied', 'reserved', 'cleaning', 'maintenance']
        beds = []
        
        for ward in wards:
            bed_count = 15 if ward.type == 'general' else 8 if ward.type == 'icu' else 10
            
            for i in range(1, bed_count + 1):
                bed_number = f"{ward.name.split()[0][0]}{i:02d}"
                status = random.choice(bed_statuses)
                
                # Assign patients to some occupied beds
                patient_id = None
                if status == 'occupied' and patients:
                    patient = random.choice(patients)
                    if not any(bed.patient_id == patient.id for bed in beds):
                        patient_id = patient.id
                    else:
                        # If patient already assigned, make bed empty
                        status = 'empty'
                
                bed = Bed(
                    ward_id=ward.id,
                    bed_number=bed_number,
                    status=status,
                    patient_id=patient_id,
                    updated_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 1440))
                )
                beds.append(bed)
        
        db.session.add_all(beds)
        db.session.commit()
        
        # Create oxygen data
        oxygen = Oxygen(
            cylinders_in_stock=45,
            cylinders_in_use=12,
            next_refill_date=datetime.now(timezone.utc) + timedelta(days=7),
            last_refill_date=datetime.now(timezone.utc) - timedelta(days=14),
            notes='Regular weekly refill scheduled'
        )
        
        db.session.add(oxygen)
        db.session.commit()
        
        # Create activity logs
        activities = [
            ActivityLog(
                user_id=staff_user.id,
                action='admit_patient',
                target='Patient Alice Brown to Bed G01',
                timestamp=datetime.now(timezone.utc) - timedelta(hours=2)
            ),
            ActivityLog(
                user_id=staff_user2.id,
                action='update_bed_status',
                target='Bed G05 from empty to cleaning',
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1)
            ),
            ActivityLog(
                user_id=admin_user.id,
                action='login',
                target='system',
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=30)
            ),
            ActivityLog(
                user_id=staff_user.id,
                action='discharge_patient',
                target='Patient from Bed I03',
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=15)
            )
        ]
        
        db.session.add_all(activities)
        db.session.commit()
        
        print("Seed data created successfully!")
        print("\nDatabase Summary:")
        print(f"   Users: {User.query.count()}")
        print(f"   Wards: {Ward.query.count()}")
        print(f"   Beds: {Bed.query.count()}")
        print(f"   Patients: {Patient.query.count()}")
        print(f"   Activities: {ActivityLog.query.count()}")
        
        print("\nLogin Credentials:")
        print("   Admin: admin@hospital.com / admin123")
        print("   Staff: nurse@hospital.com / nurse123")
        print("   Staff 2: nurse2@hospital.com / nurse123")
        
        print("\nBed Statistics:")
        print(f"   Total: {Bed.query.count()}")
        print(f"   Available: {Bed.query.filter_by(status='empty').count()}")
        print(f"   Occupied: {Bed.query.filter_by(status='occupied').count()}")
        print(f"   Reserved: {Bed.query.filter_by(status='reserved').count()}")
        print(f"   Cleaning: {Bed.query.filter_by(status='cleaning').count()}")
        print(f"   Maintenance: {Bed.query.filter_by(status='maintenance').count()}")
        
        # Create sample inventory items
        inventory_items = [
            Inventory(
                item_name='Paracetamol 500mg',
                category='medication',
                current_stock=150,
                minimum_stock=50,
                unit='tablets',
                cost_per_unit=0.25,
                supplier='PharmaCorp Ltd',
                expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
                last_restocked=datetime.now(timezone.utc) - timedelta(days=10)
            ),
            Inventory(
                item_name='Surgical Gloves',
                category='supplies',
                current_stock=25,
                minimum_stock=30,
                unit='boxes',
                cost_per_unit=12.50,
                supplier='MedSupply Inc',
                expiry_date=datetime.now(timezone.utc) + timedelta(days=730),
                last_restocked=datetime.now(timezone.utc) - timedelta(days=5)
            ),
            Inventory(
                item_name='Digital Thermometer',
                category='equipment',
                current_stock=8,
                minimum_stock=10,
                unit='pieces',
                cost_per_unit=45.00,
                supplier='MedTech Solutions',
                last_restocked=datetime.now(timezone.utc) - timedelta(days=30)
            ),
            Inventory(
                item_name='Insulin Vials',
                category='medication',
                current_stock=5,
                minimum_stock=15,
                unit='vials',
                cost_per_unit=28.75,
                supplier='PharmaCorp Ltd',
                expiry_date=datetime.now(timezone.utc) + timedelta(days=180),
                last_restocked=datetime.now(timezone.utc) - timedelta(days=20)
            ),
            Inventory(
                item_name='Bandages',
                category='supplies',
                current_stock=75,
                minimum_stock=25,
                unit='pieces',
                cost_per_unit=2.50,
                supplier='MedSupply Inc',
                expiry_date=datetime.now(timezone.utc) + timedelta(days=1095),
                last_restocked=datetime.now(timezone.utc) - timedelta(days=7)
            ),
            Inventory(
                item_name='Aspirin 100mg',
                category='medication',
                current_stock=200,
                minimum_stock=100,
                unit='tablets',
                cost_per_unit=0.15,
                supplier='Generic Pharma',
                expiry_date=datetime.now(timezone.utc) - timedelta(days=30),  # Expired item
                last_restocked=datetime.now(timezone.utc) - timedelta(days=60)
            ),
            Inventory(
                item_name='Blood Pressure Monitor',
                category='equipment',
                current_stock=3,
                minimum_stock=5,
                unit='pieces',
                cost_per_unit=125.00,
                supplier='MedTech Solutions',
                last_restocked=datetime.now(timezone.utc) - timedelta(days=45)
            ),
            Inventory(
                item_name='Syringes 10ml',
                category='supplies',
                current_stock=120,
                minimum_stock=50,
                unit='pieces',
                cost_per_unit=0.75,
                supplier='MedSupply Inc',
                expiry_date=datetime.now(timezone.utc) + timedelta(days=1460),
                last_restocked=datetime.now(timezone.utc) - timedelta(days=3)
            )
        ]
        
        for item in inventory_items:
            db.session.add(item)
        
        # Create sample notifications
        notifications = [
            Notification(
                title='Low Stock Alert',
                message='Insulin Vials are running low. Only 5 vials remaining.',
                type='warning',
                priority='high'
            ),
            Notification(
                title='Expired Medication',
                message='Aspirin 100mg has expired and needs to be removed from inventory.',
                type='error',
                priority='critical'
            ),
            Notification(
                title='System Maintenance',
                message='Scheduled system maintenance will occur tonight from 2:00 AM to 4:00 AM.',
                type='info',
                priority='normal'
            ),
            Notification(
                user_id=2,  # Staff user
                title='Shift Reminder',
                message='Your shift starts in 30 minutes. Please prepare for handover.',
                type='info',
                priority='normal'
            )
        ]
        
        for notification in notifications:
            db.session.add(notification)
        
        db.session.commit()
        
        print(f"\nInventory Items Created: {len(inventory_items)}")
        print(f"Notifications Created: {len(notifications)}")

if __name__ == '__main__':
    create_seed_data()
