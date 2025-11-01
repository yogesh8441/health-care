#!/usr/bin/env python3
"""
Deployment Verification Script for Hospital Management Dashboard
Verifies all panels and routes are accessible after deployment
"""

import os
import sys

def verify_files():
    """Verify all required files exist"""
    print("🔍 Verifying deployment files...")
    
    required_files = [
        'app.py',
        'wsgi.py',
        'models.py',
        'requirements.txt',
        'vercel.json',
        '.vercelignore',
        'runtime.txt',
        '.gitignore'
    ]
    
    required_dirs = [
        'templates/admin',
        'templates/staff',
        'templates/patient',
        'static/css',
        'static/js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    missing_dirs = []
    for dir in required_dirs:
        if not os.path.isdir(dir):
            missing_dirs.append(dir)
    
    if missing_files or missing_dirs:
        print("❌ Missing files or directories:")
        for f in missing_files:
            print(f"   - {f}")
        for d in missing_dirs:
            print(f"   - {d}/")
        return False
    
    print("✅ All required files and directories exist")
    return True

def verify_templates():
    """Verify all template files exist"""
    print("\n🔍 Verifying template files...")
    
    admin_templates = [
        'dashboard.html', 'bed_management.html', 'patients.html',
        'oxygen_management.html', 'staff_management.html', 'inventory.html',
        'reports.html', 'notifications.html', 'shift_management.html',
        'prescriptions.html'
    ]
    
    staff_templates = [
        'dashboard.html', 'ward_status.html', 'patients.html',
        'oxygen_status.html', 'medical_records.html', 'shifts.html',
        'notifications.html'
    ]
    
    patient_templates = [
        'dashboard.html', 'medical_records.html', 'medications.html',
        'appointments.html', 'profile.html'
    ]
    
    missing = []
    
    for template in admin_templates:
        path = f'templates/admin/{template}'
        if not os.path.exists(path):
            missing.append(f'admin/{template}')
    
    for template in staff_templates:
        path = f'templates/staff/{template}'
        if not os.path.exists(path):
            missing.append(f'staff/{template}')
    
    for template in patient_templates:
        path = f'templates/patient/{template}'
        if not os.path.exists(path):
            missing.append(f'patient/{template}')
    
    if missing:
        print("❌ Missing templates:")
        for t in missing:
            print(f"   - templates/{t}")
        return False
    
    print("✅ All template files exist")
    print(f"   - Admin: {len(admin_templates)} templates")
    print(f"   - Staff: {len(staff_templates)} templates")
    print(f"   - Patient: {len(patient_templates)} templates")
    return True

def verify_routes():
    """Verify routes are defined in app.py"""
    print("\n🔍 Verifying routes in app.py...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    admin_routes = [
        '/admin/dashboard',
        '/admin/bed-management',
        '/admin/patients',
        '/admin/oxygen-management',
        '/admin/staff-management',
        '/admin/inventory',
        '/admin/reports',
        '/admin/notifications',
        '/admin/shift-management',
        '/admin/prescriptions'
    ]
    
    staff_routes = [
        '/staff/dashboard',
        '/staff/ward-status',
        '/staff/patients',
        '/staff/oxygen-status',
        '/staff/medical-records',
        '/staff/shifts',
        '/staff/notifications'
    ]
    
    patient_routes = [
        '/patient/dashboard',
        '/patient/medical-records',
        '/patient/medications',
        '/patient/appointments',
        '/patient/profile'
    ]
    
    missing_routes = []
    
    for route in admin_routes + staff_routes + patient_routes:
        if f"@app.route('{route}')" not in content:
            missing_routes.append(route)
    
    if missing_routes:
        print("❌ Missing routes:")
        for r in missing_routes:
            print(f"   - {r}")
        return False
    
    print("✅ All routes are defined")
    print(f"   - Admin: {len(admin_routes)} routes")
    print(f"   - Staff: {len(staff_routes)} routes")
    print(f"   - Patient: {len(patient_routes)} routes")
    return True

def verify_dependencies():
    """Verify requirements.txt has all dependencies"""
    print("\n🔍 Verifying dependencies...")
    
    with open('requirements.txt', 'r') as f:
        deps = f.read()
    
    required_deps = [
        'Flask',
        'Flask-SQLAlchemy',
        'Werkzeug',
        'python-dotenv',
        'gunicorn',
        'psycopg2-binary',
        'SQLAlchemy'
    ]
    
    missing = []
    for dep in required_deps:
        if dep not in deps:
            missing.append(dep)
    
    if missing:
        print("❌ Missing dependencies:")
        for d in missing:
            print(f"   - {d}")
        return False
    
    print("✅ All dependencies are listed")
    return True

def verify_vercel_config():
    """Verify Vercel configuration"""
    print("\n🔍 Verifying Vercel configuration...")
    
    import json
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        if 'builds' not in config:
            print("❌ Missing 'builds' in vercel.json")
            return False
        
        if 'routes' not in config:
            print("❌ Missing 'routes' in vercel.json")
            return False
        
        # Check for wsgi.py as entry point
        builds = config.get('builds', [])
        if not any('wsgi.py' in str(build.get('src', '')) for build in builds):
            print("❌ wsgi.py not configured as build source")
            return False
        
        print("✅ Vercel configuration is valid")
        return True
    
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def print_deployment_summary():
    """Print deployment summary"""
    print("\n" + "="*60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("="*60)
    
    all_checks = [
        verify_files(),
        verify_templates(),
        verify_routes(),
        verify_dependencies(),
        verify_vercel_config()
    ]
    
    if all(all_checks):
        print("\n✅ ALL CHECKS PASSED!")
        print("\n🚀 Your application is ready for Vercel deployment!")
        print("\n📝 Next Steps:")
        print("   1. Push to GitHub: git push origin main")
        print("   2. Import to Vercel: vercel.com/new")
        print("   3. Set environment variables (DATABASE_URL, SECRET_KEY)")
        print("   4. Deploy and initialize database")
        print("\n📖 See DEPLOYMENT.md for detailed instructions")
        print("⚡ See QUICK_DEPLOY.md for quick reference")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("\n⚠️  Please fix the issues above before deploying")
        return 1

if __name__ == '__main__':
    sys.exit(print_deployment_summary())
