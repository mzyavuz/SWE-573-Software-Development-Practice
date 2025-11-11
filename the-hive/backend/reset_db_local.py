#!/usr/bin/env python3
"""
Database Reset Script for The Hive
Drops all tables and recreates them with the latest schema.
USE WITH CAUTION - This will delete ALL data!
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Get database connection using environment variables."""
    # Check for DigitalOcean DATABASE_URL first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    
    # Fallback to docker-compose style environment variables
    # Note: Use 'db' when running inside Docker, 'localhost' when running from host machine
    host = os.getenv('POSTGRES_HOST', 'localhost')  # Default to localhost for local execution
    database = os.getenv('POSTGRES_DB', 'mydatabase')
    user = os.getenv('POSTGRES_USER', 'myuser')
    password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
    port = os.getenv('POSTGRES_PORT', '5432')
    
    print(f"Connecting to: {user}@{host}:{port}/{database}")
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        cursor_factory=RealDictCursor
    )

def drop_all_tables(cursor):
    """Drop all tables in the correct order (respecting foreign keys)."""
    print("\n🗑️  Dropping all tables...")
    
    tables = [
        'messages',
        'service_progress',
        'service_applications',
        'service_availability',
        'service_tags',
        'services',
        'password_reset_tokens',
        'email_verifications',
        'tags',
        'users'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"   ✅ Dropped table: {table}")
        except Exception as e:
            print(f"   ⚠️  Error dropping {table}: {e}")
    
    print("\n✅ All tables dropped successfully!")

def main():
    """Main function to reset the database."""
    print("\n" + "="*60)
    print("THE HIVE - DATABASE RESET SCRIPT")
    print("="*60)
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("   All users, services, messages, and progress will be lost.")
    print("\n" + "="*60)
    
    # Ask for confirmation
    response = input("\nAre you ABSOLUTELY SURE you want to continue? (type 'DELETE' to confirm): ")
    
    if response != 'DELETE':
        print("\n❌ Reset cancelled. No changes made.")
        sys.exit(0)
    
    try:
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✅ Connected successfully")
        
        # Drop all tables
        drop_all_tables(cursor)
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*60)
        print("DATABASE RESET COMPLETE")
        print("="*60)
        print("\n📝 Next steps:")
        print("   1. Restart your application")
        print("   2. The app.py init_db() function will recreate all tables")
        print("   3. Database will be fresh with no data")
        print("\n💡 For DigitalOcean:")
        print("   - Go to Apps → Your App → Actions → Force Rebuild and Deploy")
        print("   - Or wait for automatic deployment if you push code changes")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()