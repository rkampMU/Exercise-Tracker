# ClassTracker - Supabase Setup Guide

## Step 1: Create a Supabase Project

1. Go to https://app.supabase.com/
2. Sign up/Log in with your email or GitHub account
3. Click "New Project"
4. Fill in the details:
   - **Name**: ClassTracker (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your location
5. Click "Create new project" (wait 2-3 minutes for setup)

## Step 2: Get Your API Keys

1. In the Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (under "Your API")
   - **anon public** (under "Project API keys")

## Step 3: Create Database Tables

In the Supabase dashboard, go to **SQL Editor** and run these queries one by one:

### Table 1: Admin Users
```sql
CREATE TABLE admin (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table 2: Classes
```sql
CREATE TABLE class (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table 3: Students
```sql
CREATE TABLE student (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  class_id BIGINT NOT NULL REFERENCES class(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX student_class_id_idx ON student(class_id);
```

### Table 4: Exercises
```sql
CREATE TABLE exercise (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name TEXT NOT NULL,
  class_id BIGINT NOT NULL REFERENCES class(id) ON DELETE CASCADE,
  qr_token TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX exercise_class_id_idx ON exercise(class_id);
CREATE INDEX exercise_qr_token_idx ON exercise(qr_token);
```

### Table 5: Completions
```sql
CREATE TABLE completion (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  student_id BIGINT NOT NULL REFERENCES student(id) ON DELETE CASCADE,
  exercise_id BIGINT NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
  student_email TEXT NOT NULL,
  completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX completion_student_id_idx ON completion(student_id);
CREATE INDEX completion_exercise_id_idx ON completion(exercise_id);
```

## Step 4: Create Admin User in Database

In the **SQL Editor**, insert the admin user:

```sql
INSERT INTO admin (username, password_hash) VALUES (
  'admin',
  '$2b$12$BdVxFfPz/4T4n16S8a3uH.WzVOL0PkdVyIa7nJ.O9uX7DxZnzWBmy'
);
```

(This hash is for password: admin123)

## Step 5: Update .env File

In your project directory, create a `.env` file:

```bash
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_anon_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

Replace the values with those from Step 2.

## Step 6: Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Step 7: Run Your App

```bash
python3 app.py
```

Your app should now be connected to Supabase! 🚀

## Troubleshooting

**Issue**: "Missing Supabase credentials"
- Make sure your `.env` file is in the project root directory
- Check that SUPABASE_URL and SUPABASE_KEY are set correctly

**Issue**: "Table does not exist"
- Make sure all SQL queries were executed in the Supabase SQL Editor
- Check table names are lowercase

**Issue**: "Connection refused"
- Check your internet connection
- Verify your Supabase project is active
- Make sure the Project URL is correct

## Data Persistence

Once connected to Supabase, your data will persist between app restarts. You can view and manage all data in the Supabase dashboard under the **Table Editor** tab.
