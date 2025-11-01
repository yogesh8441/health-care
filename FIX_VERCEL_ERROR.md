# 🔧 FIX VERCEL 500 ERROR

Your app deployed but crashes because environment variables are missing!

## STEP-BY-STEP FIX:

### Step 1: Go to Your Project Settings
1. On the Vercel page you're on, look for a button that says **"Go to Dashboard"** or **"View Project"**
2. OR go to: https://vercel.com/dashboard
3. Find your project: **"health-care"**
4. Click on it

### Step 2: Go to Settings
1. Click **"Settings"** tab (at the top)
2. In the left sidebar, click **"Environment Variables"**

### Step 3: Add The 3 Variables

Click **"Add"** for each variable:

**Variable 1:**
```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_mojRiqV7dP1Y@ep-dry-queen-adnlw7zw-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
Environment: Production, Preview, Development (select all)
```

**Variable 2:**
```
Key: SECRET_KEY
Value: 99044dacd9c65a31a306969e52a4dcba7ace5eb603f193d2f77c4e79c116b029
Environment: Production, Preview, Development (select all)
```

**Variable 3:**
```
Key: VERCEL
Value: 1
Environment: Production, Preview, Development (select all)
```

### Step 4: Redeploy
1. After adding all 3 variables, go to **"Deployments"** tab
2. Click the **"..."** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Wait 1-2 minutes

### Step 5: Test Again
Your app should now work!

═══════════════════════════════════════════════════════════════════════════

## OR: Easier Way - Let Me Help!

Tell me your Vercel project URL and I'll give you exact steps!
