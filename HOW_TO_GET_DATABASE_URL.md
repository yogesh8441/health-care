# 🔍 How to Get DATABASE_URL from Neon

## Step-by-Step with Screenshots

### After Creating Your Project on Neon.tech:

---

## ✅ Method 1: Right After Project Creation

**When you click "Create Project", Neon will show a page with:**

1. **Look for a section called "Connection Details"** or **"Quick Start"**

2. You'll see a box with connection strings. Look for one that says:
   - **"Connection string"** or
   - **"Database URL"** or
   - **"Postgres connection string"**

3. It will look like this:
   ```
   postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb
   ```

4. **Click the COPY button** next to it (usually a 📋 icon)

---

## ✅ Method 2: From Dashboard

If you missed it, go to your Neon Dashboard:

1. **Click on your project** (hospital-db)

2. **Look for "Connection Details"** tab or panel on the left/right side

3. You'll see something like:

   ```
   ┌─────────────────────────────────────────────────┐
   │  Connection string                              │
   │  ┌────────────────────────────────────────┐    │
   │  │ postgresql://user:pass@ep-xxx.aws...   │ 📋 │
   │  └────────────────────────────────────────┘    │
   └─────────────────────────────────────────────────┘
   ```

4. **Click the copy icon** 📋

---

## ✅ Method 3: From "Dashboard" → "Connection Details"

1. In Neon Dashboard, click **"Dashboard"** (top menu)
2. Click your project name: **hospital-db**
3. Look for **"Connection Details"** section
4. Find the dropdown that says **"Connection string"** or **"URI"**
5. Make sure it's set to **"Pooled connection"** (recommended)
6. Copy the string

---

## 📝 What the URL Looks Like

Your DATABASE_URL will look like ONE of these formats:

**Format 1 (Most Common):**
```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb
```

**Format 2:**
```
postgres://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech:5432/neondb
```

**Key parts:**
- Starts with: `postgresql://` or `postgres://`
- Contains: `@ep-` (Neon's signature)
- Ends with: `.aws.neon.tech/database_name`

---

## 🎯 Quick Visual Guide

```
Neon Dashboard
├── Your Projects
│   └── hospital-db  ← Click here
│       ├── Dashboard
│       ├── Connection Details  ← Look here!
│       │   └── Connection string: postgresql://...  ← COPY THIS!
│       ├── Tables
│       └── Settings
```

---

## ⚠️ Important Tips

1. **Use "Pooled connection"** if you see that option (better for Vercel)
2. **Copy the ENTIRE string** - don't miss the beginning or end
3. **Keep it secret** - don't share it publicly
4. The string includes your password - that's normal and correct

---

## 🆘 Still Can't Find It?

Try this:

1. Go to: https://console.neon.tech
2. Click your project: **hospital-db**
3. Look at the **RIGHT SIDE** of the screen
4. You should see a panel with **"Connection Details"**
5. Click **"Show connection string"** if it's hidden
6. Copy the **entire string**

---

## ✅ Once You Have It

Paste it in Vercel like this:

```
Name: DATABASE_URL
Value: postgresql://your_copied_string_here
```

Then continue with the other 2 environment variables!

---

**Need more help?** Tell me what you see on your Neon screen and I'll guide you!
