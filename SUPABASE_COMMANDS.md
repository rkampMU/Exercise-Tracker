# Quick Setup - Copy & Paste SQL Commands

## If you're having issues with Supabase setup, follow these exact steps:

### Step 1: Login to Supabase

Go to: https://app.supabase.com
- Select project: **csgwfqrmpggjapbucvlx**
- Click **SQL Editor** in the left sidebar

### Step 2: Run Each Command

Create a **new query** and run these commands ONE AT A TIME:

#### Command 1: Check if tables exist
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

**Expected result**: You should see `admin`, `class`, `student`, `exercise`, `completion`

If you DON'T see these tables, continue to Command 3.

#### Command 2: Check admin user
```sql
SELECT * FROM admin;
```

**Expected result**: One row with `username = admin`

If empty, run Command 4.

#### Command 3: Create all tables (RUN ONLY IF TABLES DON'T EXIST)

Copy the entire contents from:
`/Users/familymac/ClassTracker/project/setup_database.sql`

And paste it into a new SQL query. Then click **Run**.

#### Command 4: Insert admin user (RUN ONLY IF ADMIN DOESN'T EXIST)
```sql
INSERT INTO admin (username, password_hash) VALUES (
  'admin',
  '$2b$12$BdVxFfPz/4T4n16S8a3uH.WzVOL0PkdVyIa7nJ.O9uX7DxZnzWBmy'
) ON CONFLICT (username) DO NOTHING;
```

#### Command 5: Disable RLS (if you get permission errors)
```sql
ALTER TABLE admin DISABLE ROW LEVEL SECURITY;
ALTER TABLE class DISABLE ROW LEVEL SECURITY;
ALTER TABLE student DISABLE ROW LEVEL SECURITY;
ALTER TABLE exercise DISABLE ROW LEVEL SECURITY;
ALTER TABLE completion DISABLE ROW LEVEL SECURITY;
```

### Step 3: Verify Everything

In Supabase:
1. Go to **Table Editor**
2. Click **admin** - should have 1 row with your login
3. Click **class** - should be empty (you'll add classes via the app)
4. Repeat for other tables

### Step 4: Test the App

1. Go to http://127.0.0.1:5000/admin/login
2. Login with:
   - Username: **admin**
   - Password: **admin123**
3. Create a test class
4. Go back to Supabase Table Editor → **class**
5. Your new class should appear! ✅

## If something goes wrong:

### Error: "Table already exists"
→ This is fine! It means the table is already created. Skip that command.

### Error: "Duplicate key value"
→ Admin user already exists. Skip that command.

### Error: "Column does not exist"
→ The table structure is wrong. Delete the tables and run the full setup script again.

### No data appears in Supabase
→ Check app console for errors
→ Make sure RLS is disabled
→ Verify `.env` file has correct Supabase credentials

## Success Signs ✅

You'll know it's working when:
1. You can login to the app with admin/admin123
2. When you create a class, it appears in Supabase Table Editor
3. When you restart the app, the class is still there
4. You can see all your data in Supabase dashboard

That's it! Your Supabase integration is complete! 🎉
