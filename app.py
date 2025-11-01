from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL on Vercel
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')
else:
    # Use SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models and initialize db
from models import db, User, Ward, Bed, Patient, Oxygen, ActivityLog, MedicalRecord, Medication, Inventory, Shift, Notification, Appointment, EmergencyAlert
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    # Create helpful indexes (SQLite: IF NOT EXISTS)
    try:
        statements = [
            # User
            "CREATE INDEX IF NOT EXISTS idx_user_email ON user (email)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON user (role)",
            "CREATE INDEX IF NOT EXISTS idx_user_patient_id ON user (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_created_at ON user (created_at)",
            # Bed
            "CREATE INDEX IF NOT EXISTS idx_bed_ward_id ON bed (ward_id)",
            "CREATE INDEX IF NOT EXISTS idx_bed_status ON bed (status)",
            "CREATE INDEX IF NOT EXISTS idx_bed_patient_id ON bed (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_bed_updated_at ON bed (updated_at)",
            # Patient
            "CREATE INDEX IF NOT EXISTS idx_patient_admitted_on ON patient (admitted_on)",
            "CREATE INDEX IF NOT EXISTS idx_patient_discharged_on ON patient (discharged_on)",
            "CREATE INDEX IF NOT EXISTS idx_patient_oxygen_required ON patient (oxygen_required)",
            # ActivityLog
            "CREATE INDEX IF NOT EXISTS idx_activitylog_user_id ON activity_log (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_activitylog_timestamp ON activity_log (timestamp)",
            # MedicalRecord
            "CREATE INDEX IF NOT EXISTS idx_medicalrecord_patient_id ON medical_record (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_medicalrecord_status ON medical_record (status)",
            "CREATE INDEX IF NOT EXISTS idx_medicalrecord_created_at ON medical_record (created_at)",
            # Medication
            "CREATE INDEX IF NOT EXISTS idx_medication_patient_id ON medication (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_medication_status ON medication (status)",
            "CREATE INDEX IF NOT EXISTS idx_medication_created_at ON medication (created_at)",
            # Shift
            "CREATE INDEX IF NOT EXISTS idx_shift_user_id ON shift (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_shift_start_time ON shift (start_time)",
            "CREATE INDEX IF NOT EXISTS idx_shift_status ON shift (status)",
            # Notification
            "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification (is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification (created_at)",
            # Appointment
            "CREATE INDEX IF NOT EXISTS idx_appointment_patient_id ON appointment (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_appointment_scheduled_time ON appointment (scheduled_time)",
            "CREATE INDEX IF NOT EXISTS idx_appointment_status ON appointment (status)"
        ]
        for stmt in statements:
            db.session.execute(stmt)
        db.session.commit()
    except Exception:
        db.session.rollback()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff_dashboard'))
        else:  # patient role
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                action='login',
                target='system',
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(log)
            db.session.commit()
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:  # patient role
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='logout',
            target='system',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
    
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get dashboard statistics
    total_beds = Bed.query.count()
    occupied_beds = Bed.query.filter_by(status='occupied').count()
    available_beds = Bed.query.filter_by(status='empty').count()
    reserved_beds = Bed.query.filter_by(status='reserved').count()
    maintenance_beds = Bed.query.filter_by(status='maintenance').count()
    
    total_patients = Patient.query.filter_by(discharged_on=None).count()
    
    oxygen = Oxygen.query.first()
    oxygen_stock = oxygen.cylinders_in_stock if oxygen else 0
    
    # Get bed data for table
    beds = db.session.query(Bed, Ward, Patient).join(Ward).outerjoin(Patient).all()
    
    # Get recent activities
    recent_activities = ActivityLog.query.join(User).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_beds=total_beds,
                         occupied_beds=occupied_beds,
                         available_beds=available_beds,
                         reserved_beds=reserved_beds,
                         maintenance_beds=maintenance_beds,
                         total_patients=total_patients,
                         oxygen_stock=oxygen_stock,
                         beds=beds,
                         recent_activities=recent_activities)

@app.route('/staff/dashboard')
def staff_dashboard():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get beds assigned to this staff member (for now, show all)
    beds = db.session.query(Bed, Ward, Patient).join(Ward).outerjoin(Patient).all()
    
    # Get oxygen info
    oxygen = Oxygen.query.first()
    
    return render_template('staff/dashboard.html', beds=beds, oxygen=oxygen)

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect(url_for('login'))
    
    # Get current user and their patient record
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        flash('No patient record found for your account', 'error')
        return redirect(url_for('login'))
    
    patient = Patient.query.get(user.patient_id)
    if not patient:
        flash('Patient record not found', 'error')
        return redirect(url_for('login'))
    
    # Get current bed assignment
    current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
    ward_info = None
    if current_bed:
        ward_info = {
            'name': current_bed.ward.name,
            'type': current_bed.ward.type,
            'bed_number': current_bed.bed_number
        }
    
    # Get medical records
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).all()
    
    # Get current medications
    current_medications = Medication.query.filter_by(patient_id=patient.id, status='active').order_by(Medication.created_at.desc()).all()
    
    # Get completed medications (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_medications = Medication.query.filter(
        Medication.patient_id == patient.id,
        Medication.status.in_(['completed', 'discontinued']),
        Medication.updated_at >= thirty_days_ago
    ).order_by(Medication.updated_at.desc()).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.scheduled_time >= datetime.now(timezone.utc),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.scheduled_time).all()
    
    # Get recent appointments (last 30 days)
    recent_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.scheduled_time >= thirty_days_ago,
        Appointment.status.in_(['completed', 'cancelled'])
    ).order_by(Appointment.scheduled_time.desc()).all()
    
    # Calculate days admitted
    days_admitted = 0
    if patient.admitted_on and not patient.discharged_on:
        # Ensure both datetimes are timezone-aware
        now_utc = datetime.now(timezone.utc)
        admitted_on_utc = patient.admitted_on.replace(tzinfo=timezone.utc) if patient.admitted_on.tzinfo is None else patient.admitted_on
        days_admitted = (now_utc - admitted_on_utc).days
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         ward_info=ward_info,
                         medical_records=medical_records,
                         current_medications=current_medications,
                         recent_medications=recent_medications,
                         upcoming_appointments=upcoming_appointments,
                         recent_appointments=recent_appointments,
                         days_admitted=days_admitted)

@app.route('/patient/medical-records')
def patient_medical_records():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        flash('No patient record found', 'error')
        return redirect(url_for('login'))
    
    patient = Patient.query.get(user.patient_id)
    medical_records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).all()
    
    return render_template('patient/medical_records.html', patient=patient, medical_records=medical_records)

@app.route('/patient/medications')
def patient_medications():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        flash('No patient record found', 'error')
        return redirect(url_for('login'))
    
    patient = Patient.query.get(user.patient_id)
    
    # Get all medications
    current_medications = Medication.query.filter_by(patient_id=patient.id, status='active').order_by(Medication.created_at.desc()).all()
    completed_medications = Medication.query.filter_by(patient_id=patient.id, status='completed').order_by(Medication.updated_at.desc()).all()
    discontinued_medications = Medication.query.filter_by(patient_id=patient.id, status='discontinued').order_by(Medication.updated_at.desc()).all()
    
    return render_template('patient/medications.html', 
                         patient=patient,
                         current_medications=current_medications,
                         completed_medications=completed_medications,
                         discontinued_medications=discontinued_medications)

@app.route('/patient/appointments')
def patient_appointments():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        flash('No patient record found', 'error')
        return redirect(url_for('login'))
    
    patient = Patient.query.get(user.patient_id)
    
    # Get appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.scheduled_time >= datetime.now(timezone.utc),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.scheduled_time).all()
    
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.scheduled_time < datetime.now(timezone.utc)
    ).order_by(Appointment.scheduled_time.desc()).all()
    
    return render_template('patient/appointments.html',
                         patient=patient,
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments)

@app.route('/patient/profile')
def patient_profile():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        flash('No patient record found', 'error')
        return redirect(url_for('login'))
    
    patient = Patient.query.get(user.patient_id)
    
    # Get current bed assignment
    current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
    ward_info = None
    if current_bed:
        ward_info = {
            'name': current_bed.ward.name,
            'type': current_bed.ward.type,
            'bed_number': current_bed.bed_number
        }
    
    # Calculate days admitted and account age
    days_admitted = 0
    if patient.admitted_on and not patient.discharged_on:
        # Ensure both datetimes are timezone-aware
        now_utc = datetime.now(timezone.utc)
        admitted_on_utc = patient.admitted_on.replace(tzinfo=timezone.utc) if patient.admitted_on.tzinfo is None else patient.admitted_on
        days_admitted = (now_utc - admitted_on_utc).days
    
    # Handle timezone for user.created_at
    now_utc = datetime.now(timezone.utc)
    created_at_utc = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
    account_age_days = (now_utc - created_at_utc).days
    
    return render_template('patient/profile.html', 
                         patient=patient, 
                         ward_info=ward_info, 
                         user=user,
                         days_admitted=days_admitted,
                         account_age_days=account_age_days)

# API Routes for Patient Dashboard
@app.route('/api/patient/dashboard-stats')
def patient_dashboard_stats():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user.patient_id:
        return jsonify({'error': 'No patient record found'}), 404
    
    patient = Patient.query.get(user.patient_id)
    
    # Get counts
    current_medications_count = Medication.query.filter_by(patient_id=patient.id, status='active').count()
    medical_records_count = MedicalRecord.query.filter_by(patient_id=patient.id).count()
    upcoming_appointments_count = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.scheduled_time >= datetime.now(timezone.utc),
        Appointment.status == 'scheduled'
    ).count()
    
    # Calculate days admitted
    days_admitted = 0
    if patient.admitted_on and not patient.discharged_on:
        # Ensure both datetimes are timezone-aware
        now_utc = datetime.now(timezone.utc)
        admitted_on_utc = patient.admitted_on.replace(tzinfo=timezone.utc) if patient.admitted_on.tzinfo is None else patient.admitted_on
        days_admitted = (now_utc - admitted_on_utc).days
    
    return jsonify({
        'current_medications': current_medications_count,
        'medical_records': medical_records_count,
        'upcoming_appointments': upcoming_appointments_count,
        'days_admitted': days_admitted
    })

# Admin route to create patient accounts
@app.route('/admin/create-patient-account', methods=['POST'])
def create_patient_account():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        email = data.get('email')
        password = data.get('password', 'patient123')  # Default password
        
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if patient already has an account
        existing_user = User.query.filter_by(patient_id=patient_id).first()
        if existing_user:
            return jsonify({'error': 'Patient already has an account'}), 400
        
        # Check if email is already used
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'Email already in use'}), 400
        
        # Create user account
        new_user = User(
            name=patient.name,
            email=email,
            password=generate_password_hash(password),
            role='patient',
            patient_id=patient_id,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='create_patient_account',
            target=f'Created account for patient {patient.name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Account created for {patient.name}',
            'email': email,
            'temporary_password': password
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/staff/ward-status')
def staff_ward_status():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get ward statistics
    wards = Ward.query.all()
    ward_stats = []
    
    for ward in wards:
        total_beds = Bed.query.filter_by(ward_id=ward.id).count()
        occupied_beds = Bed.query.filter_by(ward_id=ward.id, status='occupied').count()
        available_beds = Bed.query.filter_by(ward_id=ward.id, status='empty').count()
        cleaning_beds = Bed.query.filter_by(ward_id=ward.id, status='cleaning').count()
        maintenance_beds = Bed.query.filter_by(ward_id=ward.id, status='maintenance').count()
        reserved_beds = Bed.query.filter_by(ward_id=ward.id, status='reserved').count()
        
        occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
        
        ward_stats.append({
            'ward': ward,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'cleaning_beds': cleaning_beds,
            'maintenance_beds': maintenance_beds,
            'reserved_beds': reserved_beds,
            'occupancy_rate': occupancy_rate
        })
    
    # Get recent bed changes in the last 24 hours
    from datetime import timedelta
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_changes = db.session.query(Bed, Ward).join(Ward).filter(
        Bed.updated_at >= cutoff_time
    ).order_by(Bed.updated_at.desc()).limit(20).all()
    
    return render_template('staff/ward_status.html', ward_stats=ward_stats, recent_changes=recent_changes)

@app.route('/staff/oxygen-status')
def staff_oxygen_status():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get oxygen information
    oxygen = Oxygen.query.first()
    
    # Get patients requiring oxygen
    oxygen_patients = db.session.query(Patient, Bed, Ward).select_from(Patient).join(
        Bed, Patient.id == Bed.patient_id
    ).join(
        Ward, Bed.ward_id == Ward.id
    ).filter(
        Patient.oxygen_required == True,
        Patient.discharged_on == None
    ).all()
    
    # Calculate oxygen usage statistics
    total_cylinders = oxygen.cylinders_in_stock + oxygen.cylinders_in_use if oxygen else 0
    usage_percentage = (oxygen.cylinders_in_use / total_cylinders * 100) if total_cylinders > 0 else 0
    
    days_to_refill = 0
    if oxygen and oxygen.next_refill_date:
        diff = oxygen.next_refill_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
        days_to_refill = max(0, diff.days)
    
    return render_template('staff/oxygen_status.html', 
                         oxygen=oxygen, 
                         oxygen_patients=oxygen_patients,
                         usage_percentage=usage_percentage,
                         days_to_refill=days_to_refill)

@app.route('/staff/patients')
def staff_patients():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get all active patients (not discharged)
    patients = Patient.query.filter(Patient.discharged_on.is_(None)).all()
    
    # Get patient details with bed and ward information
    patient_details = []
    for patient in patients:
        # Get current bed
        current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
        ward_name = current_bed.ward.name if current_bed else 'Not Assigned'
        bed_number = current_bed.bed_number if current_bed else 'N/A'
        
        # Get latest medical record
        latest_record = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).first()
        
        # Get active medications
        active_medications = Medication.query.filter_by(patient_id=patient.id, status='active').all()
        
        patient_info = {
            'patient': patient,
            'ward_name': ward_name,
            'bed_number': bed_number,
            'latest_record': latest_record,
            'active_medications': active_medications,
            'medication_count': len(active_medications)
        }
        patient_details.append(patient_info)
    
    return render_template('staff/patients.html', patient_details=patient_details)

@app.route('/admin/bed-management')
def admin_bed_management():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all beds with ward and patient information
    beds = db.session.query(Bed, Ward, Patient).join(Ward).outerjoin(Patient).all()
    
    # Get ward statistics for filtering
    wards = Ward.query.all()
    
    # Get bed statistics
    bed_stats = {
        'total': Bed.query.count(),
        'available': Bed.query.filter_by(status='empty').count(),
        'occupied': Bed.query.filter_by(status='occupied').count(),
        'reserved': Bed.query.filter_by(status='reserved').count(),
        'cleaning': Bed.query.filter_by(status='cleaning').count(),
        'maintenance': Bed.query.filter_by(status='maintenance').count()
    }
    
    return render_template('admin/bed_management.html', beds=beds, wards=wards, bed_stats=bed_stats)

@app.route('/admin/oxygen-management')
def admin_oxygen_management():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get oxygen information
    oxygen = Oxygen.query.first()
    
    # Get patients requiring oxygen
    oxygen_patients = db.session.query(Patient, Bed, Ward).select_from(Patient).join(
        Bed, Patient.id == Bed.patient_id
    ).join(
        Ward, Bed.ward_id == Ward.id
    ).filter(
        Patient.oxygen_required == True,
        Patient.discharged_on == None
    ).all()
    
    # Calculate usage statistics
    total_cylinders = oxygen.cylinders_in_stock + oxygen.cylinders_in_use if oxygen else 0
    usage_percentage = (oxygen.cylinders_in_use / total_cylinders * 100) if total_cylinders > 0 else 0
    
    # Get oxygen usage history (mock data for now)
    usage_history = []
    
    return render_template('admin/oxygen_management.html', 
                         oxygen=oxygen, 
                         oxygen_patients=oxygen_patients,
                         usage_percentage=usage_percentage,
                         usage_history=usage_history)

@app.route('/admin/staff-management')
def admin_staff_management():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all staff members
    staff_members = User.query.all()
    
    # Get staff activity statistics
    staff_activities = db.session.query(User, ActivityLog).join(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    # Calculate staff statistics
    staff_stats = {
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_admin': User.query.filter_by(role='admin').count(),
        'active_today': len(set([activity.user_id for user, activity in staff_activities if activity.timestamp.date() == datetime.now(timezone.utc).date()]))
    }
    
    return render_template('admin/staff_management.html', 
                         staff_members=staff_members, 
                         staff_activities=staff_activities,
                         staff_stats=staff_stats)

@app.route('/admin/patients')
def admin_patients():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all active patients (not discharged) - same as staff panel
    patients = Patient.query.filter(Patient.discharged_on.is_(None)).all()
    
    # Get patient details with bed and ward information - same structure as staff panel
    patient_details = []
    for patient in patients:
        # Get current bed
        current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
        ward_name = current_bed.ward.name if current_bed else 'Not Assigned'
        bed_number = current_bed.bed_number if current_bed else 'N/A'
        
        # Get latest medical record
        latest_record = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).first()
        
        # Get active medications
        active_medications = Medication.query.filter_by(patient_id=patient.id, status='active').all()
        
        patient_info = {
            'patient': patient,
            'ward_name': ward_name,
            'bed_number': bed_number,
            'latest_record': latest_record,
            'active_medications': active_medications,
            'medication_count': len(active_medications)
        }
        patient_details.append(patient_info)
    
    # Also get discharged patients for admin overview
    discharged_patients = Patient.query.filter(Patient.discharged_on.isnot(None)).all()
    
    # Calculate patient statistics
    patient_stats = {
        'total_active': len(patient_details),
        'total_discharged': len(discharged_patients),
        'oxygen_required': len([p for p in patient_details if p['patient'].oxygen_required]),
        'total_medications': sum([p['medication_count'] for p in patient_details])
    }
    
    return render_template('admin/patients.html', 
                         patient_details=patient_details,
                         discharged_patients=discharged_patients,
                         patient_stats=patient_stats)

# Enhanced Features Routes
@app.route('/admin/inventory')
def admin_inventory():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get inventory items
    inventory_items = Inventory.query.all()
    
    # Calculate statistics
    low_stock_items = [item for item in inventory_items if item.current_stock <= item.minimum_stock]
    
    # Handle timezone-aware datetime comparison
    current_time = datetime.now(timezone.utc)
    expired_items = []
    for item in inventory_items:
        if item.expiry_date:
            # If expiry_date is timezone-naive, make it timezone-aware
            if item.expiry_date.tzinfo is None:
                expiry_aware = item.expiry_date.replace(tzinfo=timezone.utc)
            else:
                expiry_aware = item.expiry_date
            
            if expiry_aware < current_time:
                expired_items.append(item)
    
    inventory_stats = {
        'total_items': len(inventory_items),
        'low_stock': len(low_stock_items),
        'expired': len(expired_items),
        'categories': len(set([item.category for item in inventory_items]))
    }
    
    return render_template('admin/inventory.html', 
                         inventory_items=inventory_items,
                         inventory_stats=inventory_stats,
                         low_stock_items=low_stock_items,
                         expired_items=expired_items,
                         current_time=current_time)

@app.route('/admin/reports')
def admin_reports():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Generate comprehensive statistics for reports
    from datetime import timedelta
    
    # Date ranges
    today = datetime.now(timezone.utc).date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Bed statistics
    bed_stats = {
        'total_beds': Bed.query.count(),
        'occupancy_rate': (Bed.query.filter_by(status='occupied').count() / Bed.query.count() * 100) if Bed.query.count() > 0 else 0,
        'avg_stay_duration': 3.2  # Mock data
    }
    
    # Patient statistics
    patient_stats = {
        'total_admissions': Patient.query.count(),
        'active_patients': Patient.query.filter_by(discharged_on=None).count(),
        'discharged_this_month': Patient.query.filter(Patient.discharged_on >= month_ago).count()
    }
    
    # Staff statistics
    staff_stats = {
        'total_staff': User.query.filter_by(role='staff').count(),
        'active_shifts': Shift.query.filter_by(status='active').count(),
        'completed_shifts': Shift.query.filter_by(status='completed').count()
    }
    
    return render_template('admin/reports.html',
                         bed_stats=bed_stats,
                         patient_stats=patient_stats,
                         staff_stats=staff_stats)

@app.route('/admin/notifications')
def admin_notifications():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all notifications
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    
    # Get unread count
    unread_count = Notification.query.filter_by(is_read=False).count()
    
    return render_template('admin/notifications.html',
                         notifications=notifications,
                         unread_count=unread_count)

@app.route('/staff/medical-records')
def staff_medical_records():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get medical records for active patients
    records = db.session.query(MedicalRecord, Patient).join(Patient).filter(
        Patient.discharged_on == None
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    return render_template('staff/medical_records.html', records=records)

@app.route('/staff/shifts')
def staff_shifts():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get shifts for current user
    user_shifts = Shift.query.filter_by(user_id=session['user_id']).order_by(Shift.start_time.desc()).all()
    
    # Get upcoming shifts
    upcoming_shifts = Shift.query.filter(
        Shift.user_id == session['user_id'],
        Shift.start_time > datetime.now(timezone.utc),
        Shift.status == 'scheduled'
    ).order_by(Shift.start_time).all()
    
    return render_template('staff/shifts.html', 
                         user_shifts=user_shifts,
                         upcoming_shifts=upcoming_shifts)

@app.route('/staff/notifications')
def staff_notifications():
    if 'user_id' not in session or session['user_role'] != 'staff':
        return redirect(url_for('login'))
    
    # Get notifications for current user and system-wide
    notifications = Notification.query.filter(
        (Notification.user_id == session['user_id']) | (Notification.user_id == None)
    ).order_by(Notification.created_at.desc()).all()
    
    unread_count = Notification.query.filter(
        ((Notification.user_id == session['user_id']) | (Notification.user_id == None)),
        Notification.is_read == False
    ).count()
    
    return render_template('staff/notifications.html',
                         notifications=notifications,
                         unread_count=unread_count)

# API Routes for enhanced features
@app.route('/api/create_emergency_alert', methods=['POST'])
def create_emergency_alert():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    alert = EmergencyAlert(
        alert_type=data.get('alert_type'),
        location=data.get('location'),
        description=data.get('description'),
        severity=data.get('severity'),
        reported_by=session['user_id']
    )
    
    db.session.add(alert)
    db.session.commit()
    
    # Create notification for all users
    notification = Notification(
        title=f"Emergency Alert: {alert.alert_type.replace('_', ' ').title()}",
        message=f"Location: {alert.location} - {alert.description}",
        type='error',
        priority='critical'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'alert_id': alert.id})

@app.route('/api/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Notification not found'}), 404

# Inventory Management API Routes
@app.route('/api/inventory/add', methods=['POST'])
def add_inventory_item():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Create new inventory item
    item = Inventory(
        item_name=data.get('item_name'),
        category=data.get('category'),
        current_stock=int(data.get('current_stock', 0)),
        minimum_stock=int(data.get('minimum_stock', 10)),
        unit=data.get('unit'),
        cost_per_unit=float(data.get('cost_per_unit', 0)) if data.get('cost_per_unit') else None,
        supplier=data.get('supplier'),
        expiry_date=datetime.strptime(data.get('expiry_date'), '%Y-%m-%d') if data.get('expiry_date') else None,
        last_restocked=datetime.now(timezone.utc)
    )
    
    db.session.add(item)
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='add_inventory_item',
        target=f"Added {item.item_name} to inventory",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'item_id': item.id})

@app.route('/api/inventory/bulk_update', methods=['POST'])
def bulk_update_inventory():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    item_ids = data.get('item_ids', [])
    update_type = data.get('update_type')
    
    updated_count = 0
    
    for item_id in item_ids:
        item = Inventory.query.get(item_id)
        if item:
            if update_type == 'restock':
                additional_stock = int(data.get('additional_stock', 0))
                item.current_stock += additional_stock
                item.last_restocked = datetime.now(timezone.utc)
            elif update_type == 'update_minimum':
                new_minimum = int(data.get('new_minimum', 10))
                item.minimum_stock = new_minimum
            elif update_type == 'update_supplier':
                new_supplier = data.get('new_supplier', '')
                item.supplier = new_supplier
            elif update_type == 'update_cost':
                new_cost = float(data.get('new_cost', 0))
                item.cost_per_unit = new_cost
            
            updated_count += 1
    
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='bulk_update_inventory',
        target=f"Bulk updated {updated_count} inventory items ({update_type})",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'updated_count': updated_count})

@app.route('/api/inventory/export')
def export_inventory():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    inventory_items = Inventory.query.all()
    
    # Create CSV data
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Item Name', 'Category', 'Current Stock', 'Minimum Stock', 
                     'Unit', 'Cost Per Unit', 'Supplier', 'Expiry Date', 'Last Restocked'])
    
    # Write data
    for item in inventory_items:
        writer.writerow([
            item.id,
            item.item_name,
            item.category,
            item.current_stock,
            item.minimum_stock,
            item.unit,
            item.cost_per_unit or 0,
            item.supplier or '',
            item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
            item.last_restocked.strftime('%Y-%m-%d %H:%M') if item.last_restocked else ''
        ])
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='export_inventory',
        target=f"Exported {len(inventory_items)} inventory items",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    # Return CSV data
    csv_data = output.getvalue()
    output.close()
    
    return jsonify({
        'success': True,
        'csv_data': csv_data,
        'filename': f'inventory_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    })

@app.route('/api/inventory/report')
def generate_inventory_report():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    inventory_items = Inventory.query.all()
    
    # Calculate statistics
    total_items = len(inventory_items)
    low_stock_items = [item for item in inventory_items if item.current_stock <= item.minimum_stock]
    
    # Handle timezone-aware datetime comparison for expired items
    current_time = datetime.now(timezone.utc)
    expired_items = []
    for item in inventory_items:
        if item.expiry_date:
            # If expiry_date is timezone-naive, make it timezone-aware
            if item.expiry_date.tzinfo is None:
                expiry_aware = item.expiry_date.replace(tzinfo=timezone.utc)
            else:
                expiry_aware = item.expiry_date
            
            if expiry_aware < current_time:
                expired_items.append(item)
    
    # Category breakdown
    categories = {}
    total_value = 0
    
    for item in inventory_items:
        if item.category not in categories:
            categories[item.category] = {'count': 0, 'total_stock': 0, 'value': 0}
        
        categories[item.category]['count'] += 1
        categories[item.category]['total_stock'] += item.current_stock
        
        if item.cost_per_unit:
            item_value = item.current_stock * item.cost_per_unit
            categories[item.category]['value'] += item_value
            total_value += item_value
    
    # Generate report data
    report_data = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_items': total_items,
            'low_stock_count': len(low_stock_items),
            'expired_count': len(expired_items),
            'total_inventory_value': round(total_value, 2),
            'categories_count': len(categories)
        },
        'categories': categories,
        'low_stock_items': [
            {
                'name': item.item_name,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'category': item.category
            } for item in low_stock_items
        ],
        'expired_items': [
            {
                'name': item.item_name,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                'category': item.category,
                'current_stock': item.current_stock
            } for item in expired_items
        ]
    }
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='generate_inventory_report',
        target=f"Generated inventory report with {total_items} items",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'report': report_data})

@app.route('/api/inventory/restock/<int:item_id>', methods=['POST'])
def restock_inventory_item(item_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    quantity = int(data.get('quantity', 0))
    
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item.current_stock += quantity
    item.last_restocked = datetime.now(timezone.utc)
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='restock_inventory',
        target=f"Restocked {item.item_name} with {quantity} {item.unit}",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'new_stock': item.current_stock})

@app.route('/api/update_bed_status', methods=['POST'])
def update_bed_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    bed_id = data.get('bed_id')
    new_status = data.get('status')
    
    bed = Bed.query.get(bed_id)
    if not bed:
        return jsonify({'error': 'Bed not found'}), 404
    
    old_status = bed.status
    bed.status = new_status
    
    # If status is changing to empty, discharge patient
    if new_status == 'empty' and bed.patient_id:
        patient = Patient.query.get(bed.patient_id)
        if patient:
            patient.discharged_on = datetime.now(timezone.utc)
        bed.patient_id = None
    
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='update_bed_status',
        target=f'Bed {bed.bed_number} from {old_status} to {new_status}',
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/admit_patient', methods=['POST'])
def admit_patient():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    bed_id = data.get('bed_id')
    patient_name = data.get('patient_name')
    patient_age = data.get('patient_age')
    patient_gender = data.get('patient_gender')
    
    bed = Bed.query.get(bed_id)
    if not bed or bed.status != 'empty':
        return jsonify({'error': 'Bed not available'}), 400
    
    # Create new patient
    patient = Patient(
        name=patient_name,
        age=patient_age,
        gender=patient_gender,
        admitted_on=datetime.now(timezone.utc)
    )
    db.session.add(patient)
    db.session.flush()  # Get patient ID
    
    # Update bed
    bed.patient_id = patient.id
    bed.status = 'occupied'
    
    db.session.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=session['user_id'],
        action='admit_patient',
        target=f'Patient {patient_name} to Bed {bed.bed_number}',
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/dashboard_stats')
def dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_beds = Bed.query.count()
    occupied_beds = Bed.query.filter_by(status='occupied').count()
    available_beds = Bed.query.filter_by(status='empty').count()
    
    return jsonify({
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0
    })

# Bed Management API Routes
@app.route('/api/beds/add', methods=['POST'])
def add_bed():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        ward_id = data.get('ward_id')
        bed_number = data.get('bed_number')
        
        # Check if bed number already exists in the ward
        existing_bed = Bed.query.filter_by(ward_id=ward_id, bed_number=bed_number).first()
        if existing_bed:
            return jsonify({'error': 'Bed number already exists in this ward'}), 400
        
        # Create new bed
        new_bed = Bed(
            ward_id=ward_id,
            bed_number=bed_number,
            status='empty',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_bed)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='create',
            target=f'bed {bed_number}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Bed {bed_number} added successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/beds/bulk-update', methods=['POST'])
def bulk_update_beds():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        bed_ids = data.get('bed_ids', [])
        new_status = data.get('status')
        
        if not bed_ids or not new_status:
            return jsonify({'error': 'Missing bed IDs or status'}), 400
        
        # Update beds
        beds = Bed.query.filter(Bed.id.in_(bed_ids)).all()
        updated_count = 0
        
        for bed in beds:
            # Only update if status is different and valid
            if bed.status != new_status and new_status in ['empty', 'occupied', 'reserved', 'cleaning', 'maintenance']:
                old_status = bed.status
                bed.status = new_status
                bed.updated_at = datetime.now(timezone.utc)
                
                # Log activity
                log = ActivityLog(
                    user_id=session['user_id'],
                    action='update',
                    target=f'bed {bed.bed_number} from {old_status} to {new_status}',
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(log)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Updated {updated_count} bed(s) to {new_status}',
            'updated_count': updated_count
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/beds/export')
def export_beds():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import csv
        import io
        from flask import make_response
        
        # Get all beds with ward and patient info
        beds_data = db.session.query(Bed, Ward, Patient).join(Ward).outerjoin(Patient).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Ward Name', 'Ward Type', 'Bed Number', 'Status', 'Patient Name', 'Patient Age', 'Patient Gender', 'Last Updated'])
        
        # Write data
        for bed, ward, patient in beds_data:
            writer.writerow([
                ward.name,
                ward.type,
                bed.bed_number,
                bed.status,
                patient.name if patient else '',
                patient.age if patient else '',
                patient.gender if patient else '',
                bed.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=beds_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='export',
            target='bed data',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/beds/report')
def generate_bed_report():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get comprehensive bed statistics
        total_beds = Bed.query.count()
        bed_stats = {
            'total': total_beds,
            'available': Bed.query.filter_by(status='empty').count(),
            'occupied': Bed.query.filter_by(status='occupied').count(),
            'reserved': Bed.query.filter_by(status='reserved').count(),
            'cleaning': Bed.query.filter_by(status='cleaning').count(),
            'maintenance': Bed.query.filter_by(status='maintenance').count()
        }
        
        # Calculate occupancy rate
        occupancy_rate = (bed_stats['occupied'] / total_beds * 100) if total_beds > 0 else 0
        
        # Get ward-wise statistics
        ward_stats = []
        wards = Ward.query.all()
        for ward in wards:
            ward_beds = Bed.query.filter_by(ward_id=ward.id).count()
            ward_occupied = Bed.query.filter_by(ward_id=ward.id, status='occupied').count()
            ward_occupancy = (ward_occupied / ward_beds * 100) if ward_beds > 0 else 0
            
            ward_stats.append({
                'name': ward.name,
                'type': ward.type,
                'total_beds': ward_beds,
                'occupied': ward_occupied,
                'occupancy_rate': round(ward_occupancy, 1)
            })
        
        # Get recent activities (last 24 hours)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= yesterday,
            ActivityLog.target.like('%bed%')
        ).count()
        
        report_data = {
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            'bed_stats': bed_stats,
            'occupancy_rate': round(occupancy_rate, 1),
            'ward_stats': ward_stats,
            'recent_activities_24h': recent_activities,
            'total_wards': len(wards)
        }
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='generate',
            target='bed report',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'report': report_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/beds/delete/<int:bed_id>', methods=['DELETE'])
def delete_bed(bed_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        bed = Bed.query.get_or_404(bed_id)
        
        # Check if bed is occupied
        if bed.status == 'occupied':
            return jsonify({'error': 'Cannot delete occupied bed'}), 400
        
        bed_number = bed.bed_number
        db.session.delete(bed)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='delete',
            target=f'bed {bed_number}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Bed {bed_number} deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Staff Management API Routes
@app.route('/api/staff/add', methods=['POST'])
def add_staff():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')
        password = data.get('password')
        
        # Validate required fields
        if not all([name, email, role, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new staff member
        new_staff = User(
            name=name,
            email=email,
            role=role,
            password=generate_password_hash(password),
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_staff)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='create',
            target=f'staff {name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Staff member {name} added successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/bulk-import', methods=['POST'])
def bulk_import_staff():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        import csv
        import io
        
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        added_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_input, start=2):  # Start at 2 because row 1 is header
            try:
                name = row.get('name', '').strip()
                email = row.get('email', '').strip()
                role = row.get('role', '').strip().lower()
                password = row.get('password', '').strip()
                
                # Validate required fields
                if not all([name, email, role, password]):
                    errors.append(f'Row {row_num}: Missing required fields')
                    continue
                
                # Validate role
                if role not in ['admin', 'staff']:
                    errors.append(f'Row {row_num}: Invalid role "{role}". Must be "admin" or "staff"')
                    continue
                
                # Check if email already exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    errors.append(f'Row {row_num}: Email "{email}" already exists')
                    continue
                
                # Create new staff member
                new_staff = User(
                    name=name,
                    email=email,
                    role=role,
                    password=generate_password_hash(password),
                    created_at=datetime.now(timezone.utc)
                )
                
                db.session.add(new_staff)
                added_count += 1
                
            except Exception as e:
                errors.append(f'Row {row_num}: {str(e)}')
        
        if added_count > 0:
            # Log activity
            log = ActivityLog(
                user_id=session['user_id'],
                action='bulk_import',
                target=f'{added_count} staff members',
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(log)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {added_count} staff members',
            'added_count': added_count,
            'errors': errors
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/export')
def export_staff():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import csv
        import io
        from flask import make_response
        
        # Get all staff members
        staff_members = User.query.all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Name', 'Email', 'Role', 'Created Date', 'Status'])
        
        # Write data
        for staff in staff_members:
            writer.writerow([
                staff.id,
                staff.name,
                staff.email,
                staff.role,
                staff.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Active'  # You can add a status field to User model if needed
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=staff_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='export',
            target='staff data',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/report')
def generate_staff_report():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get comprehensive staff statistics
        total_staff = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        staff_count = User.query.filter_by(role='staff').count()
        
        # Get activity statistics (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= thirty_days_ago
        ).count()
        
        # Get most active staff members (last 30 days)
        active_staff = db.session.query(
            User.name,
            User.role,
            db.func.count(ActivityLog.id).label('activity_count')
        ).join(ActivityLog).filter(
            ActivityLog.timestamp >= thirty_days_ago
        ).group_by(User.id).order_by(
            db.func.count(ActivityLog.id).desc()
        ).limit(5).all()
        
        # Get login statistics (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        login_activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= seven_days_ago,
            ActivityLog.action == 'login'
        ).count()
        
        # Get staff joined this month
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_staff_this_month = User.query.filter(
            User.created_at >= start_of_month
        ).count()
        
        report_data = {
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            'staff_stats': {
                'total': total_staff,
                'admin': admin_count,
                'staff': staff_count,
                'new_this_month': new_staff_this_month
            },
            'activity_stats': {
                'total_activities_30d': recent_activities,
                'logins_7d': login_activities,
                'avg_activities_per_day': round(recent_activities / 30, 1)
            },
            'most_active_staff': [
                {
                    'name': staff.name,
                    'role': staff.role,
                    'activity_count': staff.activity_count
                } for staff in active_staff
            ]
        }
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='generate',
            target='staff report',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'report': report_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/delete/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        staff = User.query.get_or_404(staff_id)
        
        # Prevent deleting the last admin
        if staff.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last administrator'}), 400
        
        # Prevent self-deletion
        if staff.id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        staff_name = staff.name
        db.session.delete(staff)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='delete',
            target=f'staff {staff_name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Staff member {staff_name} deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/reset-password/<int:staff_id>', methods=['POST'])
def reset_staff_password(staff_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        staff = User.query.get_or_404(staff_id)
        
        # Generate new temporary password
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Update password
        staff.password = generate_password_hash(new_password)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='reset_password',
            target=f'staff {staff.name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Password reset for {staff.name}',
            'new_password': new_password
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Patient Management API Routes
@app.route('/api/patients/admit', methods=['POST'])
def admit_new_patient():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        bed_id = data.get('bed_id')
        oxygen_required = data.get('oxygen_required', False)
        oxygen_flow_rate = data.get('oxygen_flow_rate')
        
        # Validate required fields
        if not all([name, age, gender, bed_id]):
            return jsonify({'error': 'Name, age, gender, and bed are required'}), 400
        
        # Check if bed is available
        bed = Bed.query.get(bed_id)
        if not bed:
            return jsonify({'error': 'Bed not found'}), 400
        if bed.status != 'empty':
            return jsonify({'error': 'Bed is not available'}), 400
        
        # Create new patient
        patient = Patient(
            name=name,
            age=int(age),
            gender=gender,
            oxygen_required=oxygen_required,
            oxygen_flow_rate=float(oxygen_flow_rate) if oxygen_flow_rate else None,
            admitted_on=datetime.now(timezone.utc)
        )
        
        db.session.add(patient)
        db.session.flush()  # Get the patient ID
        
        # Update bed status and assign patient
        bed.status = 'occupied'
        bed.patient_id = patient.id
        bed.last_updated = datetime.now(timezone.utc)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='admit_patient',
            target=f'patient {name} to bed {bed.bed_number}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Patient {name} admitted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/bulk-discharge', methods=['POST'])
def bulk_discharge_patients():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        patient_ids = data.get('patient_ids', [])
        
        if not patient_ids:
            return jsonify({'error': 'No patients selected'}), 400
        
        # Get patients and their beds
        patients = Patient.query.filter(
            Patient.id.in_(patient_ids),
            Patient.discharged_on.is_(None)
        ).all()
        
        discharged_count = 0
        
        for patient in patients:
            # Discharge patient
            patient.discharged_on = datetime.now(timezone.utc)
            
            # Free up the bed
            current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
            if current_bed:
                current_bed.status = 'cleaning'  # Set to cleaning after discharge
                current_bed.patient_id = None
                current_bed.last_updated = datetime.now(timezone.utc)
            
            # Log activity
            log = ActivityLog(
                user_id=session['user_id'],
                action='discharge_patient',
                target=f'patient {patient.name}',
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(log)
            discharged_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully discharged {discharged_count} patient(s)',
            'discharged_count': discharged_count
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/discharge/<int:patient_id>', methods=['POST'])
def discharge_single_patient(patient_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        if patient.discharged_on:
            return jsonify({'error': 'Patient already discharged'}), 400
        
        # Discharge patient
        patient.discharged_on = datetime.now(timezone.utc)
        
        # Free up the bed
        current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
        if current_bed:
            current_bed.status = 'cleaning'
            current_bed.patient_id = None
            current_bed.last_updated = datetime.now(timezone.utc)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='discharge_patient',
            target=f'patient {patient.name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Patient {patient.name} discharged successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/export')
def export_patients():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import csv
        import io
        from flask import make_response
        
        # Get all patients with bed and ward info
        patients_data = db.session.query(Patient, Bed, Ward).outerjoin(Bed).outerjoin(Ward).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Patient ID', 'Name', 'Age', 'Gender', 'Ward', 'Bed Number', 
            'Oxygen Required', 'Oxygen Flow Rate', 'Admitted Date', 
            'Discharged Date', 'Length of Stay (Days)', 'Status'
        ])
        
        # Write data
        for patient, bed, ward in patients_data:
            length_of_stay = ''
            status = 'Active'
            
            if patient.discharged_on:
                length_of_stay = (patient.discharged_on - patient.admitted_on).days
                status = 'Discharged'
            elif patient.admitted_on:
                length_of_stay = (datetime.now(timezone.utc) - patient.admitted_on).days
            
            writer.writerow([
                patient.id,
                patient.name,
                patient.age,
                patient.gender,
                ward.name if ward else '',
                bed.bed_number if bed else '',
                'Yes' if patient.oxygen_required else 'No',
                patient.oxygen_flow_rate or '',
                patient.admitted_on.strftime('%Y-%m-%d %H:%M:%S') if patient.admitted_on else '',
                patient.discharged_on.strftime('%Y-%m-%d %H:%M:%S') if patient.discharged_on else '',
                length_of_stay,
                status
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='export',
            target='patient data',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/report')
def generate_patient_report():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from datetime import timedelta
        
        # Get all patients
        all_patients = Patient.query.all()
        active_patients = Patient.query.filter(Patient.discharged_on.is_(None)).all()
        discharged_patients = Patient.query.filter(Patient.discharged_on.isnot(None)).all()
        
        # Calculate statistics
        total_patients = len(all_patients)
        total_active = len(active_patients)
        total_discharged = len(discharged_patients)
        
        # Oxygen statistics
        oxygen_required = len([p for p in active_patients if p.oxygen_required])
        
        # Average length of stay for discharged patients
        total_stay_days = 0
        discharged_count = 0
        for patient in discharged_patients:
            if patient.admitted_on and patient.discharged_on:
                stay_days = (patient.discharged_on - patient.admitted_on).days
                total_stay_days += stay_days
                discharged_count += 1
        
        avg_length_of_stay = round(total_stay_days / discharged_count, 1) if discharged_count > 0 else 0
        
        # Ward distribution
        ward_distribution = {}
        for patient in active_patients:
            bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
            if bed and bed.ward:
                ward_name = bed.ward.name
                if ward_name not in ward_distribution:
                    ward_distribution[ward_name] = 0
                ward_distribution[ward_name] += 1
        
        # Recent admissions (last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_admissions = Patient.query.filter(
            Patient.admitted_on >= week_ago
        ).count()
        
        # Recent discharges (last 7 days)
        recent_discharges = Patient.query.filter(
            Patient.discharged_on >= week_ago
        ).count()
        
        # Monthly admission trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_start = datetime.now(timezone.utc).replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            admissions = Patient.query.filter(
                Patient.admitted_on >= month_start,
                Patient.admitted_on < month_end
            ).count()
            
            monthly_trends.append({
                'month': month_start.strftime('%B %Y'),
                'admissions': admissions
            })
        
        monthly_trends.reverse()  # Show oldest to newest
        
        # Generate report data
        report_data = {
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_patients': total_patients,
                'active_patients': total_active,
                'discharged_patients': total_discharged,
                'oxygen_required': oxygen_required,
                'avg_length_of_stay': avg_length_of_stay,
                'recent_admissions': recent_admissions,
                'recent_discharges': recent_discharges
            },
            'ward_distribution': ward_distribution,
            'monthly_trends': monthly_trends,
            'occupancy_rate': round((total_active / Bed.query.count() * 100), 1) if Bed.query.count() > 0 else 0
        }
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='generate',
            target='patient report',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'report': report_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/edit/<int:patient_id>', methods=['PUT'])
def edit_patient(patient_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Find the patient
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if patient is discharged
        if patient.discharged_on:
            return jsonify({'error': 'Cannot edit discharged patient'}), 400
        
        # Get current bed assignment
        current_bed = Bed.query.filter_by(patient_id=patient_id, status='occupied').first()
        
        # Update basic patient information
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.gender = data.get('gender', patient.gender)
        
        # Handle bed change if requested
        new_bed_id = data.get('bed_id')
        if new_bed_id and str(new_bed_id) != 'null' and new_bed_id != '':
            new_bed_id = int(new_bed_id)
            
            # Only process if it's actually a different bed
            if not current_bed or current_bed.id != new_bed_id:
                # Check if new bed is available
                new_bed = Bed.query.get(new_bed_id)
                if not new_bed:
                    return jsonify({'error': 'New bed not found'}), 404
                
                if new_bed.status != 'empty':
                    return jsonify({'error': 'New bed is not available'}), 400
                
                # Transfer patient to new bed
                if current_bed:
                    current_bed.status = 'cleaning'
                    current_bed.patient_id = None
                    current_bed.last_updated = datetime.now(timezone.utc)
                
                new_bed.status = 'occupied'
                new_bed.patient_id = patient_id
                new_bed.last_updated = datetime.now(timezone.utc)
                
                # Log the bed transfer
                transfer_message = f"Patient {patient.name} transferred to {new_bed.ward.name} {new_bed.bed_number}"
                if current_bed:
                    transfer_message = f"Patient {patient.name} from {current_bed.ward.name} {current_bed.bed_number} to {new_bed.ward.name} {new_bed.bed_number}"
                
                log = ActivityLog(
                    user_id=session['user_id'],
                    action='transfer',
                    target=transfer_message,
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(log)
        
        # Handle oxygen requirements
        oxygen_required = data.get('oxygen_required', False)
        patient.oxygen_required = oxygen_required
        
        if oxygen_required:
            patient.oxygen_flow_rate = data.get('oxygen_flow_rate', patient.oxygen_flow_rate)
        else:
            patient.oxygen_flow_rate = None
        
        # Update additional patient fields if provided (only if the fields exist in the model)
        if 'phone' in data and hasattr(patient, 'phone'):
            patient.phone = data['phone']
        if 'address' in data and hasattr(patient, 'address'):
            patient.address = data['address']
        if 'emergency_contact' in data and hasattr(patient, 'emergency_contact'):
            patient.emergency_contact = data['emergency_contact']
        if 'blood_group' in data and hasattr(patient, 'blood_group'):
            patient.blood_group = data['blood_group']
        if 'allergies' in data and hasattr(patient, 'allergies'):
            patient.allergies = data['allergies']
        if 'medical_history' in data and hasattr(patient, 'medical_history'):
            patient.medical_history = data['medical_history']
        
        # Commit changes
        db.session.commit()
        
        # Log the patient update
        log = ActivityLog(
            user_id=session['user_id'],
            action='update',
            target=f"Patient {patient.name} information updated",
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient information updated successfully',
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
                'oxygen_required': patient.oxygen_required,
                'oxygen_flow_rate': patient.oxygen_flow_rate
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/get/<int:patient_id>')
def get_patient_for_edit(patient_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get patient with current bed information
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get current bed assignment
        current_bed = Bed.query.filter_by(patient_id=patient_id, status='occupied').first()
        
        # Get available beds for potential transfer
        available_beds = db.session.query(Bed, Ward).join(Ward).filter(
            Bed.status == 'empty'
        ).all()
        
        available_beds_list = []
        for bed, ward in available_beds:
            available_beds_list.append({
                'id': bed.id,
                'bed_number': bed.bed_number,
                'ward_name': ward.name,
                'display': f"{ward.name} - Bed {bed.bed_number}"
            })
        
        # Add current bed to the list if patient has one
        if current_bed:
            available_beds_list.insert(0, {
                'id': current_bed.id,
                'bed_number': current_bed.bed_number,
                'ward_name': current_bed.ward.name,
                'display': f"{current_bed.ward.name} - Bed {current_bed.bed_number} (Current)"
            })
        
        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'phone': getattr(patient, 'phone', '') or '',
            'address': getattr(patient, 'address', '') or '',
            'emergency_contact': getattr(patient, 'emergency_contact', '') or '',
            'blood_group': getattr(patient, 'blood_group', '') or '',
            'allergies': getattr(patient, 'allergies', '') or '',
            'medical_history': getattr(patient, 'medical_history', '') or '',
            'oxygen_required': patient.oxygen_required,
            'oxygen_flow_rate': patient.oxygen_flow_rate or '',
            'current_bed_id': current_bed.id if current_bed else None,
            'available_beds': available_beds_list
        }
        
        return jsonify({'success': True, 'patient': patient_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/patients/discharge/<int:patient_id>', methods=['POST'])
def staff_discharge_patient(patient_id):
    if 'user_id' not in session or session['user_role'] not in ['admin', 'staff']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json() or {}
        
        # Find the patient
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if patient is already discharged
        if patient.discharged_on:
            return jsonify({'error': 'Patient is already discharged'}), 400
        
        # Get the current bed assignment
        current_bed = Bed.query.filter_by(patient_id=patient_id, status='occupied').first()
        
        # Discharge the patient
        patient.discharged_on = datetime.now(timezone.utc)
        
        # Update bed status if patient has a bed
        if current_bed:
            current_bed.status = 'cleaning'
            current_bed.patient_id = None
            current_bed.last_updated = datetime.now(timezone.utc)
        
        # Update any active treatment records (if status field exists)
        try:
            active_records = MedicalRecord.query.filter_by(
                patient_id=patient_id
            ).all()
            
            for record in active_records:
                # Only update status if the field exists
                if hasattr(record, 'status'):
                    record.status = 'completed'
                if hasattr(record, 'discharge_date'):
                    record.discharge_date = datetime.now(timezone.utc)
                if hasattr(record, 'discharge_summary') and data.get('discharge_summary'):
                    record.discharge_summary = data['discharge_summary']
        except Exception as e:
            print(f"Warning: Could not update medical records: {e}")
        
        # Update active medications to completed
        try:
            active_medications = Medication.query.filter_by(
                patient_id=patient_id,
                status='active'
            ).all()
            
            for medication in active_medications:
                medication.status = 'completed'
                medication.end_date = datetime.now(timezone.utc)
        except Exception as e:
            print(f"Warning: Could not update medications: {e}")
        
        # Commit all changes
        db.session.commit()
        
        # Log the discharge activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='discharge',
            target=f"Patient {patient.name} discharged by staff",
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Patient {patient.name} has been successfully discharged',
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'discharged_on': patient.discharged_on.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Prescription Management API Routes
@app.route('/api/prescriptions/add', methods=['POST'])
def add_prescription():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        patient_id = data.get('patient_id')
        medication_name = data.get('medication_name')
        dosage = data.get('dosage')
        frequency = data.get('frequency')
        route = data.get('route')
        duration_days = data.get('duration_days')
        notes = data.get('notes', '')
        
        # Validate required fields
        if not all([patient_id, medication_name, dosage, frequency, route]):
            return jsonify({'error': 'All medication fields are required'}), 400
        
        # Check if patient exists and is not discharged
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        if patient.discharged_on:
            return jsonify({'error': 'Cannot prescribe medication to discharged patient'}), 400
        
        # Get admin user info
        admin_user = User.query.get(session['user_id'])
        
        # Calculate end date if duration is provided
        end_date = None
        if duration_days:
            try:
                end_date = datetime.now(timezone.utc) + timedelta(days=int(duration_days))
            except ValueError:
                return jsonify({'error': 'Invalid duration format'}), 400
        
        # Create new medication prescription
        new_medication = Medication(
            patient_id=patient_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            route=route,
            end_date=end_date,
            status='active',
            prescribed_by=admin_user.name,
            notes=notes,
            start_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_medication)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='prescribe',
            target=f'{medication_name} to patient {patient.name}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully prescribed {medication_name} to {patient.name}',
            'medication': {
                'id': new_medication.id,
                'medication_name': new_medication.medication_name,
                'dosage': new_medication.dosage,
                'frequency': new_medication.frequency,
                'route': new_medication.route,
                'prescribed_by': new_medication.prescribed_by
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/prescriptions/patient/<int:patient_id>')
def get_patient_prescriptions(patient_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get patient
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get all medications for the patient
        medications = Medication.query.filter_by(patient_id=patient_id).order_by(Medication.created_at.desc()).all()
        
        medication_list = []
        for med in medications:
            medication_list.append({
                'id': med.id,
                'medication_name': med.medication_name,
                'dosage': med.dosage,
                'frequency': med.frequency,
                'route': med.route,
                'status': med.status,
                'prescribed_by': med.prescribed_by,
                'start_date': med.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'end_date': med.end_date.strftime('%Y-%m-%d %H:%M:%S') if med.end_date else None,
                'notes': med.notes or '',
                'created_at': med.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender
            },
            'medications': medication_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prescriptions/update/<int:medication_id>', methods=['PUT'])
def update_prescription(medication_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Find the medication
        medication = Medication.query.get(medication_id)
        if not medication:
            return jsonify({'error': 'Prescription not found'}), 404
        
        # Update medication status
        new_status = data.get('status')
        if new_status and new_status in ['active', 'completed', 'discontinued']:
            medication.status = new_status
            
            # If completing or discontinuing, set end date
            if new_status in ['completed', 'discontinued'] and not medication.end_date:
                medication.end_date = datetime.now(timezone.utc)
        
        # Update notes if provided
        if 'notes' in data:
            medication.notes = data['notes']
        
        medication.updated_at = datetime.now(timezone.utc)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='update',
            target=f'prescription {medication.medication_name} for patient',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Prescription updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/prescriptions')
def admin_prescriptions():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all active patients for prescription
    active_patients = Patient.query.filter(Patient.discharged_on.is_(None)).all()
    
    # Get recent prescriptions with patient info
    recent_prescriptions = db.session.query(Medication, Patient).join(Patient).order_by(Medication.created_at.desc()).limit(20).all()
    
    # Get prescription statistics
    prescription_stats = {
        'total_prescriptions': Medication.query.count(),
        'active_prescriptions': Medication.query.filter_by(status='active').count(),
        'completed_prescriptions': Medication.query.filter_by(status='completed').count(),
        'discontinued_prescriptions': Medication.query.filter_by(status='discontinued').count()
    }
    
    return render_template('admin/prescriptions.html',
                         active_patients=active_patients,
                         recent_prescriptions=recent_prescriptions,
                         prescription_stats=prescription_stats)

@app.route('/admin/shift-management')
def admin_shift_management():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get shift statistics
    shift_stats = {
        'total_shifts': Shift.query.count(),
        'active_shifts': Shift.query.filter_by(status='active').count(),
        'scheduled_shifts': Shift.query.filter_by(status='scheduled').count(),
        'completed_shifts': Shift.query.filter_by(status='completed').count()
    }
    
    # Get all staff members for shift assignment
    staff_members = User.query.filter_by(role='staff').all()
    
    # Get recent shifts with user info
    recent_shifts = db.session.query(Shift, User).join(User).order_by(Shift.start_time.desc()).limit(20).all()
    
    # Get upcoming shifts (next 7 days)
    next_week = datetime.now(timezone.utc) + timedelta(days=7)
    upcoming_shifts = db.session.query(Shift, User).join(User).filter(
        Shift.start_time >= datetime.now(timezone.utc),
        Shift.start_time <= next_week,
        Shift.status == 'scheduled'
    ).order_by(Shift.start_time).all()
    
    return render_template('admin/shift_management.html',
                         shift_stats=shift_stats,
                         staff_members=staff_members,
                         recent_shifts=recent_shifts,
                         upcoming_shifts=upcoming_shifts)

@app.route('/api/beds/available')
def get_available_beds():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get available beds with ward information
        available_beds = db.session.query(Bed, Ward).join(Ward).filter(
            Bed.status == 'empty'
        ).all()
        
        beds_list = []
        for bed, ward in available_beds:
            beds_list.append({
                'id': bed.id,
                'bed_number': bed.bed_number,
                'ward_name': ward.name,
                'ward_type': ward.type
            })
        
        return jsonify({'beds': beds_list})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Shift Management API Routes
@app.route('/api/shifts/add', methods=['POST'])
def add_shift():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        shift_type = data.get('shift_type')
        
        # Validate required fields
        if not all([staff_id, start_time, end_time, shift_type]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Validate times
        if start_dt >= end_dt:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        # Check for shift conflicts
        existing_shift = Shift.query.filter(
            Shift.user_id == staff_id,
            Shift.status.in_(['scheduled', 'active']),
            db.or_(
                db.and_(Shift.start_time <= start_dt, Shift.end_time > start_dt),
                db.and_(Shift.start_time < end_dt, Shift.end_time >= end_dt),
                db.and_(Shift.start_time >= start_dt, Shift.end_time <= end_dt)
            )
        ).first()
        
        if existing_shift:
            return jsonify({'error': 'Staff member has a conflicting shift'}), 400
        
        # Create new shift
        new_shift = Shift(
            user_id=staff_id,
            start_time=start_dt,
            end_time=end_dt,
            shift_type=shift_type,
            status='scheduled',
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_shift)
        
        # Log activity
        staff_member = User.query.get(staff_id)
        log = ActivityLog(
            user_id=session['user_id'],
            action='create',
            target=f'shift for {staff_member.name} ({shift_type})',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Shift created for {staff_member.name}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/shifts/delete/<int:shift_id>', methods=['DELETE'])
def delete_shift(shift_id):
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        shift = Shift.query.get_or_404(shift_id)
        
        # Check if shift can be deleted (not active)
        if shift.status == 'active':
            return jsonify({'error': 'Cannot delete active shift'}), 400
        
        staff_member = User.query.get(shift.user_id)
        shift_info = f'{staff_member.name} - {shift.shift_type}'
        
        db.session.delete(shift)
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='delete',
            target=f'shift for {shift_info}',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Shift deleted for {staff_member.name}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/shifts/export')
def export_shifts():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import csv
        import io
        from flask import make_response
        
        # Get all shifts with staff info
        shifts_data = db.session.query(Shift, User).join(User).order_by(Shift.start_time.desc()).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Staff Name', 'Shift Type', 'Start Time', 'End Time', 'Status', 'Duration (Hours)', 'Created Date'])
        
        # Write data
        for shift, staff in shifts_data:
            duration = (shift.end_time - shift.start_time).total_seconds() / 3600
            writer.writerow([
                staff.name,
                shift.shift_type,
                shift.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                shift.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                shift.status,
                round(duration, 2),
                shift.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=shifts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # Log activity
        log = ActivityLog(
            user_id=session['user_id'],
            action='export',
            target='shift data',
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_activities')
def recent_activities():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get recent activities with user information
    activities = db.session.query(ActivityLog, User).join(User).order_by(ActivityLog.timestamp.desc()).limit(20).all()
    
    activity_list = []
    for activity, user in activities:
        activity_list.append({
            'id': activity.id,
            'user_name': user.name,
            'user_role': user.role,
            'action': activity.action,
            'target': activity.target,
            'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': get_time_ago(activity.timestamp)
        })
    
    return jsonify({'activities': activity_list})

def get_time_ago(timestamp):
    """Calculate time ago string"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    diff = now - timestamp.replace(tzinfo=timezone.utc)
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# Ward Details API
@app.route('/api/ward-details/<int:ward_id>')
def get_ward_details(ward_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        ward = Ward.query.get(ward_id)
        if not ward:
            return jsonify({'error': 'Ward not found'}), 404
            
        beds = Bed.query.filter_by(ward_id=ward_id).all()
        
        # Get bed statistics
        total_beds = len(beds)
        occupied_beds = len([b for b in beds if b.status == 'occupied'])
        available_beds = len([b for b in beds if b.status == 'empty'])
        cleaning_beds = len([b for b in beds if b.status == 'cleaning'])
        maintenance_beds = len([b for b in beds if b.status == 'maintenance'])
        reserved_beds = len([b for b in beds if b.status == 'reserved'])
        
        # Get patients in this ward
        patients_in_ward = db.session.query(Patient, Bed).join(
            Bed, Patient.id == Bed.patient_id
        ).filter(Bed.ward_id == ward_id, Bed.status == 'occupied').all()
        
        # Format bed details
        bed_details = []
        for bed in beds:
            bed_info = {
                'id': bed.id,
                'bed_number': bed.bed_number,
                'status': bed.status,
                'patient_name': None,
                'oxygen_required': False,
                'oxygen_flow_rate': None,
                'updated_at': bed.updated_at.strftime('%Y-%m-%d %H:%M')
            }
            
            # Add patient info if bed is occupied
            if bed.status == 'occupied' and bed.patient_id:
                patient = Patient.query.get(bed.patient_id)
                if patient:
                    bed_info['patient_name'] = patient.name
                    bed_info['oxygen_required'] = patient.oxygen_required
                    bed_info['oxygen_flow_rate'] = patient.oxygen_flow_rate
            
            bed_details.append(bed_info)
        
        return jsonify({
            'ward': {
                'id': ward.id,
                'name': ward.name,
                'type': ward.type
            },
            'statistics': {
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'available_beds': available_beds,
                'cleaning_beds': cleaning_beds,
                'maintenance_beds': maintenance_beds,
                'reserved_beds': reserved_beds,
                'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            },
            'beds': bed_details,
            'patients': [
                {
                    'name': patient.name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'bed_number': bed.bed_number,
                    'oxygen_required': patient.oxygen_required,
                    'oxygen_flow_rate': patient.oxygen_flow_rate,
                    'admission_date': patient.admitted_on.strftime('%Y-%m-%d') if patient.admitted_on else None
                }
                for patient, bed in patients_in_ward
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error loading ward details: {str(e)}'}), 500

# Bed Details API
@app.route('/api/bed-details/<int:bed_id>')
def get_bed_details(bed_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        bed = Bed.query.get(bed_id)
        if not bed:
            return jsonify({'error': 'Bed not found'}), 404
            
        ward = Ward.query.get(bed.ward_id)
        
        bed_info = {
            'id': bed.id,
            'bed_number': bed.bed_number,
            'status': bed.status,
            'ward': {
                'name': ward.name,
                'type': ward.type
            },
            'updated_at': bed.updated_at.strftime('%Y-%m-%d %H:%M'),
            'patient': None,
            'recent_activities': []
        }
        
        # Add patient info if bed is occupied
        if bed.status == 'occupied' and bed.patient_id:
            patient = Patient.query.get(bed.patient_id)
            if patient:
                bed_info['patient'] = {
                    'id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'oxygen_required': patient.oxygen_required,
                    'oxygen_flow_rate': patient.oxygen_flow_rate,
                    'admission_date': patient.admitted_on.strftime('%Y-%m-%d %H:%M') if patient.admitted_on else None
                }
        
        # Get recent activities for this bed (last 10)
        activities = ActivityLog.query.filter(
            ActivityLog.target.contains(f'bed {bed.bed_number}')
        ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
        
        bed_info['recent_activities'] = [
            {
                'description': f"{activity.action.title()} {activity.target}",
                'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M'),
                'user': activity.user.name if activity.user else 'System'
            }
            for activity in activities
        ]
        
        return jsonify(bed_info)
        
    except Exception as e:
        return jsonify({'error': f'Error loading bed details: {str(e)}'}), 500

# Quick Bed Actions API
@app.route('/api/bed-action/<int:bed_id>', methods=['POST'])
def quick_bed_action(bed_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    action = data.get('action')
    
    bed = Bed.query.get_or_404(bed_id)
    user = User.query.get(session['user_id'])
    
    try:
        if action == 'mark_available':
            if bed.status in ['occupied', 'cleaning']:
                bed.status = 'empty'
                bed.patient_id = None
                bed.updated_at = datetime.now(timezone.utc)
                
                # Log activity
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} marked as available",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                
        elif action == 'mark_cleaning':
            if bed.status in ['occupied', 'empty']:
                old_status = bed.status
                bed.status = 'cleaning'
                if old_status == 'occupied':
                    bed.patient_id = None
                bed.updated_at = datetime.now(timezone.utc)
                
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} marked for cleaning",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                
        elif action == 'cleaning_complete':
            if bed.status == 'cleaning':
                bed.status = 'empty'
                bed.updated_at = datetime.now(timezone.utc)
                
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} cleaning completed",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                
        elif action == 'reserve_bed':
            if bed.status == 'empty':
                bed.status = 'reserved'
                bed.updated_at = datetime.now(timezone.utc)
                
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} reserved",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                
        elif action == 'cancel_reservation':
            if bed.status == 'reserved':
                bed.status = 'empty'
                bed.updated_at = datetime.now(timezone.utc)
                
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} reservation cancelled",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                
        elif action == 'maintenance_complete':
            if bed.status == 'maintenance':
                bed.status = 'empty'
                bed.updated_at = datetime.now(timezone.utc)
                
                activity = ActivityLog(
                    user_id=user.id,
                    action='update',
                    target=f"bed {bed.bed_number} maintenance completed",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(activity)
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Bed {bed.bed_number} updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Patient Details API
@app.route('/api/patient-details/<int:patient_id>')
def get_patient_details(patient_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get current bed and ward
        current_bed = Bed.query.filter_by(patient_id=patient.id, status='occupied').first()
        location = f"{current_bed.ward.name} - Bed {current_bed.bed_number}" if current_bed else "Not Assigned"
        
        # Get latest medical record
        latest_record = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).first()
        
        # Get active medications
        active_medications = Medication.query.filter_by(patient_id=patient.id, status='active').all()
        
        return jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
                'admitted_on': patient.admitted_on.strftime('%Y-%m-%d %H:%M') if patient.admitted_on else None,
                'oxygen_required': patient.oxygen_required,
                'oxygen_flow_rate': patient.oxygen_flow_rate
            },
            'location': location,
            'latest_record': {
                'diagnosis': latest_record.diagnosis,
                'treatment': latest_record.treatment,
                'doctor_name': latest_record.doctor_name,
                'created_at': latest_record.created_at.strftime('%Y-%m-%d %H:%M')
            } if latest_record else None,
            'medications': [
                {
                    'id': med.id,
                    'medication_name': med.medication_name,
                    'dosage': med.dosage,
                    'frequency': med.frequency,
                    'route': med.route,
                    'prescribed_by': med.prescribed_by,
                    'start_date': med.start_date.strftime('%Y-%m-%d'),
                    'notes': med.notes
                }
                for med in active_medications
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error loading patient details: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Hospital Management System on port {port}...")
    print("Database initialized successfully!")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
