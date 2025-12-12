from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_bcrypt import Bcrypt
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
import re
from werkzeug.utils import secure_filename
import uuid

# Configure Flask to find templates in the frontend folder
# This path works both locally and in Docker container
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = os.path.join(static_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to connect to the database
def get_db_connection():
    # Check if DATABASE_URL is set (DigitalOcean/Production)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL for production (DigitalOcean format)
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        # Use individual environment variables for local/docker-compose/DigitalOcean
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "db"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
            database=os.environ.get("POSTGRES_DB"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            sslmode=os.environ.get("POSTGRES_SSLMODE", "require"),
            cursor_factory=RealDictCursor
        )
    return conn

# Initialize database tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone_number VARCHAR(20),
            biography TEXT,
            profile_photo VARCHAR(255),
            role VARCHAR(20) DEFAULT 'user',
            time_balance DECIMAL(10,2) DEFAULT 1.0,
            is_verified BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            user_status VARCHAR(20) DEFAULT 'active' CHECK (user_status IN ('active', 'banned', 'warning')),
            date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """)
    
    # Create email verification tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_verifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT FALSE
        );
    """)
    
    # Create tags table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            created_by INTEGER REFERENCES users(id),
            is_approved BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create services table (for both offers and needs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            service_type VARCHAR(10) NOT NULL CHECK (service_type IN ('offer', 'need')),
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            hours_required DECIMAL(10,2) NOT NULL CHECK (hours_required >= 1.0 AND hours_required <= 3.0),
            location_type VARCHAR(20) NOT NULL CHECK (location_type IN ('online', 'in-person', 'both')),
            location_address TEXT,
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled', 'expired')),
            service_date TIMESTAMP,
            start_time TIME,
            end_time TIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create service_tags junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_tags (
            service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
            tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (service_id, tag_id)
        );
    """)
    
    # Create service_availability table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_availability (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
            start_time TIME NOT NULL,
            end_time TIME NOT NULL
        );
    """)
    
    # Create password_reset_tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT FALSE
        );
    """)
    
    # Create service_applications table (for tracking applications to services)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_applications (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
            applicant_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled', 'withdrawn')),
            message TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(service_id, applicant_id)
        );
    """)
    
    # Add 'withdrawn' to existing status check constraint if table already exists
    cursor.execute("""
        DO $$
        BEGIN
            -- Drop the old constraint if it exists
            ALTER TABLE service_applications DROP CONSTRAINT IF EXISTS service_applications_status_check;
            
            -- Add the new constraint with 'withdrawn' included
            ALTER TABLE service_applications ADD CONSTRAINT service_applications_status_check 
                CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled', 'withdrawn'));
        EXCEPTION
            WHEN OTHERS THEN
                -- Ignore errors if constraint doesn't exist
                NULL;
        END $$;
    """)
    
    # Create service_progress table (for tracking service completion workflow)
    # Progress flow: selected -> scheduled -> in_progress -> awaiting_confirmation -> completed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_progress (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES services(id),
            application_id INTEGER REFERENCES service_applications(id),
            provider_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            consumer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            hours DECIMAL(10,2) NOT NULL,
            status VARCHAR(30) DEFAULT 'selected' CHECK (status IN ('selected', 'scheduled', 'in_progress', 'awaiting_confirmation', 'completed', 'disputed', 'cancelled')),
            scheduled_date DATE,
            scheduled_time TIME,
            agreed_location TEXT,
            special_instructions TEXT,
            provider_confirmed BOOLEAN DEFAULT FALSE,
            consumer_confirmed BOOLEAN DEFAULT FALSE,
            provider_start_confirmed BOOLEAN DEFAULT FALSE,
            consumer_start_confirmed BOOLEAN DEFAULT FALSE,
            provider_start_confirmed_at TIMESTAMP,
            consumer_start_confirmed_at TIMESTAMP,
            proposed_date DATE,
            proposed_time TIME,
            proposed_location TEXT,
            proposed_by INTEGER REFERENCES users(id),
            proposed_at TIMESTAMP,
            schedule_accepted_by_consumer BOOLEAN DEFAULT FALSE,
            schedule_accepted_by_provider BOOLEAN DEFAULT FALSE,
            service_end_date DATE,
            service_start_date DATE,
            provider_survey_submitted BOOLEAN DEFAULT FALSE,
            consumer_survey_submitted BOOLEAN DEFAULT FALSE,
            provider_survey_submitted_at TIMESTAMP,
            consumer_survey_submitted_at TIMESTAMP,
            provider_survey_data JSONB,
            consumer_survey_data JSONB,
            survey_deadline TIMESTAMP,
            selected_at TIMESTAMP,
            scheduled_at TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create messages table (for communication between users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
            application_id INTEGER REFERENCES service_applications(id) ON DELETE CASCADE,
            sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            receiver_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            message_type VARCHAR(50) DEFAULT 'text',
            proposal_date DATE,
            proposal_start_time TIME,
            proposal_end_time TIME,
            proposal_status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Add migration columns to existing tables (safe to run multiple times)
    print("Applying database migrations...")
    
    # Add new columns to services table
    cursor.execute("""
        ALTER TABLE services 
        ADD COLUMN IF NOT EXISTS start_time TIME,
        ADD COLUMN IF NOT EXISTS end_time TIME;
    """)
    
    # Add new columns to service_progress table
    cursor.execute("""
        ALTER TABLE service_progress 
        ADD COLUMN IF NOT EXISTS provider_start_confirmed BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS consumer_start_confirmed BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS provider_start_confirmed_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS consumer_start_confirmed_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS proposed_date DATE,
        ADD COLUMN IF NOT EXISTS proposed_time TIME,
        ADD COLUMN IF NOT EXISTS proposed_location TEXT,
        ADD COLUMN IF NOT EXISTS proposed_by INTEGER REFERENCES users(id),
        ADD COLUMN IF NOT EXISTS proposed_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS schedule_accepted_by_consumer BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS schedule_accepted_by_provider BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS service_end_date DATE,
        ADD COLUMN IF NOT EXISTS service_start_date DATE,
        ADD COLUMN IF NOT EXISTS provider_survey_submitted BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS consumer_survey_submitted BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS provider_survey_submitted_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS consumer_survey_submitted_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS provider_survey_data JSONB,
        ADD COLUMN IF NOT EXISTS consumer_survey_data JSONB,
        ADD COLUMN IF NOT EXISTS survey_deadline TIMESTAMP;
    """)
    
    # Add new columns to messages table
    cursor.execute("""
        ALTER TABLE messages 
        ADD COLUMN IF NOT EXISTS message_type VARCHAR(50) DEFAULT 'text',
        ADD COLUMN IF NOT EXISTS proposal_date DATE,
        ADD COLUMN IF NOT EXISTS proposal_start_time TIME,
        ADD COLUMN IF NOT EXISTS proposal_end_time TIME,
        ADD COLUMN IF NOT EXISTS proposal_location TEXT,
        ADD COLUMN IF NOT EXISTS proposal_status VARCHAR(20) DEFAULT 'pending';
    """)

    # Create index for survey deadlines on service_progress
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_service_progress_survey_deadline 
        ON service_progress(survey_deadline) 
        WHERE survey_deadline IS NOT NULL;
    """)
    
    # Create forum_categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create forum_threads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_threads (
            id SERIAL PRIMARY KEY,
            category_id INTEGER REFERENCES forum_categories(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            is_pinned BOOLEAN DEFAULT FALSE,
            is_locked BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create forum_comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_comments (
            id SERIAL PRIMARY KEY,
            thread_id INTEGER REFERENCES forum_threads(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            parent_comment_id INTEGER REFERENCES forum_comments(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create admin_logs table for audit trail
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id SERIAL PRIMARY KEY,
            admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            target_type VARCHAR(50) NOT NULL,
            target_id INTEGER,
            details JSONB,
            ip_address VARCHAR(45),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create reports table for content flagging
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            reporter_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            reported_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('service', 'thread', 'comment', 'user', 'message')),
            content_id INTEGER,
            reason VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'dismissed')),
            resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            resolved_at TIMESTAMP,
            resolution_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_forum_threads_category 
        ON forum_threads(category_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_forum_threads_user 
        ON forum_threads(user_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_forum_comments_thread 
        ON forum_comments(thread_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_forum_comments_user 
        ON forum_comments(user_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reports_status 
        ON reports(status);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_logs_admin 
        ON admin_logs(admin_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_admin_logs_created 
        ON admin_logs(created_at);
    """)
    
    # Add user_status column to existing users table
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS user_status VARCHAR(20) DEFAULT 'active' 
        CHECK (user_status IN ('active', 'banned', 'warning'));
    """)
    
    
    print("Migrations applied successfully!")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")

# Validation functions
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Valid"

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    pattern = r'^\+?1?\d{9,15}$'
    if re.match(pattern, phone):
        return True
    return False

def get_user_from_token(auth_header):
    """Extract and validate user from JWT token"""
    if not auth_header:
        return None, {"error": "Authorization header is required"}, 401
    
    try:
        token = auth_header.split(' ')[1]  # Bearer <token>
    except IndexError:
        return None, {"error": "Invalid authorization header format"}, 401
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id'], None, None
    except jwt.ExpiredSignatureError:
        return None, {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return None, {"error": "Invalid token"}, 401

def get_admin_from_token(auth_header):
    """Extract and validate admin user from JWT token"""
    if not auth_header:
        return None, {"error": "Authorization header is required"}, 401
    
    try:
        token = auth_header.split(' ')[1]  # Bearer <token>
    except IndexError:
        return None, {"error": "Invalid authorization header format"}, 401
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        role = payload.get('role', 'user')
        
        if role != 'admin':
            return None, {"error": "Admin access required"}, 403
            
        return user_id, None, None
    except jwt.ExpiredSignatureError:
        return None, {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return None, {"error": "Invalid token"}, 401

def log_admin_action(cursor, admin_id, action, target_type, target_id, details=None, ip_address=None):
    """Log admin actions for audit trail"""
    cursor.execute("""
        INSERT INTO admin_logs (admin_id, action, target_type, target_id, details, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (admin_id, action, target_type, target_id, details, ip_address))

def validate_time_balance(cursor, consumer_id, provider_id, hours_required):
    """
    Validate time balance constraints:
    1. Consumer must have enough time balance to consume
    2. Provider cannot exceed 10-hour maximum limit after receiving
    
    Returns: (is_valid, error_message)
    """
    MAX_TIME_BALANCE = 10.0
    
    # Get consumer's current time balance
    cursor.execute("""
        SELECT time_balance FROM users WHERE id = %s
    """, (consumer_id,))
    consumer = cursor.fetchone()
    
    if not consumer:
        return False, "Consumer not found"
    
    consumer_balance = float(consumer['time_balance'])
    
    # Check if consumer has enough balance
    if consumer_balance < hours_required:
        return False, f"Insufficient time balance. The consumer has {consumer_balance} hour(s), but this service requires {hours_required} hour(s). The consumer needs to earn more hours before you can accept this application."
    
    # Get provider's current time balance
    cursor.execute("""
        SELECT time_balance FROM users WHERE id = %s
    """, (provider_id,))
    provider = cursor.fetchone()
    
    if not provider:
        return False, "Provider not found"
    
    provider_balance = float(provider['time_balance'])
    
    # Check if provider would exceed maximum after receiving hours
    if provider_balance + hours_required > MAX_TIME_BALANCE:
        excess = (provider_balance + hours_required) - MAX_TIME_BALANCE
        return False, f"Provider time balance would exceed maximum limit of {MAX_TIME_BALANCE} hours. This service would add {hours_required} hour(s) to their current {provider_balance} hour(s), exceeding the limit by {excess} hour(s)."
    
    return True, None

# Frontend Routes
@app.route("/")
def index():
    """Landing page"""
    return render_template('index.html')

@app.route("/signup")
def signup():
    """User registration page"""
    return render_template('signup.html')

@app.route("/signin")
def signin():
    """User login page"""
    return render_template('signin.html')

@app.route("/profile")
def profile():
    """User profile page"""
    return render_template('profile.html')

@app.route("/admin-dashboard")
def admin_dashboard():
    """Admin dashboard page"""
    return render_template('admin-dashboard.html')

@app.route("/admin-users")
def admin_users_page():
    """Admin users management page"""
    return render_template('admin-users.html')

@app.route("/admin-services")
def admin_services_page():
    """Admin services management page"""
    return render_template('admin-services.html')

@app.route("/admin-reports")
def admin_reports_page():
    """Admin reports management page"""
    return render_template('admin-reports.html')

@app.route("/verify-email")
def verify_email_page():
    """Email verification page"""
    return render_template('verify-email.html')

@app.route("/create-service")
def create_service_page():
    """Create service (offer/need) page"""
    return render_template('create-service.html')

@app.route("/services")
def services_page():
    """Browse all services page"""
    return render_template('services.html')

@app.route("/forgot-password")
def forgot_password_page():
    """Forgot password page"""
    return render_template('forgot-password.html')

@app.route("/reset-password")
def reset_password_page():
    """Reset password page"""
    return render_template('reset-password.html')

@app.route("/edit-profile")
def edit_profile_page():
    """Edit profile page"""
    return render_template('edit-profile.html')

@app.route("/my-services")
def my_services_page():
    """My services page"""
    return render_template('my-services.html')

@app.route("/progress-status")
@app.route("/progress/<int:progress_id>")
def progress_status_page(progress_id=None):
    """Progress status page - tracks service completion workflow"""
    return render_template('progress-status.html')

# Progress tracking pages for different user roles
@app.route("/progress-provider-offer")
def progress_provider_offer_page():
    """Progress page for providers who own an offer - redirects to unified provider page"""
    return render_template('progress-provider.html')

@app.route("/progress-provider-need")
def progress_provider_need_page():
    """Progress page for providers responding to a need - redirects to unified provider page"""
    return render_template('progress-provider.html')

@app.route("/progress-provider")
def progress_provider_page():
    """Unified progress page for all provider types (offering service or responding to need)"""
    return render_template('progress-provider.html')

@app.route("/progress-consumer")
def progress_consumer_page():
    """Progress page for service owners (consumers)"""
    return render_template('progress-consumer.html')

# Keep old routes for backwards compatibility (redirect to progress)
@app.route("/user/<int:user_id>")
def public_profile_page(user_id):
    """Public profile page"""
    return render_template('profile-public.html')

@app.route("/edit-service/<int:service_id>")
def edit_service_page(service_id):
    """Edit service page"""
    return render_template('edit-service.html')

@app.route("/applications")
def applications_page():
    """Applications page"""
    return render_template('applications.html')

@app.route("/messages")
def messages_page():
    """Messages page"""
    return render_template('messages.html')

@app.route("/forum")
def forum_page():
    """Forum main page - The Commons"""
    return render_template('forum.html')

@app.route("/forum/category/<int:category_id>")
def forum_category_page(category_id):
    """Forum category page - shows threads in a category"""
    return render_template('forum-category.html')

@app.route("/forum/thread/<int:thread_id>")
def forum_thread_page(thread_id):
    """Forum thread page - shows a single thread with comments"""
    return render_template('forum-thread.html')

@app.route("/forum/new-thread")
def forum_new_thread_page():
    """Create new forum thread page"""
    return render_template('forum-new-thread.html')

@app.route("/service/<int:service_id>")
def service_detail_page(service_id):
    """Service detail page"""
    return render_template('service-detail.html')

# API Info Route
@app.route("/api")
def api_info():
    """API information endpoint"""
    return jsonify({
        "message": "Welcome to The Hive API!",
        "endpoints": {
            "health": "GET /api/health",
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "verify_email": "GET /api/auth/verify-email?token=<token>",
            "profile": "GET /api/auth/profile (requires token)"
        }
    })

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            "status": "success", 
            "message": "API is running and database is connected!"
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route("/api/auth/register", methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        
        # Validate email
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({"error": f"Invalid email: {str(e)}"}), 400
        
        # Validate password
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Validate phone number if provided
        if phone_number and not validate_phone(phone_number):
            return jsonify({"error": "Invalid phone number format"}), 400
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert user into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, phone_number)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, email, first_name, last_name, date_joined
            """, (email, password_hash, first_name, last_name, phone_number))
            
            user = cursor.fetchone()
            conn.commit()
            
            # Generate verification token (simplified - in production use secure tokens)
            verification_token = jwt.encode({
                'user_id': user['id'],
                'email': email,
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            # Store verification token
            cursor.execute("""
                INSERT INTO email_verifications (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user['id'], verification_token, datetime.now(timezone.utc) + timedelta(hours=24)))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "User registered successfully! Please verify your email.",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "date_joined": user['date_joined'].isoformat()
                },
                "verification_token": verification_token,
                "note": "In production, this token would be sent via email"
            }), 201
            
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Email already exists"}), 409
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/auth/login", methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name, 
                   is_verified, is_active, role, time_balance
            FROM users 
            WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check password
        if not bcrypt.check_password_hash(user['password_hash'], password):
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is banned
        cursor.execute("SELECT user_status FROM users WHERE id = %s", (user['id'],))
        status_result = cursor.fetchone()
        if status_result and status_result['user_status'] == 'banned':
            cursor.close()
            conn.close()
            return jsonify({"error": "Your account is banned"}), 403
        
        # Check if user is active
        if not user['is_active']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Check if email is verified
        if not user['is_verified']:
            cursor.close()
            conn.close()
            return jsonify({
                "error": "Please verify your email before logging in",
                "is_verified": False
            }), 403
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (user['id'],))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Generate access token
        access_token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "role": user['role'],
                "time_balance": float(user['time_balance']) if user['time_balance'] else 1.0
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/auth/verify-email", methods=['GET'])
def verify_email():
    """Email verification endpoint"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({"error": "Verification token is required"}), 400
        
        # Decode token
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Verification token has expired"}), 400
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid verification token"}), 400
        
        # Verify user
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if token is valid and not used
        cursor.execute("""
            SELECT id, is_used FROM email_verifications 
            WHERE token = %s AND user_id = %s AND expires_at > CURRENT_TIMESTAMP
        """, (token, user_id))
        
        verification = cursor.fetchone()
        
        if not verification:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid or expired token"}), 400
        
        if verification['is_used']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Token has already been used"}), 400
        
        # Update user verification status
        cursor.execute("""
            UPDATE users SET is_verified = TRUE 
            WHERE id = %s
        """, (user_id,))
        
        # Mark token as used
        cursor.execute("""
            UPDATE email_verifications SET is_used = TRUE 
            WHERE id = %s
        """, (verification['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Email verified successfully! You can now log in."
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/auth/profile", methods=['GET'])
def get_profile():
    """Get user profile (protected route)"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header is required"}), 401
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Decode token
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user profile
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, first_name, last_name, phone_number, 
                   biography, profile_photo, role, is_verified, date_joined, last_login, time_balance
            FROM users 
            WHERE id = %s AND is_active = TRUE
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "phone_number": user['phone_number'],
                "biography": user['biography'],
                "profile_photo": user['profile_photo'],
                "role": user['role'],
                "is_verified": user['is_verified'],
                "date_joined": user['date_joined'].isoformat() if user['date_joined'] else None,
                "last_login": user['last_login'].isoformat() if user['last_login'] else None,
                "time_balance": int(user['time_balance']) if user['time_balance'] is not None else 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/users/<int:user_id>", methods=['GET'])
def get_public_profile(user_id):
    """Get public user profile (no auth required)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user basic info (only public fields)
        cursor.execute("""
            SELECT id, first_name, last_name, biography, 
                   profile_photo, is_verified, date_joined,
                   COALESCE(time_balance, 1.0) as time_balance
            FROM users
            WHERE id = %s AND is_active = TRUE
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        # Get user's public services (offers and needs)
        cursor.execute("""
            SELECT s.id, s.service_type, s.title, s.description, 
                   s.hours_required, s.location_type, 
                   s.location_address, s.status, s.created_at,
                   ARRAY_AGG(DISTINCT t.name) as tags
            FROM services s
            LEFT JOIN service_tags st ON s.id = st.service_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE s.user_id = %s AND s.status = 'open'
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """, (user_id,))
        
        services = cursor.fetchall()
        
        # Get user stats (simplified - transactions table not yet implemented)
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN service_type = 'offer' AND status = 'open' THEN id END) as total_offers,
                COUNT(DISTINCT CASE WHEN service_type = 'need' AND status = 'open' THEN id END) as total_needs,
                0 as completed_as_provider,
                0 as completed_as_consumer
            FROM services
            WHERE user_id = %s
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "user": {
                "id": user['id'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "biography": user['biography'],
                "profile_photo": user['profile_photo'],
                "is_verified": user['is_verified'],
                "member_since": user['date_joined'].isoformat() if user['date_joined'] else None,
                "time_balance": float(user['time_balance'])
            },
            "stats": {
                "total_offers": stats['total_offers'] if stats else 0,
                "total_needs": stats['total_needs'] if stats else 0,
                "completed_as_provider": stats['completed_as_provider'] if stats else 0,
                "completed_as_consumer": stats['completed_as_consumer'] if stats else 0
            },
            "services": [
                {
                    "id": service['id'],
                    "service_type": service['service_type'],
                    "title": service['title'],
                    "description": service['description'],
                    "duration_hours": float(service['hours_required']),
                    "hours_cost": float(service['hours_required']),  # Using same value for now
                    "location_type": service['location_type'],
                    "location_address": service['location_address'],
                    "status": service['status'],
                    "created_at": service['created_at'].isoformat(),
                    "tags": service['tags'] if service['tags'][0] else []
                }
                for service in services
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/auth/profile", methods=['PUT'])
def update_profile():
    """Update user profile (protected route)"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        # Allowed fields to update
        if 'first_name' in data:
            first_name = data['first_name'].strip()
            if not first_name:
                return jsonify({"error": "First name cannot be empty"}), 400
            update_fields.append("first_name = %s")
            params.append(first_name)
        
        if 'last_name' in data:
            last_name = data['last_name'].strip()
            if not last_name:
                return jsonify({"error": "Last name cannot be empty"}), 400
            update_fields.append("last_name = %s")
            params.append(last_name)
        
        if 'phone_number' in data:
            phone_number = data['phone_number'].strip()
            if phone_number and not validate_phone(phone_number):
                return jsonify({"error": "Invalid phone number format"}), 400
            update_fields.append("phone_number = %s")
            params.append(phone_number if phone_number else None)
        
        if 'biography' in data:
            biography = data['biography'].strip()
            if len(biography) > 500:
                return jsonify({"error": "Biography must be 500 characters or less"}), 400
            update_fields.append("biography = %s")
            params.append(biography if biography else None)
        
        # Create database connection early if we need to check for old photo
        conn = None
        cursor = None
        if 'profile_photo' in data:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            profile_photo = data['profile_photo'].strip()
            # Convert empty string to None
            new_photo_value = profile_photo if profile_photo else None
            
            # Get the old photo URL to delete it if needed
            cursor.execute("SELECT profile_photo FROM users WHERE id = %s", (user_id,))
            old_user = cursor.fetchone()
            old_photo = old_user['profile_photo'] if old_user else None
            
            # Delete old photo file if it exists and we're changing/removing the photo
            # This triggers when: 1) old photo exists, 2) new value is different, 3) old photo is a local upload
            if old_photo and old_photo != new_photo_value and old_photo.startswith('/static/uploads/'):
                try:
                    old_filename = old_photo.split('/static/uploads/')[-1]
                    old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                        print(f"Deleted old profile photo: {old_filepath}")
                    else:
                        print(f"Old photo file not found: {old_filepath}")
                except Exception as e:
                    print(f"Error deleting old photo: {str(e)}")
            
            update_fields.append("profile_photo = %s")
            params.append(new_photo_value)
        
        if not update_fields:
            if conn:
                cursor.close()
                conn.close()
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Add user_id parameter
        params.append(user_id)
        
        # Create connection if not already created
        if not conn:
            conn = get_db_connection()
            cursor = conn.cursor()
        
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = %s AND is_active = TRUE
            RETURNING id, email, first_name, last_name, phone_number, 
                      biography, profile_photo, role, is_verified, date_joined
        """
        
        cursor.execute(query, params)
        updated_user = cursor.fetchone()
        
        if not updated_user:
            cursor.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": updated_user['id'],
                "email": updated_user['email'],
                "first_name": updated_user['first_name'],
                "last_name": updated_user['last_name'],
                "phone_number": updated_user['phone_number'],
                "biography": updated_user['biography'],
                "profile_photo": updated_user['profile_photo'],
                "role": updated_user['role'],
                "is_verified": updated_user['is_verified'],
                "date_joined": updated_user['date_joined'].isoformat() if updated_user['date_joined'] else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Password Reset Endpoints

@app.route("/api/auth/forgot-password", methods=['POST'])
def forgot_password():
    """Request password reset - generates a reset token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if user exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, first_name FROM users 
            WHERE email = %s AND is_active = TRUE
        """, (email,))
        
        user = cursor.fetchone()
        
        # Even if user doesn't exist, return success to avoid email enumeration
        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                "message": "If an account with that email exists, a password reset link will be sent.",
                "note": "In production, this would be sent via email"
            }), 200
        
        # Generate reset token
        reset_token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'purpose': 'password_reset',
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Store reset token in database
        cursor.execute("""
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, (user['id'], reset_token, datetime.now(timezone.utc) + timedelta(hours=1)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Get base URL from environment or request
        base_url = os.environ.get('BASE_URL')
        if not base_url:
            # Fallback to constructing from request
            base_url = request.url_root.rstrip('/')
        
        # In production, send email with reset link
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        return jsonify({
            "message": "Password reset link has been sent to your email.",
            "reset_token": reset_token,
            "reset_link": reset_link,
            "note": "In production, this would be sent via email. Token expires in 1 hour."
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/auth/reset-password", methods=['POST'])
def reset_password():
    """Reset password using the reset token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not token or not new_password or not confirm_password:
            return jsonify({"error": "Token, new password, and confirmation are required"}), 400
        
        # Check if passwords match
        if new_password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Decode and verify token
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Verify purpose is password reset
            if payload.get('purpose') != 'password_reset':
                return jsonify({"error": "Invalid reset token"}), 400
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Reset token has expired. Please request a new one."}), 400
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid reset token"}), 400
        
        # Check if token exists and is not used
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, is_used, expires_at 
            FROM password_reset_tokens 
            WHERE token = %s
        """, (token,))
        
        reset_record = cursor.fetchone()
        
        if not reset_record:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid reset token"}), 400
        
        if reset_record['is_used']:
            cursor.close()
            conn.close()
            return jsonify({"error": "This reset token has already been used"}), 400
        
        # Make expires_at timezone-aware for comparison
        expires_at = reset_record['expires_at']
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            cursor.close()
            conn.close()
            return jsonify({"error": "Reset token has expired"}), 400
        
        # Hash new password
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update user password
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE id = %s
        """, (password_hash, user_id))
        
        # Mark token as used
        cursor.execute("""
            UPDATE password_reset_tokens 
            SET is_used = TRUE 
            WHERE id = %s
        """, (reset_record['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Password has been reset successfully! You can now log in with your new password."
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Service Management Endpoints

@app.route("/api/tags", methods=['GET'])
def get_tags():
    """Get all approved tags"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name FROM tags 
            WHERE is_approved = TRUE 
            ORDER BY name
        """)
        
        tags = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "tags": [{"id": tag['id'], "name": tag['name']} for tag in tags]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/tags", methods=['POST'])
def create_tag():
    """Create a new tag (user-suggested)"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        tag_name = data.get('name', '').strip()
        
        if not tag_name:
            return jsonify({"error": "Tag name is required"}), 400
        
        # Normalize tag name: capitalize first letter of each word
        tag_name_normalized = ' '.join(word.capitalize() for word in tag_name.split())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tag already exists (case-insensitive)
        cursor.execute("SELECT id, name FROM tags WHERE LOWER(name) = LOWER(%s)", (tag_name_normalized,))
        existing_tag = cursor.fetchone()
        
        if existing_tag:
            cursor.close()
            conn.close()
            return jsonify({
                "error": "Tag already exists", 
                "tag": {"id": existing_tag['id'], "name": existing_tag['name']}
            }), 409
        
        # Create new tag with normalized name
        cursor.execute("""
            INSERT INTO tags (name, created_by, is_approved)
            VALUES (%s, %s, TRUE)
            RETURNING id, name
        """, (tag_name_normalized, user_id))
        
        new_tag = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Tag created successfully",
            "tag": {"id": new_tag['id'], "name": new_tag['name']}
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/tags/search", methods=['GET'])
def search_tags():
    """Search tags by query string"""
    try:
        # Get search query from URL parameter
        query = request.args.get('q', '').strip().lower()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if query:
            # Search tags that contain the query string
            cursor.execute("""
                SELECT id, name FROM tags 
                WHERE is_approved = TRUE 
                AND LOWER(name) LIKE %s
                ORDER BY 
                    CASE WHEN LOWER(name) = %s THEN 0 ELSE 1 END,
                    name
                LIMIT 10
            """, (f'%{query}%', query))
        else:
            # Return all tags if no query
            cursor.execute("""
                SELECT id, name FROM tags 
                WHERE is_approved = TRUE 
                ORDER BY name
                LIMIT 10
            """)
        
        tags = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "tags": [{"id": tag['id'], "name": tag['name']} for tag in tags]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services", methods=['POST'])
def create_service():
    """Create a new service (offer or need)"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_type', 'title', 'description', 'hours_required', 'location_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        service_type = data['service_type']
        if service_type not in ['offer', 'need']:
            return jsonify({"error": "service_type must be 'offer' or 'need'"}), 400
        
        title = data['title'].strip()
        description = data['description'].strip()
        hours_required = float(data['hours_required'])
        location_type = data['location_type']
        
        # Validate that title and description are not empty after stripping
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        if not description:
            return jsonify({"error": "description cannot be empty"}), 400
        
        # Validate hours_required: must be an integer between 1 and 3
        if hours_required != int(hours_required):
            return jsonify({"error": "hours_required must be an integer (1, 2, or 3), not a decimal"}), 400
        
        hours_required = int(hours_required)
        
        if hours_required < 1 or hours_required > 3:
            return jsonify({"error": "hours_required must be between 1 and 3"}), 400
        
        if location_type not in ['online', 'in-person', 'both']:
            return jsonify({"error": "location_type must be 'online', 'in-person', or 'both'"}), 400
        
        location_address = data.get('location_address')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        service_date = data.get('service_date')  # Date when service is needed (for needs)
        start_time = data.get('start_time')  # For needs
        end_time = data.get('end_time')  # For needs
        tag_ids = data.get('tag_ids', [])
        availability = data.get('availability', [])  # [{day_of_week: 0-6, start_time: "HH:MM", end_time: "HH:MM"}] - For offers
    
        # Validate that in-person and both services have location coordinates
        if location_type in ['in-person', 'both']:
            if not latitude or not longitude:
                return jsonify({"error": "Location coordinates (latitude and longitude) are required for in-person services. Please select a location on the map."}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert service
        cursor.execute("""
            INSERT INTO services (
                user_id, service_type, title, description, hours_required,
                location_type, location_address, latitude, longitude, service_date,
                start_time, end_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, service_type, title, description, hours_required,
              location_type, location_address, latitude, longitude, service_date,
              start_time, end_time))
        
        service_id = cursor.fetchone()['id']
        
        # Insert tags
        for tag_id in tag_ids:
            cursor.execute("""
                INSERT INTO service_tags (service_id, tag_id)
                VALUES (%s, %s)
            """, (service_id, tag_id))
        
        # Insert availability
        for avail in availability:
            cursor.execute("""
                INSERT INTO service_availability (service_id, day_of_week, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (service_id, avail['day_of_week'], avail['start_time'], avail['end_time']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"{service_type.capitalize()} created successfully",
            "service_id": service_id
        }), 201
        
    except ValueError as e:
        return jsonify({"error": "Invalid number format for hours_required"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services", methods=['GET'])
def get_services():
    """Get all services with optional filters"""
    try:
        service_type = request.args.get('type')  # 'offer' or 'need'
        tag_ids = request.args.getlist('tag_ids')  # List of tag IDs
        status = request.args.get('status', 'open')
        include_own_in_progress = request.args.get('include_own_in_progress') == 'true'
        
        # Get user ID if authenticated (for filtering own services)
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and include_own_in_progress:
            user_id, error, status_code = get_user_from_token(auth_header)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT s.*, 
                   u.first_name, u.last_name, u.profile_photo,
                   ARRAY_AGG(DISTINCT t.name) as tags,
                   sp.id as progress_id,
                   sp.status as progress_status,
                   sp.consumer_id,
                   sp.provider_id as progress_provider_id
            FROM services s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN service_tags st ON s.id = st.service_id
            LEFT JOIN tags t ON st.tag_id = t.id
            LEFT JOIN LATERAL (
                SELECT id, status, consumer_id, provider_id
                FROM service_progress
                WHERE service_id = s.id
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
                LIMIT 1
            ) sp ON true
        """
        
        params = []
        where_added = False
        
        # Handle status filter
        if status != 'all':
            if user_id and include_own_in_progress:
                # Show open services AND in_progress/completed services owned by the user
                # Also show in_progress offers (they remain public unless disabled)
                query += " WHERE (s.status = %s OR ((s.status = 'in_progress' OR s.status = 'completed') AND s.user_id = %s) OR (s.status = 'in_progress' AND s.service_type = 'offer'))"
                params.append(status)
                params.append(user_id)
                where_added = True
            else:
                # Show open services + in_progress offers (offers remain public)
                query += " WHERE (s.status = %s OR (s.status = 'in_progress' AND s.service_type = 'offer'))"
                params.append(status)
                where_added = True
        else:
            where_added = False
        
        if service_type:
            if where_added:
                query += " AND s.service_type = %s"
            else:
                query += " WHERE s.service_type = %s"
                where_added = True
            params.append(service_type)
        
        if tag_ids:
            placeholders = ','.join(['%s'] * len(tag_ids))
            if where_added:
                query += f" AND s.id IN (SELECT service_id FROM service_tags WHERE tag_id IN ({placeholders}))"
            else:
                query += f" WHERE s.id IN (SELECT service_id FROM service_tags WHERE tag_id IN ({placeholders}))"
                where_added = True
            params.extend(tag_ids)
        
        query += " GROUP BY s.id, u.first_name, u.last_name, u.profile_photo, sp.id, sp.status, sp.consumer_id, sp.provider_id ORDER BY s.created_at DESC"
        
        cursor.execute(query, tuple(params))
        services = cursor.fetchall()
        
        result = []
        for service in services:
            result.append({
                "id": service['id'],
                "provider_id": service['user_id'],
                "service_type": service['service_type'],
                "title": service['title'],
                "description": service['description'],
                "duration_hours": float(service['hours_required']),
                "hours_cost": float(service['hours_required']),
                "location_type": service['location_type'],
                "location": service['location_address'],
                "latitude": float(service['latitude']) if service['latitude'] else None,
                "longitude": float(service['longitude']) if service['longitude'] else None,
                "status": service['status'],
                "service_date": service['service_date'].isoformat() if service.get('service_date') else None,
                "start_time": str(service['start_time']) if service.get('start_time') else None,
                "end_time": str(service['end_time']) if service.get('end_time') else None,
                "created_at": service['created_at'].isoformat(),
                "provider_name": f"{service['first_name']} {service['last_name']}",
                "provider_photo": service['profile_photo'],
                "tags": service['tags'] if service['tags'][0] else [],
                "progress_id": service.get('progress_id'),
                "progress_status": service.get('progress_status'),
                "progress_consumer_id": service.get('consumer_id'),
                "progress_provider_id": service.get('progress_provider_id')
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services/<int:service_id>", methods=['GET'])
def get_service(service_id):
    """Get a specific service by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, 
                   u.first_name, u.last_name, u.email, u.phone_number, 
                   u.biography, u.profile_photo, u.date_joined,
                   ARRAY_AGG(DISTINCT t.name) as tags,
                   ARRAY_AGG(DISTINCT jsonb_build_object(
                       'day_of_week', sa.day_of_week,
                       'start_time', sa.start_time::text,
                       'end_time', sa.end_time::text
                   )) as availability
            FROM services s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN service_tags st ON s.id = st.service_id
            LEFT JOIN tags t ON st.tag_id = t.id
            LEFT JOIN service_availability sa ON s.id = sa.service_id
            WHERE s.id = %s
            GROUP BY s.id, u.first_name, u.last_name, u.email, u.phone_number, u.biography, u.profile_photo, u.date_joined
        """, (service_id,))
        
        service = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not service:
            return jsonify({"error": "Service not found"}), 404
        
        return jsonify({
            "service": {
                "id": service['id'],
                "service_type": service['service_type'],
                "title": service['title'],
                "description": service['description'],
                "hours_required": float(service['hours_required']),
                "location_type": service['location_type'],
                "location_address": service['location_address'],
                "latitude": float(service['latitude']) if service['latitude'] else None,
                "longitude": float(service['longitude']) if service['longitude'] else None,
                "status": service['status'],
                "service_date": service['service_date'].isoformat() if service.get('service_date') else None,
                "start_time": str(service['start_time']) if service.get('start_time') else None,
                "end_time": str(service['end_time']) if service.get('end_time') else None,
                "created_at": service['created_at'].isoformat(),
                "provider": {
                    "id": service['user_id'],
                    "first_name": service['first_name'],
                    "last_name": service['last_name'],
                    "email": service['email'],
                    "phone_number": service['phone_number'],
                    "biography": service['biography'],
                    "profile_photo": service['profile_photo'],
                    "date_joined": service['date_joined'].isoformat() if service.get('date_joined') else None
                },
                "tags": service['tags'] if service['tags'][0] else [],
                "availability": service['availability'] if service['availability'][0] else []
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services/<int:service_id>/user-application", methods=['GET'])
def get_user_application_for_service(service_id):
    """Check if the current user has an application for this service OR owns the service with accepted applications"""
    try:
        # Get user from token (optional - can be anonymous)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"has_application": False}), 200
        
        user_id, error, status = get_user_from_token(auth_header)
        if error:
            return jsonify({"has_application": False}), 200
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, check if user is the service owner
        cursor.execute("""
            SELECT user_id, service_type 
            FROM services 
            WHERE id = %s
        """, (service_id,))
        
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"has_application": False}), 200
        
        is_service_owner = (service['user_id'] == user_id)
        
        # Case 1: User applied to this service (as provider)
        if not is_service_owner:
            cursor.execute("""
                SELECT 
                    sa.id as application_id,
                    sa.status as application_status,
                    sa.applied_at,
                    s.service_type,
                    s.user_id as service_owner_id,
                    sp.id as progress_id,
                    sp.status as progress_status
                FROM service_applications sa
                JOIN services s ON sa.service_id = s.id
                LEFT JOIN service_progress sp ON sa.id = sp.application_id
                WHERE sa.service_id = %s AND sa.applicant_id = %s
                ORDER BY sa.applied_at DESC
                LIMIT 1
            """, (service_id, user_id))
            
            application = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not application:
                return jsonify({"has_application": False}), 200
            
            # Use unified progress page for providers
            progress_page = 'progress-provider'
            
            return jsonify({
                "has_application": True,
                "application_id": application['application_id'],
                "application_status": application['application_status'],
                "progress_id": application['progress_id'],
                "progress_status": application['progress_status'],
                "progress_page": progress_page,
                "redirect_url": f"/{progress_page}?application_id={application['application_id']}"
            }), 200
        
        # Case 2: User owns the service (consumer) - check for accepted applications with progress
        else:
            cursor.execute("""
                SELECT 
                    sa.id as application_id,
                    sa.status as application_status,
                    sa.applied_at,
                    s.service_type,
                    sp.id as progress_id,
                    sp.status as progress_status
                FROM service_applications sa
                JOIN services s ON sa.service_id = s.id
                LEFT JOIN service_progress sp ON sa.id = sp.application_id
                WHERE sa.service_id = %s 
                  AND sa.status = 'accepted'
                  AND sp.id IS NOT NULL
                ORDER BY sp.created_at DESC
                LIMIT 1
            """, (service_id,))
            
            application = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not application:
                # No accepted applications with progress yet
                return jsonify({"has_application": False}), 200
            
            # Determine progress page based on service type
            # For offers: owner is provider, for needs: owner is consumer
            if application['service_type'] == 'offer':
                progress_page = "progress-provider"
            else:  # need
                progress_page = "progress-consumer"
            
            # Service owner with accepted application
            return jsonify({
                "has_application": True,
                "application_id": application['application_id'],
                "application_status": application['application_status'],
                "progress_id": application['progress_id'],
                "progress_status": application['progress_status'],
                "progress_page": progress_page,
                "redirect_url": f"/{progress_page}?application_id={application['application_id']}"
            }), 200
        
    except Exception as e:
        print(f"ERROR in get_user_application_for_service: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services/<int:service_id>", methods=['PUT'])
def update_service(service_id):
    """Update a service"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if service exists and belongs to user
        cursor.execute("SELECT user_id FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        if service['user_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append("title = %s")
            params.append(data['title'])
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        if 'hours_required' in data:
            hours_val = float(data['hours_required'])
            if hours_val < 1.0 or hours_val > 3.0:
                cursor.close()
                conn.close()
                return jsonify({"error": "hours_required must be between 1.0 and 3.0"}), 400
            update_fields.append("hours_required = %s")
            params.append(hours_val)
        if 'location_type' in data:
            update_fields.append("location_type = %s")
            params.append(data['location_type'])
        if 'location_address' in data:
            update_fields.append("location_address = %s")
            params.append(data['location_address'])
        if 'latitude' in data:
            update_fields.append("latitude = %s")
            params.append(float(data['latitude']) if data['latitude'] else None)
        if 'longitude' in data:
            update_fields.append("longitude = %s")
            params.append(float(data['longitude']) if data['longitude'] else None)
        if 'status' in data:
            update_fields.append("status = %s")
            params.append(data['status'])
        
        # Handle service_date, start_time, end_time for needs
        if 'service_date' in data:
            update_fields.append("service_date = %s")
            params.append(data['service_date'])
        if 'start_time' in data:
            update_fields.append("start_time = %s")
            params.append(data['start_time'])
        if 'end_time' in data:
            update_fields.append("end_time = %s")
            params.append(data['end_time'])
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(service_id)
        
        if update_fields:
            query = f"UPDATE services SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, params)
        
        # Update tags if provided
        if 'tag_ids' in data:
            # Delete existing tags
            cursor.execute("DELETE FROM service_tags WHERE service_id = %s", (service_id,))
            
            # Insert new tags
            for tag_id in data['tag_ids']:
                cursor.execute(
                    "INSERT INTO service_tags (service_id, tag_id) VALUES (%s, %s)",
                    (service_id, tag_id)
                )
        
        # Update availability if provided (for offers)
        if 'availability' in data:
            # Delete existing availability
            cursor.execute("DELETE FROM service_availability WHERE service_id = %s", (service_id,))
            
            # Insert new availability
            for slot in data['availability']:
                cursor.execute("""
                    INSERT INTO service_availability (service_id, day_of_week, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                """, (service_id, slot['day_of_week'], slot['start_time'], slot['end_time']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Service updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services/<int:service_id>", methods=['DELETE'])
def delete_service(service_id):
    """Delete a service"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if service exists and belongs to user
        cursor.execute("SELECT user_id FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        if service['user_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Delete service (cascade will handle related records)
        cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Service deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ============= Service Applications API =============

@app.route("/api/services/<int:service_id>/apply", methods=['POST'])
def apply_to_service(service_id):
    """Apply to a service (offer or need)"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if service exists and is open
        cursor.execute("""
            SELECT id, user_id, service_type, status, title 
            FROM services 
            WHERE id = %s
        """, (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        # Can't apply to your own service
        if service['user_id'] == user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Cannot apply to your own service"}), 400
        
        # Can only apply to open services
        if service['status'] != 'open':
            cursor.close()
            conn.close()
            return jsonify({"error": "This service is no longer accepting applications"}), 400
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        # Message is required
        if not message:
            cursor.close()
            conn.close()
            return jsonify({"error": "A message is required to apply to this service"}), 400
        
        # Check if already applied
        cursor.execute("""
            SELECT id, status FROM service_applications 
            WHERE service_id = %s AND applicant_id = %s
        """, (service_id, user_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            if existing['status'] == 'rejected':
                return jsonify({"error": "You cannot apply to this service because your previous application was rejected"}), 403
            return jsonify({"error": "You have already applied to this service"}), 400
        
        # Create application
        cursor.execute("""
            INSERT INTO service_applications (service_id, applicant_id, message, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING id, applied_at
        """, (service_id, user_id, message))
        
        application = cursor.fetchone()
        application_id = application['id']
        
        # Automatically create the initial message in the messages table
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, application_id, service_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, service['user_id'], message, application_id, service_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Application submitted successfully",
            "application_id": application_id,
            "applied_at": application['applied_at'].isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/services/<int:service_id>/applications", methods=['GET'])
def get_service_applications(service_id):
    """Get all applications for a service (only for service owner)"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if service belongs to user
        cursor.execute("SELECT user_id FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        if service['user_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get applications with applicant details and progress info (updated from transactions)
        cursor.execute("""
            SELECT 
                sa.id,
                sa.status,
                sa.message,
                sa.applied_at,
                sa.updated_at,
                u.id as applicant_id,
                u.first_name,
                u.last_name,
                u.profile_photo,
                u.biography,
                u.date_joined,
                sp.id as progress_id,
                sp.id as transaction_id,
                sp.status as progress_status,
                sp.status as transaction_status,
                sp.hours as transaction_hours
            FROM service_applications sa
            JOIN users u ON sa.applicant_id = u.id
            LEFT JOIN service_progress sp ON sa.id = sp.application_id
            WHERE sa.service_id = %s
            ORDER BY sa.applied_at DESC
        """, (service_id,))
        
        applications = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify([dict(app) for app in applications]), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/applications/<int:application_id>/accept", methods=['POST'])
def accept_application(application_id):
    """Accept an application and create a transaction"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get application details
        cursor.execute("""
            SELECT sa.*, s.user_id as service_owner_id, s.service_type, s.hours_required
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            WHERE sa.id = %s
        """, (application_id,))
        
        application = cursor.fetchone()
        
        if not application:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        # Only service owner can accept
        if application['service_owner_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        if application['status'] != 'pending':
            cursor.close()
            conn.close()
            return jsonify({"error": "Application is no longer pending"}), 400
        
        # Update application status
        cursor.execute("""
            UPDATE service_applications 
            SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (application_id,))
        
        # Reject other applications for this service
        cursor.execute("""
            UPDATE service_applications 
            SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
            WHERE service_id = %s AND id != %s AND status = 'pending'
        """, (application['service_id'], application_id))
        
        # Update service status
        cursor.execute("""
            UPDATE services 
            SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (application['service_id'],))
        
        # Determine provider and consumer based on service type
        if application['service_type'] == 'offer':
            provider_id = application['service_owner_id']
            consumer_id = application['applicant_id']
        else:  # need
            provider_id = application['applicant_id']
            consumer_id = application['service_owner_id']
        
        # NOTE: We don't validate time balance here because:
        # 1. User might earn more hours before the service starts
        # 2. Schedule isn't confirmed yet
        # Validation happens when schedule is accepted or service starts
        
        # Create progress tracking (replaces old transaction)
        # Status starts as 'selected' - next step will be to schedule it
        cursor.execute("""
            INSERT INTO service_progress (
                service_id, application_id, provider_id, consumer_id, hours, 
                status, selected_at
            )
            VALUES (%s, %s, %s, %s, %s, 'selected', NOW())
            RETURNING id
        """, (application['service_id'], application_id, provider_id, consumer_id, application['hours_required']))
        
        progress = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Application accepted successfully",
            "progress_id": progress['id'],
            "transaction_id": progress['id']  # For backwards compatibility
        }), 200
        
    except Exception as e:
        print(f"ERROR in accept_application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/applications/<int:application_id>/withdraw", methods=['POST'])
def withdraw_application(application_id):
    """Withdraw/cancel a pending application"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get application details
        cursor.execute("""
            SELECT sa.*, s.title as service_title
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            WHERE sa.id = %s
        """, (application_id,))
        
        application = cursor.fetchone()
        
        if not application:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        # Only the applicant can withdraw their own application
        if application['applicant_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized - You can only withdraw your own applications"}), 403
        
        # Can only withdraw pending applications
        if application['status'] != 'pending':
            cursor.close()
            conn.close()
            return jsonify({"error": f"Cannot withdraw application with status '{application['status']}'. Only pending applications can be withdrawn."}), 400
        
        # Update application status to withdrawn
        cursor.execute("""
            UPDATE service_applications 
            SET status = 'withdrawn', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (application_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Application withdrawn successfully",
            "application_id": application_id,
            "service_title": application['service_title']
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ============= Messages API =============

@app.route("/api/messages", methods=['POST'], strict_slashes=False)
def send_message():
    """Send a message"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        message = data.get('message')
        application_id = data.get('application_id')
        service_id = data.get('service_id')
        
        if not receiver_id or not message:
            return jsonify({"error": "receiver_id and message are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the service progress is cancelled
        if application_id:
            cursor.execute("""
                SELECT sp.status
                FROM service_progress sp
                WHERE sp.application_id = %s
            """, (application_id,))
            
            progress = cursor.fetchone()
            if progress and progress['status'] == 'cancelled':
                cursor.close()
                conn.close()
                return jsonify({"error": "Cannot send messages for a cancelled service"}), 400
        
        # Create message
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, application_id, service_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (user_id, receiver_id, message, application_id, service_id))
        
        new_message = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Message sent successfully",
            "message_id": new_message['id'],
            "created_at": new_message['created_at'].isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/messages", methods=['GET'], strict_slashes=False)
def get_user_conversations():
    """Get all conversations for the current user"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all applications where user is either applicant or service owner
        cursor.execute("""
            SELECT
                sa.id as application_id,
                s.id as service_id,
                s.title as service_title,
                s.service_type,
                s.hours_required,
                sa.status as application_status,
                sa.applied_at as application_date,
                sp.status as progress_status,
                sp.hours as transaction_hours,
                CASE 
                    WHEN sa.applicant_id = %s THEN provider.id
                    ELSE applicant.id
                END as other_user_id,
                CASE 
                    WHEN sa.applicant_id = %s THEN provider.first_name || ' ' || provider.last_name
                    ELSE applicant.first_name || ' ' || applicant.last_name
                END as other_user_name,
                CASE 
                    WHEN sa.applicant_id = %s THEN provider.profile_photo
                    ELSE applicant.profile_photo
                END as other_user_photo,
                (SELECT COUNT(*) 
                 FROM messages 
                 WHERE application_id = sa.id 
                 AND receiver_id = %s 
                 AND is_read = FALSE) as unread_count,
                (SELECT m.message 
                 FROM messages m 
                 WHERE m.application_id = sa.id 
                 ORDER BY m.created_at DESC 
                 LIMIT 1) as last_message,
                (SELECT m.created_at 
                 FROM messages m 
                 WHERE m.application_id = sa.id 
                 ORDER BY m.created_at DESC 
                 LIMIT 1) as last_message_time,
                (SELECT COUNT(*) FROM messages WHERE application_id = sa.id) as message_count
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            JOIN users applicant ON sa.applicant_id = applicant.id
            JOIN users provider ON s.user_id = provider.id
            LEFT JOIN service_progress sp ON sa.id = sp.application_id
            WHERE (sa.applicant_id = %s OR s.user_id = %s)
            ORDER BY 
                COALESCE(
                    (SELECT MAX(m.created_at) FROM messages m WHERE m.application_id = sa.id),
                    sa.applied_at
                ) DESC
        """, (user_id, user_id, user_id, user_id, user_id, user_id))
        
        conversations = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"conversations": [dict(conv) for conv in conversations]}), 200
        
    except Exception as e:
        print(f"Error in get_user_conversations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/applications/<int:application_id>/messages", methods=['GET'])
def get_application_messages(application_id):
    """Get all messages for an application"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user is part of this application
        cursor.execute("""
            SELECT sa.applicant_id, s.user_id as service_owner_id
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            WHERE sa.id = %s
        """, (application_id,))
        
        application = cursor.fetchone()
        
        if not application:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        if user_id not in [application['applicant_id'], application['service_owner_id']]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get messages
        cursor.execute("""
            SELECT 
                m.id,
                m.message,
                m.is_read,
                m.created_at,
                m.message_type,
                m.proposal_date,
                m.proposal_start_time,
                m.proposal_end_time,
                m.proposal_location,
                m.proposal_status,
                m.sender_id,
                m.receiver_id,
                sender.first_name as sender_first_name,
                sender.last_name as sender_last_name,
                sender.profile_photo as sender_photo
            FROM messages m
            JOIN users sender ON m.sender_id = sender.id
            WHERE m.application_id = %s
            ORDER BY m.created_at ASC
        """, (application_id,))
        
        messages = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        serialized_messages = []
        for msg in messages:
            msg_dict = dict(msg)
            # Convert date and time objects to strings
            if msg_dict.get('proposal_date'):
                msg_dict['proposal_date'] = msg_dict['proposal_date'].isoformat()
            if msg_dict.get('proposal_start_time'):
                msg_dict['proposal_start_time'] = msg_dict['proposal_start_time'].strftime('%H:%M')
            if msg_dict.get('proposal_end_time'):
                msg_dict['proposal_end_time'] = msg_dict['proposal_end_time'].strftime('%H:%M')
            if msg_dict.get('created_at'):
                msg_dict['created_at'] = msg_dict['created_at'].isoformat()
            serialized_messages.append(msg_dict)
        
        # Mark messages as read
        cursor.execute("""
            UPDATE messages 
            SET is_read = TRUE 
            WHERE application_id = %s AND receiver_id = %s
        """, (application_id, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(serialized_messages), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/user/applications", methods=['GET'])
def get_user_applications():
    """Get all applications submitted by the current user"""
    try:
        # Get user from token
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        print(f"DEBUG: Loading applications for user_id: {user_id}")
        
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get applications with service details and progress info (updated from transactions)
        cursor.execute("""
            SELECT 
                sa.id as application_id,
                sa.status as application_status,
                sa.message as application_message,
                sa.applied_at,
                sa.updated_at,
                s.id as service_id,
                s.title as service_title,
                s.description as service_description,
                s.service_type,
                s.hours_required,
                s.location_type,
                s.location_address,
                s.status as service_status,
                owner.id as owner_id,
                owner.first_name as owner_first_name,
                owner.last_name as owner_last_name,
                owner.profile_photo as owner_photo,
                sp.id as progress_id,
                sp.id as transaction_id,
                sp.status as progress_status,
                sp.status as transaction_status,
                sp.hours as transaction_hours
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            JOIN users owner ON s.user_id = owner.id
            LEFT JOIN service_progress sp ON sa.id = sp.application_id
            WHERE sa.applicant_id = %s
            ORDER BY sa.applied_at DESC
        """, (user_id,))
        
        applications = cursor.fetchall()
        
        print(f"DEBUG: Found {len(applications)} applications")
        if applications:
            print(f"DEBUG: First application keys: {applications[0].keys()}")
            print(f"DEBUG: First application transaction_hours: {applications[0].get('transaction_hours')}")
        
        cursor.close()
        conn.close()
        
        return jsonify([dict(app) for app in applications]), 200
        
    except Exception as e:
        print(f"ERROR in get_user_applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ===== SERVICE PROGRESS TRACKING APIS =====

@app.route("/api/applications/<int:application_id>/progress", methods=['GET'])
def get_application_progress(application_id):
    """Get progress tracking for an application"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user is part of this application
        cursor.execute("""
            SELECT sa.id, sa.applicant_id, s.user_id as service_owner_id
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            WHERE sa.id = %s
        """, (application_id,))
        
        app = cursor.fetchone()
        if not app:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        if user_id not in [app['applicant_id'], app['service_owner_id']]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get progress details
        cursor.execute("""
            SELECT 
                sp.*,
                s.title as service_title,
                s.service_type,
                s.hours_required,
                s.location_address,
                s.service_date,
                s.start_time,
                s.end_time,
                s.created_at as service_created_at,
                s.description as service_description,
                provider.id as provider_id,
                provider.first_name || ' ' || provider.last_name as provider_name,
                provider.profile_photo as provider_photo,
                consumer.id as consumer_id,
                consumer.first_name || ' ' || consumer.last_name as consumer_name,
                consumer.profile_photo as consumer_photo
            FROM service_progress sp
            JOIN services s ON sp.service_id = s.id
            JOIN users provider ON sp.provider_id = provider.id
            JOIN users consumer ON sp.consumer_id = consumer.id
            WHERE sp.application_id = %s
        """, (application_id,))
        
        progress = cursor.fetchone()
        
        # Get availability for offers
        availability = []
        if progress and progress['service_type'] == 'offer':
            cursor.execute("""
                SELECT day_of_week, start_time, end_time
                FROM service_availability
                WHERE service_id = %s
                ORDER BY day_of_week
            """, (progress['service_id'],))
            availability = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if progress:
            # Convert to dict and handle time objects
            progress_dict = dict(progress)
            # Convert time objects to strings
            if progress_dict.get('start_time'):
                progress_dict['start_time'] = str(progress_dict['start_time'])
            if progress_dict.get('end_time'):
                progress_dict['end_time'] = str(progress_dict['end_time'])
            if progress_dict.get('scheduled_time'):
                progress_dict['scheduled_time'] = str(progress_dict['scheduled_time'])
            if progress_dict.get('proposed_time'):
                progress_dict['proposed_time'] = str(progress_dict['proposed_time'])
            
            # Add availability data
            if availability:
                progress_dict['availability'] = [
                    {
                        'day_of_week': a['day_of_week'],
                        'start_time': str(a['start_time']),
                        'end_time': str(a['end_time'])
                    }
                    for a in availability
                ]
            else:
                progress_dict['availability'] = []
            
            # Determine who the "other user" is based on current user
            is_provider = (user_id == progress_dict['provider_id'])
            
            if is_provider:
                # Current user is provider, other user is consumer
                other_user = {
                    "id": progress_dict['consumer_id'],
                    "full_name": progress_dict['consumer_name'],
                    "photo": progress_dict['consumer_photo']
                }
            else:
                # Current user is consumer, other user is provider
                other_user = {
                    "id": progress_dict['provider_id'],
                    "full_name": progress_dict['provider_name'],
                    "photo": progress_dict['provider_photo']
                }
            
            # Add is_provider to progress dict
            progress_dict['is_provider'] = is_provider
            
            # Structure the response to match frontend expectations
            return jsonify({
                "progress": progress_dict,
                "application": {
                    "id": application_id,
                    "applied_at": progress_dict.get('created_at')
                },
                "service": {
                    "id": progress_dict['service_id'],
                    "title": progress_dict['service_title'],
                    "service_type": progress_dict['service_type'],
                    "type": progress_dict['service_type'],
                    "hours_required": float(progress_dict['hours_required']),
                    "location_address": progress_dict.get('location_address'),
                    "service_date": progress_dict.get('service_date'),
                    "start_time": progress_dict.get('start_time'),
                    "end_time": progress_dict.get('end_time'),
                    "created_at": progress_dict['service_created_at'],
                    "description": progress_dict.get('service_description'),
                    "tags": ""  # Tags not included in this query
                },
                "other_user": other_user
            }), 200
        else:
            return jsonify({"progress": None}), 200
        
    except Exception as e:
        print(f"ERROR in get_application_progress: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/applications/<int:application_id>/progress", methods=['POST'])
def create_progress(application_id):
    """Create progress tracking when application is accepted (status changes to 'accepted')"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        scheduled_date = data.get('scheduled_date')
        scheduled_time = data.get('scheduled_time')
        location = data.get('location', '')
        instructions = data.get('instructions', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get application and service details
        cursor.execute("""
            SELECT 
                sa.id, sa.applicant_id, sa.service_id,
                s.user_id as service_owner_id, s.service_type, s.hours_required
            FROM service_applications sa
            JOIN services s ON sa.service_id = s.id
            WHERE sa.id = %s
        """, (application_id,))
        
        app = cursor.fetchone()
        if not app:
            cursor.close()
            conn.close()
            return jsonify({"error": "Application not found"}), 404
        
        # Only service owner can create progress
        if user_id != app['service_owner_id']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Only the service owner can accept and schedule"}), 403
        
        # Determine provider and consumer based on service type
        if app['service_type'] == 'offer':
            provider_id = app['service_owner_id']
            consumer_id = app['applicant_id']
        else:  # need
            provider_id = app['applicant_id']
            consumer_id = app['service_owner_id']
        
        # Create progress entry
        cursor.execute("""
            INSERT INTO service_progress 
            (service_id, application_id, provider_id, consumer_id, hours, status,
             scheduled_date, scheduled_time, agreed_location, special_instructions,
             selected_at, scheduled_at)
            VALUES (%s, %s, %s, %s, %s, 'scheduled', %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (app['service_id'], application_id, provider_id, consumer_id, 
              app['hours_required'], scheduled_date, scheduled_time, location, instructions))
        
        progress_id = cursor.fetchone()['id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Progress created", "progress_id": progress_id}), 201
        
    except Exception as e:
        print(f"ERROR in create_progress: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/progress/<int:progress_id>/status", methods=['PUT'])
def update_progress_status(progress_id):
    """Update progress status (start service, mark complete, etc.)"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['in_progress', 'awaiting_confirmation', 'completed', 'cancelled', 'disputed']:
            return jsonify({"error": "Invalid status"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress details
        cursor.execute("""
            SELECT provider_id, consumer_id, status 
            FROM service_progress 
            WHERE id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check authorization
        if user_id not in [progress['provider_id'], progress['consumer_id']]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Update status with timestamp
        timestamp_field = None
        if new_status == 'in_progress':
            timestamp_field = 'started_at'
        elif new_status == 'completed':
            timestamp_field = 'completed_at'
        
        if timestamp_field:
            cursor.execute(f"""
                UPDATE service_progress 
                SET status = %s, {timestamp_field} = NOW(), updated_at = NOW()
                WHERE id = %s
            """, (new_status, progress_id))
        else:
            cursor.execute("""
                UPDATE service_progress 
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """, (new_status, progress_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Status updated", "status": new_status}), 200
        
    except Exception as e:
        print(f"ERROR in update_progress_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/progress/<int:progress_id>/mark-finished", methods=['POST'])
def mark_service_finished(progress_id):
    """Mark service as finished - initiates survey process"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress details
        cursor.execute("""
            SELECT provider_id, consumer_id, status
            FROM service_progress 
            WHERE id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check if user is provider or consumer
        is_provider = user_id == progress['provider_id']
        is_consumer = user_id == progress['consumer_id']
        
        if not (is_provider or is_consumer):
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Can only mark finished from in_progress status
        if progress['status'] != 'in_progress':
            cursor.close()
            conn.close()
            return jsonify({"error": "Service must be in progress to mark as finished"}), 400
        
        # Move to awaiting_confirmation and set 24-hour deadline
        cursor.execute("""
            UPDATE service_progress 
            SET status = 'awaiting_confirmation',
                survey_deadline = NOW() + INTERVAL '24 hours',
                updated_at = NOW()
            WHERE id = %s
        """, (progress_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Service marked as finished. Please complete the confirmation form.",
            "show_survey": True
        }), 200
        
    except Exception as e:
        print(f"ERROR in mark_service_finished: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/progress/<int:progress_id>/submit-survey", methods=['POST'])
def submit_completion_survey(progress_id):
    """Submit completion survey/confirmation form"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        survey_data = data.get('survey_data', {})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress details
        cursor.execute("""
            SELECT service_id, provider_id, consumer_id, status, hours,
                   provider_survey_submitted, consumer_survey_submitted,
                   survey_deadline
            FROM service_progress 
            WHERE id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check if user is provider or consumer
        is_provider = user_id == progress['provider_id']
        is_consumer = user_id == progress['consumer_id']
        
        if not (is_provider or is_consumer):
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Must be in awaiting_confirmation status
        if progress['status'] != 'awaiting_confirmation':
            cursor.close()
            conn.close()
            return jsonify({"error": "Service is not awaiting confirmation"}), 400
        
        # Check if already submitted
        if is_provider and progress['provider_survey_submitted']:
            cursor.close()
            conn.close()
            return jsonify({"error": "You have already submitted your confirmation"}), 400
        if is_consumer and progress['consumer_survey_submitted']:
            cursor.close()
            conn.close()
            return jsonify({"error": "You have already submitted your confirmation"}), 400
        
        # Save survey data
        import json
        if is_provider:
            cursor.execute("""
                UPDATE service_progress 
                SET provider_survey_submitted = TRUE,
                    provider_survey_submitted_at = NOW(),
                    provider_survey_data = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING provider_survey_submitted, consumer_survey_submitted
            """, (json.dumps(survey_data), progress_id))
        else:
            cursor.execute("""
                UPDATE service_progress 
                SET consumer_survey_submitted = TRUE,
                    consumer_survey_submitted_at = NOW(),
                    consumer_survey_data = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING provider_survey_submitted, consumer_survey_submitted
            """, (json.dumps(survey_data), progress_id))
        
        result = cursor.fetchone()
        
        # If both surveys submitted, complete the service
        if result['provider_survey_submitted'] and result['consumer_survey_submitted']:
            # Update progress status to completed
            cursor.execute("""
                UPDATE service_progress 
                SET status = 'completed', completed_at = NOW(), updated_at = NOW()
                WHERE id = %s
            """, (progress_id,))
            
            # Update service status to completed
            cursor.execute("""
                UPDATE services 
                SET status = 'completed', updated_at = NOW()
                WHERE id = %s
            """, (progress['service_id'],))
            
            # Transfer hours: add to provider, deduct from consumer
            cursor.execute("""
                UPDATE users 
                SET time_balance = time_balance + %s 
                WHERE id = %s
            """, (progress['hours'], progress['provider_id']))
            
            cursor.execute("""
                UPDATE users 
                SET time_balance = time_balance - %s 
                WHERE id = %s
            """, (progress['hours'], progress['consumer_id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Thank you! Service completed and hours transferred.",
                "completed": True
            }), 200
        else:
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Thank you! Waiting for the other party to complete their confirmation.",
                "completed": False
            }), 200
        
    except Exception as e:
        print(f"ERROR in submit_completion_survey: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/progress/<int:progress_id>/confirm", methods=['POST'])
def confirm_progress_completion(progress_id):
    """Legacy endpoint - redirects to new survey flow"""
    return mark_service_finished(progress_id)


@app.route("/api/progress/<int:progress_id>/confirm-start", methods=['POST'])
def confirm_service_start(progress_id):
    """Confirm service has started (both provider and consumer must confirm)"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress details
        cursor.execute("""
            SELECT sp.*
            FROM service_progress sp
            WHERE sp.id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check authorization
        if user_id not in [progress['provider_id'], progress['consumer_id']]:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Check if status is 'scheduled'
        if progress['status'] != 'scheduled':
            cursor.close()
            conn.close()
            return jsonify({"error": f"Cannot confirm start. Current status: {progress['status']}"}), 400
        
        # Determine if user is provider or consumer
        is_provider = (user_id == progress['provider_id'])
        
        # Update confirmation based on role
        if is_provider:
            cursor.execute("""
                UPDATE service_progress
                SET provider_start_confirmed = TRUE,
                    provider_start_confirmed_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
            """, (progress_id,))
        else:
            cursor.execute("""
                UPDATE service_progress
                SET consumer_start_confirmed = TRUE,
                    consumer_start_confirmed_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
            """, (progress_id,))
        
        conn.commit()
        
        # Re-fetch to check if both confirmed
        cursor.execute("""
            SELECT provider_start_confirmed, consumer_start_confirmed, hours,
                   provider_id, consumer_id
            FROM service_progress
            WHERE id = %s
        """, (progress_id,))
        
        updated_progress = cursor.fetchone()
        
        # If both confirmed, validate time balance before moving to 'in_progress'
        if updated_progress['provider_start_confirmed'] and updated_progress['consumer_start_confirmed']:
            # VALIDATE TIME BALANCE BEFORE STARTING SERVICE
            is_valid, error_msg = validate_time_balance(
                cursor,
                updated_progress['consumer_id'],
                updated_progress['provider_id'],
                float(updated_progress['hours'])
            )
            
            if not is_valid:
                # Rollback the confirmations if validation fails
                cursor.execute("""
                    UPDATE service_progress
                    SET provider_start_confirmed = FALSE,
                        consumer_start_confirmed = FALSE,
                        provider_start_confirmed_at = NULL,
                        consumer_start_confirmed_at = NULL,
                        updated_at = NOW()
                    WHERE id = %s
                """, (progress_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"error": error_msg}), 400
            
            cursor.execute("""
                UPDATE service_progress
                SET status = 'in_progress',
                    started_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
            """, (progress_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Service started! Both parties confirmed.",
                "confirmed": True,
                "both_confirmed": True,
                "status": "in_progress"
            }), 200
        else:
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Start confirmation recorded. Waiting for other party.",
                "confirmed": True,
                "both_confirmed": False,
                "status": "scheduled"
            }), 200
        
    except Exception as e:
        print(f"ERROR in confirm_service_start: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/progress/<int:progress_id>/propose-schedule", methods=['POST'])
def propose_schedule_change(progress_id):
    """Propose a schedule change by sending a message with proposal"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        proposed_date = data.get('proposed_date')
        proposed_start_time = data.get('proposed_start_time')
        proposed_end_time = data.get('proposed_end_time')
        proposed_location = data.get('proposed_location')
        
        if not all([proposed_date, proposed_start_time, proposed_end_time]):
            return jsonify({"error": "Date, start time, and end time are required"}), 400
        
        # Validate time format and calculate duration
        from datetime import datetime, time
        try:
            start_time_obj = datetime.strptime(proposed_start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(proposed_end_time, '%H:%M').time()
            
            # Calculate proposed duration in hours
            start_datetime = datetime.combine(datetime.today(), start_time_obj)
            end_datetime = datetime.combine(datetime.today(), end_time_obj)
            duration_delta = end_datetime - start_datetime
            proposed_hours = duration_delta.total_seconds() / 3600
            
            if proposed_hours <= 0:
                return jsonify({"error": "End time must be after start time"}), 400
                
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM format"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress and service details including hours_required and service_type
        cursor.execute("""
            SELECT sp.provider_id, sp.consumer_id, sp.status, sp.service_id, sp.application_id,
                   s.title as service_title, s.hours_required, s.service_type
            FROM service_progress sp
            JOIN services s ON sp.service_id = s.id
            WHERE sp.id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check if progress is cancelled
        if progress['status'] == 'cancelled':
            cursor.close()
            conn.close()
            return jsonify({"error": "Cannot propose schedule for a cancelled service"}), 400
        
        # Convert hours_required to float for comparison
        hours_required = float(progress['hours_required'])
        service_type = progress['service_type']
        
        # Validate duration based on service type
        if service_type == 'offer':
            # For offers: flexible hours between 1-3
            if proposed_hours < 1:
                cursor.close()
                conn.close()
                return jsonify({
                    "error": "Proposed duration must be at least 1 hour for offers."
                }), 400
            elif proposed_hours > 3:
                cursor.close()
                conn.close()
                return jsonify({
                    "error": "Proposed duration cannot exceed 3 hours for offers."
                }), 400
        else:
            # For needs: must match exactly
            if abs(proposed_hours - hours_required) > 0.01:  # Allow small floating point differences
                cursor.close()
                conn.close()
                return jsonify({
                    "error": f"The estimated hours is {hours_required:.1f} hours. Proposed duration ({proposed_hours:.1f} hours) must match this. Please adjust the start/end time."
                }), 400
        
        # Check if user is provider or consumer
        is_provider = user_id == progress['provider_id']
        is_consumer = user_id == progress['consumer_id']
        
        if not (is_provider or is_consumer):
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Determine receiver (the other party)
        receiver_id = progress['consumer_id'] if is_provider else progress['provider_id']
        proposer_role = "provider" if is_provider else "consumer"
        
        # Create a schedule proposal message
        location_text = f" at {proposed_location}" if proposed_location else ""
        message_text = f"New schedule proposed: {proposed_date} from {proposed_start_time} to {proposed_end_time}{location_text}"
        
        cursor.execute("""
            INSERT INTO messages 
            (service_id, application_id, sender_id, receiver_id, message, 
             message_type, proposal_date, proposal_start_time, proposal_end_time, proposal_location, proposal_status)
            VALUES (%s, %s, %s, %s, %s, 'schedule_proposal', %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (progress['service_id'], progress['application_id'], user_id, receiver_id, 
              message_text, proposed_date, proposed_start_time, proposed_end_time, proposed_location))
        
        message_id = cursor.fetchone()['id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Schedule proposal sent successfully",
            "message_id": message_id,
            "proposed_by": proposer_role
        }), 200
        
    except Exception as e:
        print(f"ERROR in propose_schedule_change: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/messages/<int:message_id>/respond-schedule", methods=['POST'])
def respond_to_schedule_proposal_message(message_id):
    """Accept or reject a schedule proposal message"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        accept = data.get('accept', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get message details
        cursor.execute("""
            SELECT m.*, sp.id as progress_id, sp.service_id, s.status as service_status
            FROM messages m
            JOIN service_progress sp ON m.application_id = sp.application_id
            JOIN services s ON m.service_id = s.id
            WHERE m.id = %s AND m.message_type = 'schedule_proposal'
        """, (message_id,))
        
        message = cursor.fetchone()
        if not message:
            cursor.close()
            conn.close()
            return jsonify({"error": "Schedule proposal message not found"}), 404
        
        # Check if user is the receiver
        if user_id != message['receiver_id']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized - you are not the recipient"}), 403
        
        # Check if already responded
        if message['proposal_status'] != 'pending':
            cursor.close()
            conn.close()
            return jsonify({"error": f"Proposal already {message['proposal_status']}"}), 400
        
        if accept:
            # Calculate actual hours from proposed schedule
            from datetime import datetime, time
            try:
                # Handle both string and time object formats
                if isinstance(message['proposal_start_time'], time):
                    start_time_obj = message['proposal_start_time']
                else:
                    start_time_obj = datetime.strptime(message['proposal_start_time'], '%H:%M').time()
                
                if isinstance(message['proposal_end_time'], time):
                    end_time_obj = message['proposal_end_time']
                else:
                    end_time_obj = datetime.strptime(message['proposal_end_time'], '%H:%M').time()
                
                # Calculate duration in hours
                start_datetime = datetime.combine(datetime.today(), start_time_obj)
                end_datetime = datetime.combine(datetime.today(), end_time_obj)
                duration_delta = end_datetime - start_datetime
                scheduled_hours = duration_delta.total_seconds() / 3600
                
                if scheduled_hours <= 0:
                    cursor.close()
                    conn.close()
                    return jsonify({"error": "Invalid schedule: end time must be after start time"}), 400
                    
            except (ValueError, TypeError) as e:
                cursor.close()
                conn.close()
                return jsonify({"error": f"Invalid time format in proposal: {str(e)}"}), 400
            
            # Get progress details for validation
            cursor.execute("""
                SELECT provider_id, consumer_id
                FROM service_progress
                WHERE id = %s
            """, (message['progress_id'],))
            
            progress_detail = cursor.fetchone()
            if not progress_detail:
                cursor.close()
                conn.close()
                return jsonify({"error": "Progress not found"}), 404
            
            # VALIDATE TIME BALANCE BEFORE ACCEPTING SCHEDULE
            # Use the calculated scheduled hours, not the original hours_required
            is_valid, error_msg = validate_time_balance(
                cursor,
                progress_detail['consumer_id'],
                progress_detail['provider_id'],
                scheduled_hours
            )
            
            if not is_valid:
                cursor.close()
                conn.close()
                return jsonify({"error": error_msg}), 400
            
            # Update message status to accepted
            cursor.execute("""
                UPDATE messages 
                SET proposal_status = 'accepted',
                    is_read = TRUE
                WHERE id = %s
            """, (message_id,))
            
            # Update service schedule (and location if provided)
            if message.get('proposal_location'):
                cursor.execute("""
                    UPDATE services
                    SET service_date = %s,
                        start_time = %s,
                        end_time = %s,
                        location_address = %s
                    WHERE id = %s
                """, (message['proposal_date'], message['proposal_start_time'], 
                      message['proposal_end_time'], message['proposal_location'], message['service_id']))
            else:
                cursor.execute("""
                    UPDATE services
                    SET service_date = %s,
                        start_time = %s,
                        end_time = %s
                    WHERE id = %s
                """, (message['proposal_date'], message['proposal_start_time'], 
                      message['proposal_end_time'], message['service_id']))
            
            # Update progress status to 'scheduled' AND update hours to match actual scheduled duration
            cursor.execute("""
                UPDATE service_progress
                SET status = 'scheduled',
                    scheduled_date = %s,
                    scheduled_time = %s,
                    hours = %s,
                    scheduled_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
            """, (message['proposal_date'], message['proposal_start_time'], scheduled_hours, message['progress_id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Schedule accepted! Progress will continue.",
                "status": "accepted"
            }), 200
        else:
            # Update message status to rejected
            cursor.execute("""
                UPDATE messages 
                SET proposal_status = 'rejected',
                    is_read = TRUE
                WHERE id = %s
            """, (message_id,))
            
            # Change service back to 'open' and stop progress
            cursor.execute("""
                UPDATE services
                SET status = 'open'
                WHERE id = %s
            """, (message['service_id'],))
            
            # Update progress status to 'cancelled'
            cursor.execute("""
                UPDATE service_progress
                SET status = 'cancelled',
                    updated_at = NOW()
                WHERE id = %s
            """, (message['progress_id'],))
            
            # Update application status to 'rejected'
            cursor.execute("""
                UPDATE service_applications
                SET status = 'rejected',
                    updated_at = NOW()
                WHERE id = %s
            """, (message['application_id'],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Schedule rejected. Service is now available for others.",
                "status": "rejected"
            }), 200
        
    except Exception as e:
        print(f"ERROR in respond_to_schedule_proposal_message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/progress/<int:progress_id>/respond-schedule", methods=['POST'])
def respond_to_schedule_proposal(progress_id):
    """Accept or reject a proposed schedule change"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        accept = data.get('accept', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get progress details
        cursor.execute("""
            SELECT provider_id, consumer_id, status, hours,
                   proposed_date, proposed_time, proposed_location,
                   proposed_by, schedule_accepted_by_consumer, 
                   schedule_accepted_by_provider
            FROM service_progress 
            WHERE id = %s
        """, (progress_id,))
        
        progress = cursor.fetchone()
        if not progress:
            cursor.close()
            conn.close()
            return jsonify({"error": "Progress not found"}), 404
        
        # Check if user is provider or consumer
        is_provider = user_id == progress['provider_id']
        is_consumer = user_id == progress['consumer_id']
        
        if not (is_provider or is_consumer):
            cursor.close()
            conn.close()
            return jsonify({"error": "Unauthorized"}), 403
        
        # Check if there's a pending proposal
        if not progress['proposed_by']:
            cursor.close()
            conn.close()
            return jsonify({"error": "No pending schedule proposal"}), 400
        
        # Can't respond to own proposal
        if progress['proposed_by'] == user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "Cannot respond to your own proposal"}), 400
        
        if accept:
            # VALIDATE TIME BALANCE BEFORE ACCEPTING
            is_valid, error_msg = validate_time_balance(
                cursor, 
                progress['consumer_id'], 
                progress['provider_id'], 
                float(progress['hours'])
            )
            
            if not is_valid:
                cursor.close()
                conn.close()
                return jsonify({"error": error_msg}), 400
            
            # Set acceptance for this user
            if is_provider:
                cursor.execute("""
                    UPDATE service_progress 
                    SET schedule_accepted_by_provider = TRUE,
                        updated_at = NOW()
                    WHERE id = %s
                """, (progress_id,))
            else:
                cursor.execute("""
                    UPDATE service_progress 
                    SET schedule_accepted_by_consumer = TRUE,
                        updated_at = NOW()
                    WHERE id = %s
                """, (progress_id,))
            
            # Check if both have accepted
            cursor.execute("""
                SELECT schedule_accepted_by_consumer, schedule_accepted_by_provider,
                       proposed_date, proposed_time, proposed_location
                FROM service_progress WHERE id = %s
            """, (progress_id,))
            
            updated_progress = cursor.fetchone()
            
            if updated_progress['schedule_accepted_by_consumer'] and updated_progress['schedule_accepted_by_provider']:
                # Both accepted - apply the proposed schedule
                cursor.execute("""
                    UPDATE service_progress 
                    SET scheduled_date = proposed_date,
                        scheduled_time = proposed_time,
                        agreed_location = COALESCE(proposed_location, agreed_location),
                        proposed_date = NULL,
                        proposed_time = NULL,
                        proposed_location = NULL,
                        proposed_by = NULL,
                        proposed_at = NULL,
                        schedule_accepted_by_consumer = FALSE,
                        schedule_accepted_by_provider = FALSE,
                        scheduled_at = NOW(),
                        status = 'scheduled',
                        updated_at = NOW()
                    WHERE id = %s
                """, (progress_id,))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({
                    "message": "Schedule accepted by both parties and applied!",
                    "both_accepted": True
                }), 200
            else:
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({
                    "message": "Schedule accepted. Waiting for other party.",
                    "both_accepted": False
                }), 200
        else:
            # Rejected - clear the proposal
            cursor.execute("""
                UPDATE service_progress 
                SET proposed_date = NULL,
                    proposed_time = NULL,
                    proposed_location = NULL,
                    proposed_by = NULL,
                    proposed_at = NULL,
                    schedule_accepted_by_consumer = FALSE,
                    schedule_accepted_by_provider = FALSE,
                    updated_at = NOW()
                WHERE id = %s
            """, (progress_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"message": "Schedule proposal rejected"}), 200
        
    except Exception as e:
        print(f"ERROR in respond_to_schedule_proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/messages/<int:message_id>/cancel-proposal", methods=['POST'])
def cancel_schedule_proposal(message_id):
    """Cancel a pending schedule proposal"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the proposal message
        cursor.execute("""
            SELECT m.id, m.sender_id, m.proposal_status, m.application_id,
                   sa.service_id
            FROM messages m
            JOIN service_applications sa ON m.application_id = sa.id
            WHERE m.id = %s AND m.message_type = 'schedule_proposal'
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            cursor.close()
            conn.close()
            return jsonify({"error": "Proposal not found"}), 404
        
        # Only the sender can cancel their own proposal
        if message['sender_id'] != user_id:
            cursor.close()
            conn.close()
            return jsonify({"error": "You can only cancel your own proposals"}), 403
        
        # Can only cancel pending proposals
        if message['proposal_status'] != 'pending':
            cursor.close()
            conn.close()
            return jsonify({"error": "Can only cancel pending proposals"}), 400
        
        # Update the proposal status to cancelled
        cursor.execute("""
            UPDATE messages
            SET proposal_status = 'cancelled'
            WHERE id = %s
        """, (message_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Proposal cancelled successfully"
        }), 200
        
    except Exception as e:
        print(f"ERROR in cancel_schedule_proposal: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/process-expired-surveys", methods=['POST'])
def trigger_expired_surveys():
    """Manual trigger for processing expired surveys (for testing/admin use)"""
    try:
        from survey_processor import process_expired_surveys
        count = process_expired_surveys()
        return jsonify({
            "message": f"Processed {count} expired surveys",
            "count": count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== ADMIN API ENDPOINTS ====================

@app.route("/api/admin/stats", methods=['GET'])
def get_admin_stats():
    """Get aggregate statistics for admin dashboard"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total users count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Get active users count (logged in within last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE last_login >= NOW() - INTERVAL '30 days'
        """)
        active_users = cursor.fetchone()['count']
        
        # Get total active services (both offers and needs)
        cursor.execute("""
            SELECT COUNT(*) as count FROM services 
            WHERE status = 'open'
        """)
        active_services = cursor.fetchone()['count']
        
        # Calculate hours exchanged from completed service progress
        cursor.execute("""
            SELECT COALESCE(SUM(hours), 0) as total_hours 
            FROM service_progress 
            WHERE status = 'completed'
        """)
        hours_exchanged = cursor.fetchone()['total_hours']
        
        # Get pending reports
        cursor.execute("""
            SELECT COUNT(*) as count FROM reports 
            WHERE status = 'open'
        """)
        pending_reports = cursor.fetchone()['count']
        
        # Get banned users count
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE user_status = 'banned'
        """)
        banned_users = cursor.fetchone()['count']
        
        # Get users with warnings
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE user_status = 'warning'
        """)
        warned_users = cursor.fetchone()['count']
        
        # Get total forum threads
        cursor.execute("SELECT COUNT(*) as count FROM forum_threads")
        total_threads = cursor.fetchone()['count']
        
        # Get total forum comments
        cursor.execute("SELECT COUNT(*) as count FROM forum_comments")
        total_comments = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "users": {
                "total": total_users,
                "active": active_users,
                "banned": banned_users,
                "warned": warned_users
            },
            "services": {
                "active_services": active_services,
                "hours_exchanged": float(hours_exchanged)
            },
            "reports": {
                "pending": pending_reports
            },
            "forum": {
                "threads": total_threads,
                "comments": total_comments
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_admin_stats: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/users", methods=['GET'])
def get_admin_users():
    """Get list of all users with their status"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        user_id = request.args.get('user_id')  # Single user ID
        user_status = request.args.get('status')  # active, banned, warning
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        # Build query with service count
        query = """
            SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.user_status, 
                   u.time_balance, u.is_verified, u.is_active, u.date_joined, u.last_login,
                   COUNT(s.id) as service_count
            FROM users u
            LEFT JOIN services s ON u.id = s.user_id
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND u.id = %s"
            params.append(user_id)
        
        if user_status:
            query += " AND u.user_status = %s"
            params.append(user_status)
        
        if search:
            query += " AND (u.email ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " GROUP BY u.id, u.email, u.first_name, u.last_name, u.role, u.user_status, u.time_balance, u.is_verified, u.is_active, u.date_joined, u.last_login"
        query += " ORDER BY u.date_joined DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) as count FROM users u WHERE 1=1"
        count_params = []
        
        if user_status:
            count_query += " AND u.user_status = %s"
            count_params.append(user_status)
        
        if search:
            count_query += " AND (u.email ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s)"
            search_pattern = f"%{search}%"
            count_params.extend([search_pattern, search_pattern, search_pattern])
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "users": [dict(user) for user in users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_admin_users: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/services", methods=['GET'])
def get_admin_services():
    """Get list of all services for admin panel"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        service_type = request.args.get('type')  # offer, need
        service_status = request.args.get('status')  # open, in_progress, completed, cancelled
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        # Build query with user info and application count
        query = """
            SELECT s.id, s.title, s.description, s.service_type, s.status, 
                   s.hours_required, s.created_at, s.user_id,
                   u.first_name, u.last_name, u.email,
                   COUNT(DISTINCT a.id) as application_count,
                   STRING_AGG(DISTINCT t.name, ', ' ORDER BY t.name) as tags
            FROM services s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN service_applications a ON s.id = a.service_id
            LEFT JOIN service_tags st ON s.id = st.service_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE 1=1
        """
        params = []
        
        if service_type:
            query += " AND s.service_type = %s"
            params.append(service_type)
        
        if service_status:
            query += " AND s.status = %s"
            params.append(service_status)
        
        if search:
            query += " AND (s.title ILIKE %s OR s.description ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        query += """ 
            GROUP BY s.id, s.title, s.description, s.service_type, s.status, 
                     s.hours_required, s.created_at, s.user_id, u.first_name, u.last_name, u.email
            ORDER BY s.created_at DESC 
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        services = cursor.fetchall()
        
        # Get total count for pagination
        count_query = """
            SELECT COUNT(DISTINCT s.id) as count 
            FROM services s
            JOIN users u ON s.user_id = u.id
            WHERE 1=1
        """
        count_params = []
        
        if service_type:
            count_query += " AND s.service_type = %s"
            count_params.append(service_type)
        
        if service_status:
            count_query += " AND s.status = %s"
            count_params.append(service_status)
        
        if search:
            count_query += " AND (s.title ILIKE %s OR s.description ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s)"
            search_pattern = f"%{search}%"
            count_params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "services": [dict(service) for service in services],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_admin_services: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/services/<int:service_id>", methods=['DELETE'])
def admin_remove_service(service_id):
    """Remove a service as admin"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        reason = data.get('reason', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get service owner
        cursor.execute("SELECT user_id, title FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        # Delete the service
        cursor.execute("UPDATE services SET status = 'cancelled' WHERE id = %s", (service_id,))
        
        # Send notification to owner
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (admin_id, service['user_id'], 
              f"Your service '{service['title']}' has been removed by an administrator. Reason: {reason}"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Service removed successfully"}), 200
        
    except Exception as e:
        print(f"ERROR in admin_remove_service: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/services/<int:service_id>/warn", methods=['POST'])
def admin_warn_service_owner(service_id):
    """Warn service owner as admin"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        warning_message = data.get('message', '')
        
        if not warning_message:
            return jsonify({"error": "Warning message is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get service owner
        cursor.execute("SELECT user_id, title FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            cursor.close()
            conn.close()
            return jsonify({"error": "Service not found"}), 404
        
        # Send warning message to owner
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (admin_id, service['user_id'], 
              f"⚠️ Admin Warning regarding your service '{service['title']}': {warning_message}"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Warning sent successfully"}), 200
        
    except Exception as e:
        print(f"ERROR in admin_warn_service_owner: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/users/<int:user_id>/action", methods=['POST'])
def admin_user_action():
    """Ban or warn a user"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        action = data.get('action')  # 'ban', 'warn', 'activate'
        reason = data.get('reason', '')
        user_id = request.view_args['user_id']
        
        if action not in ['ban', 'warn', 'activate']:
            return jsonify({"error": "Invalid action. Must be 'ban', 'warn', or 'activate'"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        # Cannot ban/warn other admins
        if user['role'] == 'admin':
            cursor.close()
            conn.close()
            return jsonify({"error": "Cannot modify admin users"}), 403
        
        # Update user status
        new_status = 'banned' if action == 'ban' else ('warning' if action == 'warn' else 'active')
        
        cursor.execute("""
            UPDATE users 
            SET user_status = %s
            WHERE id = %s
        """, (new_status, user_id))
        
        # Log the action
        log_admin_action(
            cursor, 
            admin_id, 
            f"user_{action}", 
            'user', 
            user_id, 
            {'reason': reason, 'email': user['email']},
            request.remote_addr
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"User {action}ed successfully",
            "user_id": user_id,
            "new_status": new_status
        }), 200
        
    except Exception as e:
        print(f"ERROR in admin_user_action: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/reports", methods=['GET'])
def get_admin_reports():
    """Get all content reports"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        report_status = request.args.get('status', 'open')  # open, resolved, dismissed
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        # Get reports with user information
        cursor.execute("""
            SELECT r.id, r.content_type, r.content_id, r.reason, r.description,
                   r.status, r.created_at, r.resolved_at, r.resolution_notes,
                   u1.email as reporter_email, u1.first_name as reporter_first_name,
                   u1.last_name as reporter_last_name,
                   u2.email as reported_user_email, u2.first_name as reported_first_name,
                   u2.last_name as reported_last_name,
                   u3.email as resolved_by_email
            FROM reports r
            LEFT JOIN users u1 ON r.reporter_id = u1.id
            LEFT JOIN users u2 ON r.reported_user_id = u2.id
            LEFT JOIN users u3 ON r.resolved_by = u3.id
            WHERE r.status = %s
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """, (report_status, per_page, offset))
        
        reports = cursor.fetchall()
        
        # Get total count
        cursor.execute("""
            SELECT COUNT(*) as count FROM reports WHERE status = %s
        """, (report_status,))
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "reports": [dict(report) for report in reports],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_admin_reports: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/admin/reports/<int:report_id>/resolve", methods=['POST'])
def resolve_report():
    """Resolve or dismiss a report"""
    try:
        admin_id, error, status = get_admin_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        action = data.get('action')  # 'resolved' or 'dismissed'
        notes = data.get('notes', '')
        report_id = request.view_args['report_id']
        
        if action not in ['resolved', 'dismissed']:
            return jsonify({"error": "Invalid action. Must be 'resolved' or 'dismissed'"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if report exists
        cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
        report = cursor.fetchone()
        
        if not report:
            cursor.close()
            conn.close()
            return jsonify({"error": "Report not found"}), 404
        
        # Update report
        cursor.execute("""
            UPDATE reports 
            SET status = %s, resolved_by = %s, resolved_at = NOW(), resolution_notes = %s
            WHERE id = %s
        """, (action, admin_id, notes, report_id))
        
        # Log the action
        log_admin_action(
            cursor, 
            admin_id, 
            f"report_{action}", 
            'report', 
            report_id, 
            {'notes': notes, 'content_type': report['content_type'], 'content_id': report['content_id']},
            request.remote_addr
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"Report {action} successfully",
            "report_id": report_id
        }), 200
        
    except Exception as e:
        print(f"ERROR in resolve_report: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ==================== TESTING API ENDPOINTS ====================

@app.route("/api/testing/user/balance", methods=['PUT'])
def update_user_balance_for_testing():
    """Update user's time balance for testing purposes only"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        new_balance = data.get('balance')
        
        if new_balance is None:
            return jsonify({"error": "balance is required"}), 400
        
        try:
            new_balance = float(new_balance)
        except (ValueError, TypeError):
            return jsonify({"error": "balance must be a number"}), 400
        
        if new_balance < 0:
            return jsonify({"error": "balance cannot be negative"}), 400
        
        if new_balance > 10:
            return jsonify({"error": "balance cannot exceed 10 hours"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update user's balance
        cursor.execute("""
            UPDATE users 
            SET time_balance = %s
            WHERE id = %s
        """, (new_balance, user_id))
        
        conn.commit()
        
        # Get updated user info
        cursor.execute("""
            SELECT id, email, first_name, last_name, time_balance
            FROM users
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Balance updated successfully",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "time_balance": float(user['time_balance'])
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in update_user_balance_for_testing: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ==================== FORUM API ENDPOINTS ====================

@app.route("/api/forum/categories", methods=['GET'])
def get_forum_categories():
    """Get all active forum categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fc.id, fc.name, fc.description, fc.created_at,
                   COUNT(DISTINCT ft.id) as thread_count
            FROM forum_categories fc
            LEFT JOIN forum_threads ft ON fc.id = ft.category_id
            WHERE fc.is_active = TRUE
            GROUP BY fc.id
            ORDER BY fc.name
        """)
        
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "categories": [dict(cat) for cat in categories]
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_forum_categories: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/forum/threads", methods=['GET'])
def get_forum_threads():
    """Get forum threads with optional category filter and pagination"""
    try:
        category_id = request.args.get('category')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT ft.id, ft.title, ft.content, ft.is_pinned, ft.is_locked,
                   ft.view_count, ft.created_at, ft.updated_at,
                   fc.name as category_name, fc.id as category_id,
                   u.id as author_id, u.first_name, u.last_name, u.email,
                   COUNT(DISTINCT fc2.id) as comment_count
            FROM forum_threads ft
            JOIN forum_categories fc ON ft.category_id = fc.id
            JOIN users u ON ft.user_id = u.id
            LEFT JOIN forum_comments fc2 ON ft.id = fc2.thread_id
            WHERE 1=1
        """
        params = []
        
        if category_id:
            query += " AND ft.category_id = %s"
            params.append(int(category_id))
        
        query += """
            GROUP BY ft.id, fc.id, u.id
            ORDER BY ft.is_pinned DESC, ft.updated_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        threads = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM forum_threads WHERE 1=1"
        count_params = []
        
        if category_id:
            count_query += " AND category_id = %s"
            count_params.append(int(category_id))
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "threads": [dict(thread) for thread in threads],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_forum_threads: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/forum/threads", methods=['POST'])
def create_forum_thread():
    """Create a new forum thread (requires authentication)"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        category_id = data.get('category_id')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        # Validation
        if not category_id:
            return jsonify({"error": "Category is required"}), 400
        
        if not title or len(title) < 5:
            return jsonify({"error": "Title must be at least 5 characters"}), 400
        
        if not content or len(content) < 10:
            return jsonify({"error": "Content must be at least 10 characters"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category exists and is active
        cursor.execute("""
            SELECT id FROM forum_categories 
            WHERE id = %s AND is_active = TRUE
        """, (category_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid or inactive category"}), 400
        
        # Create thread
        cursor.execute("""
            INSERT INTO forum_threads (category_id, user_id, title, content)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (category_id, user_id, title, content))
        
        result = cursor.fetchone()
        thread_id = result['id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Thread created successfully",
            "thread": {
                "id": thread_id,
                "title": title,
                "created_at": result['created_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"ERROR in create_forum_thread: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/forum/threads/<int:thread_id>", methods=['GET'])
def get_forum_thread(thread_id):
    """Get a single thread with its details"""
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Increment view count
        cursor.execute("""
            UPDATE forum_threads 
            SET view_count = view_count + 1 
            WHERE id = %s
        """, (thread_id,))
        
        # Get thread details
        cursor.execute("""
            SELECT ft.id, ft.title, ft.content, ft.is_pinned, ft.is_locked,
                   ft.view_count, ft.created_at, ft.updated_at,
                   fc.name as category_name, fc.id as category_id,
                   u.id as author_id, u.first_name, u.last_name, u.email
            FROM forum_threads ft
            JOIN forum_categories fc ON ft.category_id = fc.id
            JOIN users u ON ft.user_id = u.id
            WHERE ft.id = %s
        """, (thread_id,))
        
        thread = cursor.fetchone()
        
        if not thread:
            cursor.close()
            conn.close()
            return jsonify({"error": "Thread not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "thread": dict(thread)
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_forum_thread: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/forum/threads/<int:thread_id>/comments", methods=['GET'])
def get_thread_comments(thread_id):
    """Get all comments for a thread"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if thread exists
        cursor.execute("SELECT id FROM forum_threads WHERE id = %s", (thread_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Thread not found"}), 404
        
        # Get comments
        cursor.execute("""
            SELECT fc.id, fc.content, fc.parent_comment_id, fc.created_at, fc.updated_at,
                   u.id as author_id, u.first_name, u.last_name, u.email
            FROM forum_comments fc
            JOIN users u ON fc.user_id = u.id
            WHERE fc.thread_id = %s
            ORDER BY fc.created_at ASC
            LIMIT %s OFFSET %s
        """, (thread_id, per_page, offset))
        
        comments = cursor.fetchall()
        
        # Get total count
        cursor.execute("""
            SELECT COUNT(*) as count FROM forum_comments WHERE thread_id = %s
        """, (thread_id,))
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "comments": [dict(comment) for comment in comments],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_thread_comments: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/forum/threads/<int:thread_id>/comments", methods=['POST'])
def add_thread_comment(thread_id):
    """Add a comment to a thread"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        content = data.get('content', '').strip()
        parent_comment_id = data.get('parent_comment_id')
        
        # Validation
        if not content or len(content) < 1:
            return jsonify({"error": "Comment content is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if thread exists and is not locked
        cursor.execute("""
            SELECT id, is_locked FROM forum_threads WHERE id = %s
        """, (thread_id,))
        
        thread = cursor.fetchone()
        if not thread:
            cursor.close()
            conn.close()
            return jsonify({"error": "Thread not found"}), 404
        
        if thread['is_locked']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Thread is locked"}), 403
        
        # If parent_comment_id is provided, verify it exists
        if parent_comment_id:
            cursor.execute("""
                SELECT id FROM forum_comments 
                WHERE id = %s AND thread_id = %s
            """, (parent_comment_id, thread_id))
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error": "Parent comment not found"}), 404
        
        # Create comment
        cursor.execute("""
            INSERT INTO forum_comments (thread_id, user_id, content, parent_comment_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (thread_id, user_id, content, parent_comment_id))
        
        result = cursor.fetchone()
        comment_id = result['id']
        
        # Update thread's updated_at timestamp
        cursor.execute("""
            UPDATE forum_threads 
            SET updated_at = NOW() 
            WHERE id = %s
        """, (thread_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Comment added successfully",
            "comment": {
                "id": comment_id,
                "content": content,
                "created_at": result['created_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"ERROR in add_thread_comment: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/reports", methods=['POST'])
def create_report():
    """Create a new content report"""
    try:
        user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
        if error:
            return jsonify(error), status
        
        data = request.get_json()
        content_type = data.get('content_type')  # service, thread, comment, user, message
        content_id = data.get('content_id')
        reported_user_id = data.get('reported_user_id')
        reason = data.get('reason', '').strip()
        description = data.get('description', '').strip()
        
        # Validation
        valid_types = ['service', 'thread', 'comment', 'user', 'message']
        if content_type not in valid_types:
            return jsonify({"error": f"Invalid content type. Must be one of: {', '.join(valid_types)}"}), 400
        
        if not reason:
            return jsonify({"error": "Reason is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create report
        cursor.execute("""
            INSERT INTO reports (reporter_id, reported_user_id, content_type, content_id, reason, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (user_id, reported_user_id, content_type, content_id, reason, description))
        
        result = cursor.fetchone()
        report_id = result['id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Report submitted successfully",
            "report": {
                "id": report_id,
                "created_at": result['created_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"ERROR in create_report: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ==================== IMAGE UPLOAD ENDPOINT ====================
@app.route("/api/upload/image", methods=['POST'])
def upload_image():
    """Handle image upload"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file and allowed_file(file.filename):
            # Generate unique filename to prevent overwrites
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Save file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            
            # Return the URL (relative to static)
            # Note: app serves static files from /static/
            file_url = f"/static/uploads/{unique_filename}"
            
            return jsonify({
                "message": "File uploaded successfully",
                "url": file_url
            }), 201
            
        return jsonify({"error": "File type not allowed"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, '../frontend/static'),
        'hive_logo.png',
        mimetype='image/png'
    )


if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    
    # Start background survey processor
    try:
        from survey_processor import start_background_processor
        start_background_processor()
    except Exception as e:
        print(f"Failed to start background processor: {e}")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
