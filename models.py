from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'admin', 'staff', or 'patient'
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True, index=True)  # Link to patient record if role is 'patient'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Ward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'general', 'icu', 'emergency', etc.
    beds = db.relationship('Bed', backref='ward', lazy=True)

class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False, index=True)
    bed_number = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), default='empty', index=True)  # 'empty', 'occupied', 'reserved', 'cleaning', 'maintenance'
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False, index=True)
    gender = db.Column(db.String(10), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    admitted_on = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    discharged_on = db.Column(db.DateTime, nullable=True, index=True)
    oxygen_required = db.Column(db.Boolean, default=False, index=True)
    oxygen_flow_rate = db.Column(db.Float, nullable=True)
    beds = db.relationship('Bed', backref='patient', lazy=True)
    user_account = db.relationship('User', backref='patient_record', lazy=True)

class Oxygen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cylinders_in_stock = db.Column(db.Integer, default=0)
    cylinders_in_use = db.Column(db.Integer, default=0)
    next_refill_date = db.Column(db.DateTime, nullable=True)
    last_refill_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user = db.relationship('User', backref='activities', lazy=True)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # 'active', 'completed', 'cancelled'
    discharge_date = db.Column(db.DateTime, nullable=True)
    discharge_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
    patient = db.relationship('Patient', backref='medical_records', lazy=True)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # '500mg', '10ml', etc.
    frequency = db.Column(db.String(50), nullable=False)  # 'twice daily', 'every 6 hours', etc.
    route = db.Column(db.String(20), nullable=False)  # 'oral', 'IV', 'injection', etc.
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # 'active', 'completed', 'discontinued'
    prescribed_by = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
    patient = db.relationship('Patient', backref='medications', lazy=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'medication', 'equipment', 'supplies'
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=10)
    unit = db.Column(db.String(20), nullable=False)  # 'pieces', 'bottles', 'boxes'
    cost_per_unit = db.Column(db.Float, nullable=True)
    supplier = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    last_restocked = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    shift_type = db.Column(db.String(20), nullable=False)  # 'morning', 'afternoon', 'night'
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled', index=True)  # 'scheduled', 'active', 'completed', 'missed'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user = db.relationship('User', backref='shifts', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)  # None for system-wide
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'info', 'warning', 'error', 'success'
    priority = db.Column(db.String(10), default='normal')  # 'low', 'normal', 'high', 'critical'
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user = db.relationship('User', backref='notifications', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)  # 'consultation', 'follow_up', 'surgery'
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='scheduled', index=True)  # 'scheduled', 'completed', 'cancelled', 'no_show'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    patient = db.relationship('Patient', backref='appointments', lazy=True)

class EmergencyAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'code_blue', 'fire', 'evacuation', 'security'
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(10), nullable=False)  # 'low', 'medium', 'high', 'critical'
    status = db.Column(db.String(20), default='active')  # 'active', 'resolved', 'cancelled'
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    reporter = db.relationship('User', foreign_keys=[reported_by], backref='reported_alerts', lazy=True)
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts', lazy=True)
