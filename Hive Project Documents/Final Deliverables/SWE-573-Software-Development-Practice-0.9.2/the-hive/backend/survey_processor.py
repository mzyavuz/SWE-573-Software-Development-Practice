"""
Background task processor for expired surveys
This module handles auto-completion of services when 24-hour survey deadline expires
"""
import time
import threading
from app import get_db_connection


def process_expired_surveys():
    """
    Process surveys that have exceeded the 24-hour deadline.
    Auto-complete services where deadline has passed.
    This should be called periodically (e.g., every hour via cron job).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find all services awaiting confirmation with expired deadlines
        cursor.execute("""
            SELECT id, provider_id, consumer_id, hours,
                   provider_survey_submitted, consumer_survey_submitted
            FROM service_progress
            WHERE status = 'awaiting_confirmation'
            AND survey_deadline < NOW()
            AND survey_deadline IS NOT NULL
        """)
        
        expired_services = cursor.fetchall()
        
        for service in expired_services:
            print(f"Auto-completing service {service['id']} (deadline expired)")
            
            # Update progress status to completed
            cursor.execute("""
                UPDATE service_progress 
                SET status = 'completed', 
                    completed_at = NOW(), 
                    updated_at = NOW()
                WHERE id = %s
            """, (service['id'],))
            
            # Transfer hours: add to provider, deduct from consumer
            cursor.execute("""
                UPDATE users 
                SET time_balance = time_balance + %s 
                WHERE id = %s
            """, (service['hours'], service['provider_id']))
            
            cursor.execute("""
                UPDATE users 
                SET time_balance = time_balance - %s 
                WHERE id = %s
            """, (service['hours'], service['consumer_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Processed {len(expired_services)} expired surveys")
        return len(expired_services)
        
    except Exception as e:
        print(f"ERROR in process_expired_surveys: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def background_survey_processor():
    """Background thread that processes expired surveys every hour"""
    while True:
        try:
            time.sleep(3600)  # Wait 1 hour
            process_expired_surveys()
        except Exception as e:
            print(f"Error in background survey processor: {e}")


def start_background_processor():
    """Start the background survey processor thread"""
    survey_thread = threading.Thread(target=background_survey_processor, daemon=True)
    survey_thread.start()
    print("Started background survey processor (runs every hour)")
