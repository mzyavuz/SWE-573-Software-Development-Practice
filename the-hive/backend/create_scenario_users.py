def mark_scenario_users_verified():
    """Directly set is_verified=True for all scenario users in the users table."""
    emails = [
        'alex.chen@hive.com.tr',
        'jane.miller@hive.com.tr',
        'austin.page@hive.com.tr',
        'elizabeth.taylor@hive.com.tr',
        'taylor.hope@hive.com.tr',
        'elmira.mcarthur@hive.com.tr'
    ]
    conn = get_db_connection()
    cursor = conn.cursor()
    for email in emails:
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = %s", (email,))
    conn.commit()
    cursor.close()
    conn.close()
    print("Scenario users marked as verified in users table.")

"""
Script to create users based on the Scenarios and Personas
Creates all personas mentioned in the scenarios with realistic data

IMPORTANT: Save these credentials for testing!
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import requests
from datetime import datetime


host = os.getenv('POSTGRES_HOST', 'localhost')  # Default to localhost for local execution
database = os.getenv('POSTGRES_DB', 'mydatabase')
user = os.getenv('POSTGRES_USER', 'myuser')
password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
port = os.getenv('POSTGRES_PORT', '5001')

def get_db_connection():
    """Connect to the database"""
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        cursor_factory=RealDictCursor
    )
    return conn

def create_user(cursor, email, password, first_name, last_name, phone, biography, time_balance=1.0):
    pass  # No longer used for sign-up

def create_scenario_users():
    """Create all persona users from the scenarios"""
    
    # Define all users based on scenarios and personas
    users_data = [
        {
            'email': 'alex.chen@hive.com.tr',
            'password': 'Alex2024!',
            'first_name': 'Alex',
            'last_name': 'Chen',
            'phone': '5551234567',
            'biography': '28-year-old freelance graphic designer, new to the neighborhood. Tech-savvy and eager to connect with the community. I offer design skills and looking for help with furniture assembly and home setup.',
            'time_balance': 1.0,
            'role': 'user'
        },
        {
            'email': 'jane.miller@hive.com.tr',
            'password': 'Jane2024!',
            'first_name': 'Jane',
            'last_name': 'Miller',
            'phone': '5552345678',
            'biography': 'Master\'s student and mother of a wonderful 4.5-year-old daughter. Looking for trustworthy babysitters for evening classes. I can offer academic help like proofreading and research assistance in return.',
            'time_balance': 1.0,
            'role': 'user'
        },
        {
            'email': 'austin.page@hive.com.tr',
            'password': 'Austin2024!',
            'first_name': 'Austin',
            'last_name': 'Page',
            'phone': '5553456789',
            'biography': 'College student, new to the city. Offering guitar lessons and help with household chores. Friendly and reliable, hoping to make this neighborhood feel like home while earning some time credits.',
            'time_balance': 1.0,
            'role': 'user'
        },
        {
            'email': 'elizabeth.taylor@hive.com.tr',
            'password': 'Elizabeth2024!',
            'first_name': 'Elizabeth',
            'last_name': 'Taylor',
            'phone': '5554567890',
            'biography': '70-year-old retiree and art history enthusiast. Living in this neighborhood for over 40 years. Sometimes need help with gardening or moving boxes. Love sharing stories about art and my grandchildren with friendly neighbors.',
            'time_balance': 1.0,
            'role': 'user'
        },
        {
            'email': 'taylor.hope@hive.com.tr',
            'password': 'Taylor2024!',
            'first_name': 'Taylor',
            'last_name': 'Hope',
            'phone': '5555678901',
            'biography': '16-year-old high school student and basketball player. Available for running errands or making deliveries on my bike. Saving time credits for math tutoring to ace my upcoming exams!',
            'time_balance': 1.0,
            'role': 'user'
        },
        {
            'email': 'elmira.mcarthur@hive.com.tr',
            'password': 'Elmira2024!',
            'first_name': 'Elmira',
            'last_name': 'McArthur',
            'phone': '5556789012',
            'biography': '45-year-old retired project manager running a local community center. Passionate about fostering a safe and fair environment for neighbors. Detail-oriented with a strong sense of justice.',
            'time_balance': 1.0,
            'role': 'user'        }
    ]
    
    print("\n" + "=" * 70)
    print("CREATING SCENARIO USERS FROM PERSONAS")
    print("=" * 70)
    
    credentials = []
    signup_url = os.getenv('SIGNUP_URL', 'http://localhost:5001/api/auth/register')
    for user_data in users_data:
        role = user_data.pop('role')
        print(f"\n📝 Signing up: {user_data['first_name']} {user_data['last_name']} ({role})")
        payload = {
            'email': user_data['email'],
            'password': user_data['password'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'phone_number': user_data['phone']
        }
        verification_token = None
        try:
            response = requests.post(signup_url, json=payload)
            data = response.json()
            if response.status_code == 201:
                print(f"   ✅ Signed up: {user_data['email']}")
                signed_up = True
                verification_token = data.get('verification_token')
            elif response.status_code == 409:
                print(f"   ⚠️  User {user_data['email']} already exists, skipping...")
                signed_up = False
            else:
                print(f"   ❌ Error signing up {user_data['email']}: {response.text}")
                signed_up = False
        except Exception as e:
            print(f"   ❌ Exception for {user_data['email']}: {e}")
            signed_up = False
        # If we have a verification token, verify via API
        if verification_token:
            verify_url = os.getenv('VERIFY_URL', 'http://localhost:5001/api/auth/verify-email')
            verify_response = requests.get(verify_url, params={'token': verification_token})
            if verify_response.status_code == 200:
                print(f"   ✅ Verified {user_data['email']} via API.")
            else:
                print(f"   ❌ Failed to verify {user_data['email']} via API: {verify_response.text}")
        credentials.append({
            'name': f"{user_data['first_name']} {user_data['last_name']}",
            'email': user_data['email'],
            'password': user_data['password'],
            'role': role,
            'biography': user_data['biography'],
            'signed_up': signed_up
        })
    # Update biography for all users
    conn = get_db_connection()
    cursor = conn.cursor()
    for cred in credentials:
        cursor.execute("UPDATE users SET biography = %s WHERE email = %s", (cred['biography'], cred['email']))
    conn.commit()
    cursor.close()
    conn.close()
    return credentials

def print_credentials_summary(credentials):
    """Print a formatted summary of all user credentials"""
    print("\n" + "=" * 70)
    print("✅ USER CREATION COMPLETED - SAVE THESE CREDENTIALS!")
    print("=" * 70)
    
    print("\n📋 USER CREDENTIALS FOR TESTING:\n")
    print("-" * 70)
    
    for cred in credentials:
        print(f"\n{cred['name']} - {cred['role']}")
        print(f"  📧 Email:    {cred['email']}")
        print(f"  🔑 Password: {cred['password']}")
        print(f"  🆔 User ID:  {cred['id']}")
    
    print("\n" + "-" * 70)
    print("\n💡 QUICK REFERENCE:")
    print("-" * 70)
    for cred in credentials:
        print(f"{cred['email']} / {cred['password']}")
    
        print("\n" + "=" * 70)
        print("SCENARIO MAPPING:")
        print("=" * 70)
        print("""
Scenario 1: Alex Chen signs up and verifies email
    → Use: alex.chen@hive.com.tr / Alex2024!

Scenario 2: Austin posts guitar lesson offering
    → Use: austin.page@hive.com.tr / Austin2024!

Scenario 3: Taylor searches map for gardening request
    → Use: taylor.hope@hive.com.tr / Taylor2024!

Scenario 4: Jane requests babysitting, Elizabeth provides
    → Jane (Consumer): jane.miller@hive.com.tr / Jane2024!
    → Elizabeth (Provider): elizabeth.taylor@hive.com.tr / Elizabeth2024!

Scenario 5: Alex completes moving-help request
    → Use: alex.chen@hive.com.tr / Alex2024!

Scenario 6: Elmira flags abusive content (Regular user)
    → Use: elmira.mcarthur@hive.com.tr / Elmira2024!
        """)
        print("=" * 70)

def main():
    """Main function to create all scenario users"""
    print("\n🚀 Starting user creation process...")
    
    try:
        credentials = create_scenario_users()
        mark_scenario_users_verified()
        if credentials:
            print_credentials_summary(credentials)
            print("\n\n🎯 NEXT STEPS:")
            print("  1. Copy these credentials to a safe place")
            print("  2. Run create_mock_data.py to create services")
            print("  3. Test scenarios using these user accounts")
            print("  4. Access local app at: http://localhost:5001")
            print("\n✨ Ready to test all scenarios!\n")
        else:
            print("\n⚠️  No users were created (they may already exist)")
    except Exception as e:
        print(f"\n❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
