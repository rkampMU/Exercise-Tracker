#!/usr/bin/env python3
"""
Script to create or update admin user in Supabase database.
Uses environment variables for credentials.
"""

import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def create_or_update_admin():
    """Create or update admin user in the database"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Hash the password
        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        
        # Check if admin user exists
        response = supabase.table('admin').select('*').eq('username', ADMIN_USERNAME).execute()
        
        if response.data and len(response.data) > 0:
            # Update existing admin
            admin_id = response.data[0]['id']
            supabase.table('admin').update({
                'password_hash': password_hash.decode('utf-8')
            }).eq('id', admin_id).execute()
            
            print(f"✅ Admin user '{ADMIN_USERNAME}' password updated successfully!")
        else:
            # Create new admin
            supabase.table('admin').insert({
                'username': ADMIN_USERNAME,
                'password_hash': password_hash.decode('utf-8')
            }).execute()
            
            print(f"✅ Admin user '{ADMIN_USERNAME}' created successfully!")
        
        print(f"\nAdmin Credentials:")
        print(f"  Username: {ADMIN_USERNAME}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print("\n⚠️  Make sure to change the password in production!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*50)
    print("Admin User Setup")
    print("="*50)
    create_or_update_admin()
