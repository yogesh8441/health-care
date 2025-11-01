# Patient Dashboard Feature

## Overview

The Patient Dashboard is a comprehensive feature that allows patients to access their medical information through a secure web interface. Patients can view their medical records, current medications, appointments, and personal information.

## Features

### 🏥 Patient Dashboard
- **Overview Statistics**: Current medications count, medical records, upcoming appointments, days admitted
- **Current Treatment**: View active medications with dosage, frequency, and prescribing doctor
- **Medical Records**: Access to complete medical history with diagnosis and treatment information
- **Patient Information**: Personal details, ward assignment, and medical status

### 💊 Medications Management
- **Active Medications**: Current prescriptions with detailed information
- **Medication History**: Completed and discontinued medications
- **Prescription Details**: Dosage, frequency, route, prescribing doctor, and notes

### 📅 Appointments
- **Upcoming Appointments**: Scheduled appointments with doctors
- **Appointment History**: Past appointments with status and notes
- **Appointment Details**: Doctor name, type, date, time, and duration

### 👤 Patient Profile
- **Personal Information**: Name, age, gender, contact details
- **Medical Information**: Blood group, allergies, medical history, oxygen requirements
- **Account Information**: Email, account creation date, patient ID

## Technical Implementation

### Database Changes

#### User Model Updates
```python
class User(db.Model):
    # ... existing fields ...
    role = db.Column(db.String(20), nullable=False)  # Now supports 'patient' role
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
```

#### Patient Model Enhancements
```python
class Patient(db.Model):
    # ... existing fields ...
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    user_account = db.relationship('User', backref='patient_record', lazy=True)
```

### New Routes

#### Patient Dashboard Routes
- `GET /patient/dashboard` - Main patient dashboard
- `GET /patient/medical-records` - Medical records page
- `GET /patient/medications` - Medications page
- `GET /patient/appointments` - Appointments page
- `GET /patient/profile` - Patient profile page

#### API Endpoints
- `GET /api/patient/dashboard-stats` - Dashboard statistics
- `POST /admin/create-patient-account` - Create patient account (admin only)

### Authentication & Authorization

The system now supports three user roles:
1. **Admin** - Full system access
2. **Staff** - Hospital staff access
3. **Patient** - Patient-specific access

Patient authentication is handled through the existing login system with role-based redirects.

## Setup Instructions

### 1. Database Migration

Run the database migration script to add new fields:

```bash
python migrate_patient_fields.py
```

### 2. Create Patient Accounts

Use the account creation script to create test patient accounts:

```bash
python create_patient_accounts.py
```

This will create accounts for the first 5 patients with:
- **Email**: `patient.name@patient.hospital.com`
- **Password**: `patient123`

### 3. Manual Account Creation

Admins can create patient accounts through the API:

```javascript
POST /admin/create-patient-account
{
    "patient_id": 1,
    "email": "john.doe@email.com",
    "password": "custom_password"  // Optional, defaults to "patient123"
}
```

## Usage

### For Patients

1. **Login**: Use the provided email and password
2. **Dashboard**: View overview of medical information
3. **Navigation**: Use the sidebar to access different sections
4. **Medical Records**: View detailed medical history
5. **Medications**: Check current and past medications
6. **Appointments**: See upcoming and past appointments
7. **Profile**: View and verify personal information

### For Administrators

1. **Create Accounts**: Use the admin panel or API to create patient accounts
2. **Manage Patients**: Existing patient management features remain unchanged
3. **Monitor Access**: Patient logins are logged in the activity log

## Security Features

- **Role-based Access Control**: Patients can only access their own data
- **Session Management**: Secure session handling with automatic logout
- **Data Privacy**: Patients can only view, not modify, their medical records
- **Audit Trail**: All patient logins and activities are logged

## UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern Interface**: Clean, medical-themed design using Tailwind CSS
- **Intuitive Navigation**: Easy-to-use sidebar navigation
- **Visual Indicators**: Color-coded status indicators and badges
- **Quick Actions**: Easy access to frequently used features

## File Structure

```
templates/patient/
├── dashboard.html          # Main patient dashboard
├── medical_records.html    # Medical records page
├── medications.html        # Medications page
├── appointments.html       # Appointments page
└── profile.html           # Patient profile page

scripts/
├── migrate_patient_fields.py      # Database migration
└── create_patient_accounts.py     # Account creation utility
```

## Testing

### Test Accounts

After running the setup scripts, you can test with:

- **Email**: `[patient.name]@patient.hospital.com`
- **Password**: `patient123`

### Test Scenarios

1. **Login as Patient**: Verify dashboard loads correctly
2. **View Medical Records**: Check medical history display
3. **Check Medications**: Verify current and past medications
4. **View Appointments**: Test appointment scheduling display
5. **Profile Information**: Verify personal information display

## Future Enhancements

### Planned Features
- **Appointment Booking**: Allow patients to book appointments
- **Medication Reminders**: Email/SMS reminders for medications
- **Test Results**: View lab and diagnostic test results
- **Billing Information**: Access to billing and insurance information
- **Health Tracking**: Basic health metrics tracking
- **Communication**: Secure messaging with healthcare providers

### Technical Improvements
- **Mobile App**: Native mobile application
- **Push Notifications**: Real-time notifications
- **Data Export**: Export medical records to PDF
- **Multi-language Support**: Internationalization
- **Advanced Security**: Two-factor authentication

## Troubleshooting

### Common Issues

1. **Login Issues**
   - Verify patient account exists
   - Check email and password
   - Ensure patient_id is correctly linked

2. **Missing Data**
   - Run database migration script
   - Verify patient records exist
   - Check foreign key relationships

3. **Template Errors**
   - Ensure all patient templates are in place
   - Verify Tailwind CSS is loading
   - Check template block structure

### Support

For technical support or feature requests, please refer to the main project documentation or contact the development team.

## Changelog

### Version 1.0.0
- Initial patient dashboard implementation
- Basic medical information display
- Patient authentication system
- Responsive UI design
- Database schema updates

---

**Note**: This feature integrates seamlessly with the existing hospital management system while providing patients with secure access to their medical information.
