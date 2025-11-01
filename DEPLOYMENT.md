# 🚀 Vercel Deployment Guide - Hospital Management Dashboard

This guide will help you deploy your Hospital Management Dashboard to Vercel with all three panels (Admin, Staff, and Patient) working properly.

## 📋 Prerequisites

1. **GitHub Account** - To push your code
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free tier available)
3. **PostgreSQL Database** - For production (recommended: Vercel Postgres or Supabase)

## 🔧 Pre-Deployment Checklist

✅ All files are ready:
- `app.py` - Main Flask application (configured for Vercel)
- `wsgi.py` - WSGI entry point for Vercel
- `models.py` - Database models
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel configuration
- `.vercelignore` - Files to ignore during deployment
- `runtime.txt` - Python version specification
- Templates for all 3 panels (admin, staff, patient)

## 📝 Step-by-Step Deployment

### Step 1: Set Up PostgreSQL Database

**Option A: Vercel Postgres (Recommended)**
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Storage" → "Create Database" → "Postgres"
3. Choose a region close to your users
4. Copy the `DATABASE_URL` connection string

**Option B: Supabase (Free Alternative)**
1. Go to [supabase.com](https://supabase.com) and create a project
2. Go to Project Settings → Database
3. Copy the "Connection String" (URI format)
4. Replace `[YOUR-PASSWORD]` with your actual password

### Step 2: Push to GitHub

```bash
# Navigate to your project directory
cd hospital-dashboard

# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Hospital Dashboard ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/hospital-dashboard.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Vercel

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"

2. **Import Your GitHub Repository**
   - Select "Import Git Repository"
   - Find your `hospital-dashboard` repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset:** Other
   - **Root Directory:** `./` (default)
   - **Build Command:** Leave empty
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements.txt`

4. **Set Environment Variables** (CRITICAL!)
   Click "Environment Variables" and add:

   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-super-secret-random-key-change-this
   VERCEL=1
   ```

   **Important:** Replace with your actual values:
   - `DATABASE_URL`: Your PostgreSQL connection string from Step 1
   - `SECRET_KEY`: Generate a secure random key (e.g., use Python: `python -c "import secrets; print(secrets.token_hex(32))"`)

5. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete (usually 1-2 minutes)

### Step 4: Initialize Database

After deployment succeeds:

1. **Visit the initialization endpoint:**
   ```
   https://your-app-name.vercel.app/init-db-secret-route-12345
   ```
   You should see: `{"message": "Database initialized successfully!"}`

2. **Create the admin user:**
   ```
   https://your-app-name.vercel.app/create-admin-secret-route-67890
   ```
   You should see the admin credentials

3. **IMPORTANT: For security, disable these routes after first use!**
   Comment out or remove these routes from `app.py` after initialization.

### Step 5: Verify All Panels

Visit your deployed app and test all three panels:

1. **Admin Panel** (`/admin/dashboard`)
   - Login: `admin@hospital.com` / `admin123`
   - Test: Dashboard, Bed Management, Patient Management, Oxygen Management, Staff Management, Inventory, Reports

2. **Staff Panel** (`/staff/dashboard`)
   - First create a staff account from admin panel
   - Test: Dashboard, Ward Status, Patients, Oxygen Status, Medical Records, Shifts

3. **Patient Panel** (`/patient/dashboard`)
   - Create a patient account from admin panel
   - Test: Dashboard, Medical Records, Medications, Appointments, Profile

## 🔒 Post-Deployment Security

1. **Change Default Passwords**
   ```sql
   -- Login to admin panel and change the password
   -- Or update directly in database
   ```

2. **Remove Initialization Routes**
   - Comment out `/init-db-secret-route-12345` and `/create-admin-secret-route-67890` in `app.py`
   - Redeploy to Vercel

3. **Enable Custom Domain** (Optional)
   - In Vercel Dashboard → Settings → Domains
   - Add your custom domain

## 📊 Database Seeding (Optional)

To add sample data for testing:

1. Create a seed script or use the admin panel to:
   - Add Wards (General, ICU, Emergency, Pediatric, etc.)
   - Add Beds to each ward
   - Add sample patients
   - Configure oxygen inventory
   - Add staff members

## 🐛 Troubleshooting

### Issue: Database Connection Error
- **Solution:** Verify `DATABASE_URL` environment variable is correct
- Check if your PostgreSQL database is accessible

### Issue: 500 Internal Server Error
- **Solution:** Check Vercel logs (Dashboard → Your Project → Logs)
- Verify all environment variables are set

### Issue: Tables Not Created
- **Solution:** Visit `/init-db-secret-route-12345` again
- Check database permissions

### Issue: Static Files Not Loading
- **Solution:** Vercel automatically serves static files from `/static`
- Check that TailwindCSS CDN is accessible

## 🔄 Continuous Deployment

Vercel automatically redeploys when you push to your GitHub repository:

```bash
# Make changes to your code
git add .
git commit -m "Your commit message"
git push origin main
# Vercel will automatically deploy!
```

## 📱 All Panel Features Verified

### ✅ Admin Panel Features
- [x] Dashboard with statistics
- [x] Bed management with all status types
- [x] Patient admission/discharge
- [x] Oxygen inventory management
- [x] Staff management and activity logs
- [x] Inventory management with expiry tracking
- [x] Comprehensive reports
- [x] Notifications system
- [x] Shift management
- [x] Patient account creation

### ✅ Staff Panel Features
- [x] Dashboard with bed overview
- [x] Ward status and occupancy
- [x] Patient management
- [x] Oxygen status tracking
- [x] Medical records access
- [x] Shift schedule
- [x] Notifications

### ✅ Patient Panel Features
- [x] Personal dashboard
- [x] Medical records view
- [x] Current and past medications
- [x] Appointments (upcoming and past)
- [x] Profile information
- [x] Days admitted tracking

## 🌐 Access URLs

After deployment:
- **Production URL:** `https://your-app-name.vercel.app`
- **Admin Panel:** `https://your-app-name.vercel.app/admin/dashboard`
- **Staff Panel:** `https://your-app-name.vercel.app/staff/dashboard`
- **Patient Panel:** `https://your-app-name.vercel.app/patient/dashboard`

## 💡 Tips

1. **Always use HTTPS** - Vercel provides free SSL certificates
2. **Monitor your database** - Keep an eye on storage limits
3. **Regular backups** - Set up automatic backups for your PostgreSQL database
4. **Performance** - Monitor response times in Vercel Analytics
5. **Environment Variables** - Never commit sensitive data to Git

## 📞 Support

If you encounter any issues:
1. Check Vercel deployment logs
2. Verify database connection
3. Ensure all environment variables are set correctly
4. Review the application logs for specific errors

---

**🎉 Congratulations! Your Hospital Management Dashboard is now live on Vercel with all three panels working!**
