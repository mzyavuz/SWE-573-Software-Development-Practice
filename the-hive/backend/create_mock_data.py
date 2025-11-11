"""
Script to create mock services and applications for testing
This creates a variety of services (offers and needs) and applications between users
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import random

def get_db_connection():
    conn = psycopg2.connect(
        host="db",
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        cursor_factory=RealDictCursor
    )
    return conn

def create_mock_services():
    """Create mock services (offers and needs)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, first_name, last_name FROM users ORDER BY id")
    users = cursor.fetchall()
    
    if len(users) < 2:
        print("Need at least 2 users to create mock data. Please create users first.")
        return
    
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  - User {user['id']}: {user['first_name']} {user['last_name']}")
    
    # Get or create tags
    tags = [
        'Tutoring', 'Music', 'Language', 'Cooking', 'Gardening',
        'Computer', 'Art', 'Fitness Training', 'Pet Care', 'Home Repair',
        'Photography', 'Writing', 'Math', 'Career Advice', 'Elderly Care'
    ]
    
    tag_ids = {}
    for tag_name in tags:
        # Try to get existing tag first
        cursor.execute("SELECT id FROM tags WHERE LOWER(name) = LOWER(%s)", (tag_name,))
        existing = cursor.fetchone()
        
        if existing:
            tag_ids[tag_name] = existing['id']
        else:
            # Create new tag if it doesn't exist
            cursor.execute("""
                INSERT INTO tags (name, created_by, is_approved) 
                VALUES (%s, %s, TRUE)
                RETURNING id
            """, (tag_name, users[0]['id']))
            tag_ids[tag_name] = cursor.fetchone()['id']
    
    print(f"\nProcessed {len(tags)} tags")
    
    # Mock service data - OFFERS
    mock_offers = [
        {
            'title': 'Python Programming Tutoring',
            'description': 'Experienced Python developer offering tutoring sessions. I can help with basics, web development, data analysis, and more. Perfect for beginners or intermediate learners!',
            'hours_required': 2.0,
            'location_type': 'online',
            'location_address': 'Istanbul, Kadıköy - Music Studio',
            'latitude': 40.9929,
            'longitude': 29.0260,
            'tags': ['Tutoring', 'Computer'],
            'status': 'open',
            'availability': [
                {'day': 3, 'start': '18:00', 'end': '21:00'},  
                {'day': 4, 'start': '18:00', 'end': '21:00'},  
                {'day': 5, 'start': '14:00', 'end': '20:00'},  
            ]
        },
        {
            'title': 'Guitar Lessons for Beginners',
            'description': 'I have been playing guitar for 10 years and love teaching! Offering fun, relaxed lessons for beginners. We can cover acoustic or electric guitar basics.',
            'hours_required': 1,
            'location_type': 'in-person',
            'location_address': 'Istanbul, Kadıköy - Music Studio',
            'latitude': 40.9929,
            'longitude': 29.0260,
            'tags': ['Music', 'Tutoring'],
            'status': 'open',
            'availability': [
                {'day': 1, 'start': '18:00', 'end': '21:00'},  
                {'day': 3, 'start': '18:00', 'end': '21:00'},  
                {'day': 5, 'start': '14:00', 'end': '20:00'},  
            ]
        },
        {
            'title': 'Turkish Language Practice',
            'description': 'Native Turkish speaker offering conversation practice for language learners. Great for improving your speaking skills in a friendly environment!',
            'hours_required': 1.0,
            'location_type': 'both',
            'location_address': 'Istanbul, Beşiktaş - Coffee Shop',
            'latitude': 41.0422,
            'longitude': 29.0096,
            'tags': ['Language', 'Tutoring'],
            'status': 'open',
            'availability': [
                {'day': 2, 'start': '10:00', 'end': '12:00'},  
                {'day': 4, 'start': '10:00', 'end': '12:00'},  
                {'day': 6, 'start': '09:00', 'end': '15:00'}, 
            ]
        },
        {
            'title': 'Home Cooking Classes',
            'description': 'Love cooking and want to share my passion! I can teach you traditional Turkish dishes or international cuisine. Hands-on sessions in my kitchen.',
            'hours_required': 3.0,
            'location_type': 'in-person',
            'location_address': 'Istanbul, Şişli - My Kitchen',
            'latitude': 41.0602,
            'longitude': 28.9887,
            'tags': ['Cooking'],
            'status': 'open',
            'availability': [
                {'day': 0, 'start': '14:00', 'end': '18:00'}, 
                {'day': 6, 'start': '11:00', 'end': '17:00'},  
            ]
        },
        {
            'title': 'Garden Design Consultation',
            'description': 'Professional landscaper offering garden design advice. I can help you plan your balcony garden, backyard, or indoor plants. Virtual consultations available!',
            'hours_required': 2.0,
            'location_type': 'in-person',
            'location_address': 'Istanbul, Kadıköy - My Office',
            'latitude': 40.9929,
            'longitude': 29.0260,
            'tags': ['Gardening'],
            'status': 'open',
            'availability': [
                {'day': 6, 'start': '14:00', 'end': '18:00'},  
                {'day': 0, 'start': '11:00', 'end': '17:00'},  
            ]
        },
        {
            'title': 'Basic Photography Skills',
            'description': 'Amateur photographer sharing tips and techniques! Learn composition, lighting, and basic editing. Bring your camera or smartphone.',
            'hours_required': 2,
            'location_type': 'in-person',
            'location_address': 'Istanbul, Taksim - Gezi Park',
            'latitude': 41.0370,
            'longitude': 28.9869,
            'tags': ['Photography', 'Art Classes'],
            'status': 'open',
            'availability': [
                {'day': 6, 'start': '10:00', 'end': '16:00'},  # Saturday
                {'day': 0, 'start': '10:00', 'end': '16:00'},  # Sunday
            ]
        }
    ]
    
    # Mock service data - NEEDS
    mock_needs = [
        {
            'title': 'Need Help with Math Homework',
            'description': 'Student struggling with calculus. Looking for someone who can explain derivatives and integrals in a simple way. Online sessions preferred.',
            'hours_required': 2.0,
            'service_date': '2025-11-20 18:00:00',
            'start_time': '18:00:00',
            'end_time': '20:00:00',
            'location_type': 'online',
            'location_address': 'Istanbul, Online',
            'latitude': 41.0082,
            'longitude': 28.9784,
            'tags': ['Math', 'Tutoring'],
            'status': 'open'
        },
        {
            'title': 'Looking for Dog Walker',
            'description': 'My golden retriever needs daily walks while I\'m at work. Looking for a reliable person who loves dogs! Weekday mornings preferred.',
            'hours_required': 1.0,
            'service_date': '2025-11-18 08:00:00',
            'start_time': '08:00:00',
            'end_time': '09:00:00',
            'location_type': 'in-person',
            'location_address': 'Istanbul, Nişantaşı',
            'latitude': 41.0492,
            'longitude': 28.9941,
            'tags': ['Pet Care'],
            'status': 'open',
        },
        {
            'title': 'Resume Writing Assistance',
            'description': 'Recent graduate looking for help with resume and cover letter writing. I need guidance on how to present my skills effectively for job applications.',
            'hours_required': 1,
            'service_date': '2025-11-22 16:00:00',
            'start_time': '16:00:00',
            'end_time': '17:00:00',
            'location_type': 'online',
            'location_address': 'Istanbul, Online',
            'latitude': 41.0082,
            'longitude': 28.9784,
            'tags': ['Career Advice', 'Writing'],
            'status': 'open'
        },
        {
            'title': 'Website Design Help Needed',
            'description': 'Looking for someone with HTML/CSS/WordPress knowledge to guide me through the process.',
            'hours_required': 3,
            'service_date': '2025-11-19 10:00:00',
            'start_time': '10:00:00',
            'end_time': '13:00:00',
            'location_type': 'online',
            'location_address': 'Istanbul, Online',
            'latitude': 41.0082,
            'longitude': 28.9784,
            'tags': ['Computer'],
            'status': 'open'
        },
        {
            'title': 'English Conversation Partner',
            'description': 'Preparing for TOEFL exam and need to practice speaking English. Looking for a native or fluent speaker for regular conversation practice.',
            'hours_required': 1.0,
            'service_date': '2025-11-21 11:00:00',
            'start_time': '11:00:00',
            'end_time': '12:00:00',
            'location_type': 'both',
            'location_address': 'Istanbul, Levent - Coffee Shop',
            'latitude': 41.0809,
            'longitude': 29.0122,
            'tags': ['Language', 'Tutoring'],
            'status': 'open',
        },
        {
            'title': 'Elderly Care Companion',
            'description': 'Looking for someone to spend time with my elderly father. He enjoys conversation, board games, and short walks. Kind and patient person needed.',
            'hours_required': 2.0,
            'service_date': '2025-11-20 14:00:00',
            'start_time': '14:00:00',
            'end_time': '16:00:00',
            'location_type': 'in-person',
            'location_address': 'Istanbul, Bakırköy',
            'latitude': 40.9833,
            'longitude': 28.8597,
            'tags': ['Elderly Care'],
            'status': 'open',
        }
    ]
    
    # Create offers
    created_services = []
    user_index = 0
    
    print("\n=== Creating OFFERS ===")
    for offer_data in mock_offers:
        user_id = users[user_index % len(users)]['id']
        user_index += 1
        
        # Insert service
        cursor.execute("""
            INSERT INTO services (
                user_id, service_type, title, description, hours_required,
                location_type, location_address, latitude, longitude, status,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            'offer',
            offer_data['title'],
            offer_data['description'],
            offer_data['hours_required'],
            offer_data['location_type'],
            offer_data.get('location_address'),
            offer_data.get('latitude'),
            offer_data.get('longitude'),
            offer_data['status'],
            datetime.now() - timedelta(days=random.randint(1, 10))
        ))
        
        service_id = cursor.fetchone()['id']
        created_services.append({'id': service_id, 'type': 'offer', 'user_id': user_id})
        
        # Add tags
        for tag_name in offer_data['tags']:
            cursor.execute("""
                INSERT INTO service_tags (service_id, tag_id)
                VALUES (%s, %s)
            """, (service_id, tag_ids[tag_name]))
        
        # Add availability if provided
        if 'availability' in offer_data:
            for avail in offer_data['availability']:
                cursor.execute("""
                    INSERT INTO service_availability (service_id, day_of_week, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                """, (service_id, avail['day'], avail['start'], avail['end']))
        
        print(f"  ✓ Created offer #{service_id}: {offer_data['title']} (User {user_id})")
    
    # Create needs
    print("\n=== Creating NEEDS ===")
    for need_data in mock_needs:
        user_id = users[user_index % len(users)]['id']
        user_index += 1
        
        # Insert service
        cursor.execute("""
            INSERT INTO services (
                user_id, service_type, title, description, hours_required,
                location_type, location_address, latitude, longitude, status,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            'need',
            need_data['title'],
            need_data['description'],
            need_data['hours'],
            need_data['location_type'],
            need_data.get('location'),
            need_data.get('latitude'),
            need_data.get('longitude'),
            need_data['status'],
            datetime.now() - timedelta(days=random.randint(1, 10))
        ))
        
        service_id = cursor.fetchone()['id']
        created_services.append({'id': service_id, 'type': 'need', 'user_id': user_id})
        
        # Add tags
        for tag_name in need_data['tags']:
            cursor.execute("""
                INSERT INTO service_tags (service_id, tag_id)
                VALUES (%s, %s)
            """, (service_id, tag_ids[tag_name]))
        
        # Add availability if provided
        if 'availability' in need_data:
            for avail in need_data['availability']:
                cursor.execute("""
                    INSERT INTO service_availability (service_id, day_of_week, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                """, (service_id, avail['day'], avail['start'], avail['end']))
        
        print(f"  ✓ Created need #{service_id}: {need_data['title']} (User {user_id})")
    
    conn.commit()
    print(f"\n✅ Created {len(mock_offers)} offers and {len(mock_needs)} needs")
    
    return created_services, users

def create_mock_applications(created_services, users):
    """Create mock applications for services"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n=== Creating APPLICATIONS ===")
    
    application_messages = [
        "I'm very interested in this service! I have experience in this area.",
        "This looks perfect for what I need. I'm available as scheduled!",
        "I'd love to help with this! Please let me know if I'm a good fit.",
        "Count me in! I think we can work great together.",
        "This matches my skills perfectly. Looking forward to working together!",
        "I'm excited about this opportunity. Let me know if you need more info!",
        "I believe I can provide great value here. Happy to discuss further!",
        "This is exactly what I've been looking for. Thank you for posting!"
    ]
    
    applications_created = 0
    
    # Create applications - each service gets 1-3 random applications from different users
    for service in created_services:
        service_id = service['id']
        service_owner = service['user_id']
        service_type = service['type']
        
        # Determine how many applications (1-3)
        num_applications = random.randint(1, 3)
        
        # Get potential applicants (users who don't own this service)
        potential_applicants = [u for u in users if u['id'] != service_owner]
        
        # Select random applicants
        applicants = random.sample(potential_applicants, min(num_applications, len(potential_applicants)))
        
        for i, applicant in enumerate(applicants):
            # Determine application status
            if i == 0:
                # First application has higher chance of being accepted
                status = random.choice(['pending', 'pending', 'accepted', 'pending'])
            else:
                status = random.choice(['pending', 'pending', 'pending', 'rejected'])
            
            message = random.choice(application_messages)
            
            # Create application
            cursor.execute("""
                INSERT INTO service_applications (
                    service_id, applicant_id, status, message, applied_at
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                service_id,
                applicant['id'],
                status,
                message,
                datetime.now() - timedelta(days=random.randint(0, 7))
            ))
            
            application_id = cursor.fetchone()['id']
            applications_created += 1
            
            status_emoji = {'pending': '⏳', 'accepted': '✅', 'rejected': '❌', 'withdrawn': '🚫'}
            print(f"  {status_emoji.get(status, '•')} Application #{application_id}: User {applicant['id']} → Service #{service_id} ({status})")
    
    conn.commit()
    print(f"\n✅ Created {applications_created} applications")
    
    cursor.close()
    conn.close()

def main():
    print("=" * 60)
    print("CREATING MOCK SERVICES AND APPLICATIONS")
    print("=" * 60)
    
    try:
        created_services, users = create_mock_services()
        create_mock_applications(created_services, users)
        
        print("\n" + "=" * 60)
        print("✅ MOCK DATA CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now:")
        print("  • Browse services at http://localhost:5000")
        print("  • View applications in user profiles")
        print("  • Test the full workflow from application to completion")
        
    except Exception as e:
        print(f"\n❌ Error creating mock data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
