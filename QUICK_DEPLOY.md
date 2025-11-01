# ⚡ Quick Deployment Checklist

Use this quick reference for deploying to Vercel.

## ✅ Pre-Flight Check

### Files Ready
- [x] `app.py` - Main application
- [x] `wsgi.py` - WSGI entry point
- [x] `models.py` - Database models
- [x] `requirements.txt` - Dependencies
- [x] `vercel.json` - Vercel config
- [x] `.vercelignore` - Ignore patterns
- [x] `runtime.txt` - Python version
- [x] `.gitignore` - Git ignore patterns

### All Panels Configured
- [x] **Admin Panel** - 10 templates (dashboard, bed_management, patients, oxygen_management, staff_management, inventory, reports, notifications, shift_management, prescriptions)
- [x] **Staff Panel** - 7 templates (dashboard, ward_status, patients, oxygen_status, medical_records, shifts, notifications)
- [x] **Patient Panel** - 5 templates (dashboard, medical_records, medications, appointments, profile)

## 🚀 5-Minute Deploy

### 1. Setup PostgreSQL (2 min)
```bash
# Option A: Vercel Postgres
# Go to vercel.com → Storage → Create Database → Postgres
# Copy DATABASE_URL

# Option B: Supabase
# Go to supabase.com → New Project → Settings → Database
# Copy Connection String
```

### 2. Push to GitHub (1 min)
```bash
cd hospital-dashboard
git init
git add .
git commit -m "Deploy: Hospital Dashboard"
git remote add origin https://github.com/YOUR_USERNAME/hospital-dashboard.git
git push -u origin main
```

### 3. Deploy on Vercel (2 min)
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your repository
3. Set Environment Variables:
   ```
   DATABASE_URL=your_postgres_url_here
   SECRET_KEY=generate_random_32_char_key
   VERCEL=1
   ```
4. Click "Deploy"

### 4. Initialize Database (30 sec)
```bash
# Visit these URLs (replace with your actual URL):
https://your-app.vercel.app/init-db-secret-route-12345
https://your-app.vercel.app/create-admin-secret-route-67890

# You'll get the admin credentials
```

### 5. Test All Panels (1 min)
- ✅ Admin: `https://your-app.vercel.app/login` → `admin@hospital.com` / `admin123`
- ✅ Staff: Create staff from admin panel → login
- ✅ Patient: Create patient from admin panel → login

## 🔐 Default Credentials

### Admin
- Email: `admin@hospital.com`
- Password: `admin123`
- **⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN**

## 🎯 Post-Deployment

1. **Change admin password**
2. **Remove init routes** (comment out in `app.py` lines 97-135)
3. **Add sample data** via admin panel:
   - Create Wards
   - Add Beds to each ward
   - Add Staff members
   - Configure Oxygen inventory

## 📊 Panel Routes

### Admin Panel Routes
- `/admin/dashboard` - Main dashboard
- `/admin/bed-management` - Bed management
- `/admin/patients` - Patient management
- `/admin/oxygen-management` - Oxygen inventory
- `/admin/staff-management` - Staff & user management
- `/admin/inventory` - Medical inventory
- `/admin/reports` - Reports & analytics
- `/admin/notifications` - System notifications
- `/admin/shift-management` - Staff shifts
- `/admin/prescriptions` - Patient prescriptions

### Staff Panel Routes
- `/staff/dashboard` - Staff dashboard
- `/staff/ward-status` - Ward occupancy status
- `/staff/patients` - Active patients list
- `/staff/oxygen-status` - Oxygen levels
- `/staff/medical-records` - Medical records
- `/staff/shifts` - My shifts
- `/staff/notifications` - My notifications

### Patient Panel Routes
- `/patient/dashboard` - Patient dashboard
- `/patient/medical-records` - My medical records
- `/patient/medications` - My medications
- `/patient/appointments` - My appointments
- `/patient/profile` - My profile

## 🐛 Quick Fixes

### Can't connect to database?
```bash
# Verify DATABASE_URL in Vercel:
# Dashboard → Your Project → Settings → Environment Variables
```

### 500 Error?
```bash
# Check logs:
# Vercel Dashboard → Your Project → Logs
```

### Tables not created?
```bash
# Re-visit:
https://your-app.vercel.app/init-db-secret-route-12345
```

## 📱 Mobile Access

All three panels are fully responsive and work on:
- 📱 Mobile (320px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)

## ✨ What's Working

### Admin Panel ✅
- Dashboard with real-time stats
- Complete bed management (all statuses)
- Patient admission/discharge
- Oxygen inventory tracking
- Staff & user management
- Medical inventory with expiry alerts
- Comprehensive reports
- Notification system
- Shift scheduling
- Prescription management
- Activity logs

### Staff Panel ✅
- Real-time bed status dashboard
- Ward occupancy overview
- Patient list with details
- Oxygen level monitoring
- Medical records access
- Personal shift schedule
- Staff notifications
- Quick patient actions

### Patient Panel ✅
- Personal health dashboard
- Medical records history
- Current & past medications
- Appointment scheduling
- Profile management
- Days admitted tracking
- Emergency contact info

---

**Ready to deploy? Follow the steps above and you'll be live in 5 minutes! 🚀**

For detailed instructions, see `DEPLOYMENT.md`
