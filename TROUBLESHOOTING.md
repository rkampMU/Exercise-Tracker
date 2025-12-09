````markdown
# 🔧 Troubleshooting: Data Not Saving to Supabase

## FIXED ISSUES

### ✅ Fixed: "Missing required parameter 'digestmod'" Error
**What was wrong**: The app was using werkzeug's `check_password_hash` which doesn't work with bcrypt hashes.
**What I fixed**: Now using `bcrypt` library directly for password verification.

### ✅ Fixed: Data Not Being Saved to Supabase
**What was wrong**: App wasn't making actual calls to Supabase.
**What I fixed**: Completely rewrote `app.py` to make real API calls to Supabase for all operations.

## Current Issue: Verify Your Setup

### Step 1: Verify Supabase Tables Exist

Before the app can save data, your Supabase database needs the correct tables:

1. Go to https://app.supabase.com
2. Select your project: **csgwfqrmpggjapbucvlx**
3. Click **SQL Editor** in the left sidebar
4. Run this query to check if tables exist:

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see:
- admin
- class
- student
- exercise
- completion

### If tables don't exist:

Open `setup_database.sql` in your project and run ALL the SQL queries in the Supabase SQL Editor.

## Step 2: Verify Admin User Exists

Run this query in SQL Editor:

```sql
SELECT * FROM admin;
```

You should see one row with:
- `username`: admin
- `password_hash`: $2b$12$...

If it's empty, run this:

```sql
INSERT INTO admin (username, password_hash) VALUES (
  'admin',
  '$2b$12$BdVxFfPz/4T4n16S8a3uH.WzVOL0PkdVyIa7nJ.O9uX7DxZnzWBmy'
);
```

## Step 3: Test the App

1. Go to http://127.0.0.1:5000
2. Click "Admin Login"
3. Enter:
   - Username: `admin`
   - Password: `admin123`
4. Create a test class

### Check the Console Output

When you create a class, you should see in the terminal:

```
Creating class: My Class - CODE1
✅ Class created with ID: 1
```

If you see ❌ errors instead, copy the full error message.

## Step 4: Verify Data in Supabase

After creating data in the app:

1. Go to https://app.supabase.com
2. Go to **Table Editor**
3. Click on **class** table
4. You should see your new class!

## Common Issues & Solutions

### Issue 1: "Table does not exist"

**Error message**: `Table "class" does not exist`

**Solution**: Run the SQL setup script in Supabase SQL Editor

### Issue 2: "Row-Level Security violation"

**Error message**: `new row violates row-level security policy`

**Solution**: Run this in SQL Editor to disable RLS temporarily:

```sql
ALTER TABLE admin DISABLE ROW LEVEL SECURITY;
ALTER TABLE class DISABLE ROW LEVEL SECURITY;
ALTER TABLE student DISABLE ROW LEVEL SECURITY;
ALTER TABLE exercise DISABLE ROW LEVEL SECURITY;
ALTER TABLE completion DISABLE ROW LEVEL SECURITY;
```

### Issue 3: "Invalid API key"

**Error message**: `Invalid or expired API key`

**Solution**: 
1. Check your `.env` file has `SUPABASE_KEY` set
2. Get the correct key from https://app.supabase.com > Settings > API
3. Use the **anon public** key (not the service role key)

### Issue 4: "CORS error" or "Network error"

**Error message**: `fetch() failed` or `Network error`

**Solution**: Verify your `.env` has the correct Supabase URL (should be https://...)

## Verifying the Fix Works

To confirm data is saving to Supabase:

1. Create a class via the web app
2. Check the Supabase Table Editor
3. Refresh the browser - class should still be there
4. Restart the app - class should STILL be there
5. The data persists! ✅

## Console Logging

The app now logs everything. Look for:

✅ **Success messages**:
- `✅ Connected to Supabase`
- `✅ Class created with ID: ...`
- `✅ Student created with ID: ...`

❌ **Error messages**:
- `❌ Table "class" does not exist`
- `❌ Error creating class: ...`

Share any error messages you see for more help!

## Next Steps

1. Make sure tables exist in Supabase
2. Test creating a class
3. Check the console for ✅ or ❌ messages
4. Verify data appears in Supabase Table Editor
5. Restart the app and confirm data persists

Your data should now be saving to Supabase! 🎉
