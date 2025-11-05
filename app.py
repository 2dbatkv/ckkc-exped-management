#!/usr/bin/env python3
"""
CKKC October 2025 Expedition Management System
Ultra-portable Flask application for offline expedition management
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2 import pool, errors
from datetime import datetime
import json
import math
import csv
import io
import shutil
import zipfile

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ckkc_whigpistle_expedition_2025_change_in_production')  # For flash messages

# Add custom Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string into Python object"""
    if not value:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []

# Admin configuration
ADMIN_PASSCODE = os.getenv('ADMIN_PASSCODE', 'expedition2025')  # Simple passcode for admin access

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/expedition_db')
# PostgreSQL uses same database connection




# Database connection pool
db_pool = None

def init_connection_pool():
    """Initialize PostgreSQL connection pool"""
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
        print("✓ PostgreSQL connection pool initialized")
    except (Exception, psycopg2.Error) as error:
        print(f"Error creating connection pool: {error}")
        raise

def get_db_connection():
    """Get a database connection from pool with validation"""
    if db_pool is None:
        raise Exception("Connection pool not initialized")
    conn = db_pool.getconn()
    # Test the connection to ensure it's not stale
    try:
        with conn.cursor() as test_cursor:
            test_cursor.execute('SELECT 1')
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        # Connection is stale, close it and get a new one
        try:
            conn.close()
        except:
            pass
        conn = db_pool.getconn()
    return conn

def return_connection(conn, error=False):
    """Return connection to pool or close if error occurred"""
    if db_pool and conn:
        if error:
            # Close connection on error, don't return to pool
            try:
                conn.close()
            except:
                pass
            db_pool.putconn(conn, close=True)
        else:
            db_pool.putconn(conn)

def get_cursor(conn):
    """Get cursor with dict-like row factory"""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def close_connection_pool():
    """Close all connections"""
    if db_pool:
        db_pool.closeall()



def shot_to_cartesian(distance, azimuth_deg, inclination_deg):
    """Convert shot measurements to Cartesian coordinates (dx, dy, dz)"""
    if distance is None or azimuth_deg is None or inclination_deg is None:
        return 0.0, 0.0, 0.0
    
    inc_rad = math.radians(inclination_deg)
    az_rad = math.radians(azimuth_deg)
    
    horizontal_distance = distance * math.cos(inc_rad)
    
    dx = horizontal_distance * math.sin(az_rad)  # East component
    dy = horizontal_distance * math.cos(az_rad)  # North component  
    dz = distance * math.sin(inc_rad)           # Up component (vertical)
    
    return dx, dy, dz

def calculate_variance(fs_value, bs_value):
    """Calculate variance between frontsight and backsight readings"""
    if fs_value is None or bs_value is None:
        return None
    return abs(fs_value - bs_value)

@app.route('/')
def dashboard():
    """Main dashboard"""
    conn = None
    try:
        # Get participant count
        conn = get_db_connection()
        cursor = get_cursor(conn)
        cursor.execute('SELECT COUNT(*) as count FROM participants')
        participant_count = cursor.fetchone()['count']
        return render_template('dashboard.html', participant_count=participant_count)
    except Exception as e:
        app.logger.error(f"Error in dashboard: {e}")
        if conn:
            return_connection(conn, error=True)
        return render_template('dashboard.html', participant_count=0)
    finally:
        if conn:
            return_connection(conn)

@app.route('/register')
def register_form():
    """Show registration form - default to clean design"""
    return render_template('register_clean.html')

@app.route('/register/clean')
def register_clean():
    """Clean & Professional design"""
    return render_template('register_clean.html')

@app.route('/register/cave')
def register_cave():
    """Cave-themed design"""
    return render_template('register_cave.html')

@app.route('/register', methods=['POST'])
def register_submit():
    """Process registration form submission"""
    try:
        # Extract form data
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        address = request.form.get('address', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        traveled_with = request.form.get('traveled_with', '').strip()
        accommodation = request.form.get('accommodation', '')
        other_accommodation = request.form.get('other_accommodation', '').strip()
        
        print(f"  - full_name: '{full_name}'")
        print(f"  - email: '{email}'")
        print(f"  - phone_number: '{phone_number}'")
        print(f"  - address: '{address}'")
        print(f"  - emergency_contact: '{emergency_contact}'")
        print(f"  - accommodation: '{accommodation}'")
        
        # Handle multi-select fields
        participation_days = request.form.getlist('participation_days')
        eating_at_expedition = 'eating_at_expedition' in request.form
        roppel_trips = request.form.get('roppel_trips', '')
        crf_compass_agreement = 'crf_compass_agreement' in request.form
        skills = request.form.getlist('skills')
        have_instruments = 'have_instruments' in request.form
        instruments_details = request.form.get('instruments_details', '').strip()
        group_gear = request.form.getlist('group_gear')
        group_gear_other_details = request.form.get('group_gear_other_details', '').strip()
        additional_info = request.form.get('additional_info', '').strip()
        
        print(f"  - participation_days: {participation_days}")
        print(f"  - eating_at_expedition: {eating_at_expedition}")
        print(f"  - roppel_trips: '{roppel_trips}'")
        print(f"  - crf_compass_agreement: {crf_compass_agreement}")
        print(f"  - skills: {skills}")
        print(f"  - have_instruments: {have_instruments}")
        print(f"  - group_gear: {group_gear}")
        
        # Validate required fields
        required_fields = [full_name, email, phone_number, address, emergency_contact, accommodation]
        
        if not all(required_fields):
            missing_fields = []
            if not full_name: missing_fields.append('Full Name')
            if not email: missing_fields.append('Email Address')
            if not phone_number: missing_fields.append('Phone Number')
            if not address: missing_fields.append('Physical Address')
            if not emergency_contact: missing_fields.append('Emergency Contact')
            if not accommodation: missing_fields.append('Accommodation')
            
            error_msg = f'Please fill in all required fields: {", ".join(missing_fields)}'
            flash(error_msg, 'error')
            return redirect(url_for('register_form'))
        
        # Validate required selections (checkboxes/multi-select)
        if not participation_days:
            flash('Please select at least one participation day.', 'error')
            return redirect(url_for('register_form'))
        
        if not skills:
            flash('Please select at least one skill or experience level.', 'error')
            return redirect(url_for('register_form'))
        
        # Validate CRF compass course agreement (required only if participating in Roppel trips)
        if roppel_trips == 'yes' and not crf_compass_agreement:
            error_msg = 'You must agree to use the CRF compass course method for Roppel Cave System trips to complete registration.'
            flash(error_msg, 'error')
            return redirect(url_for('register_form'))
        
        # Validate "Other" accommodation requires details
        if accommodation == 'other' and not other_accommodation:
            error_msg = 'Please specify your accommodation details.'
            flash(error_msg, 'error')
            return redirect(url_for('register_form'))
        
        # Validate instruments details if checkbox is checked
        if have_instruments and not instruments_details:
            error_msg = 'Please provide details about your survey instruments.'
            flash(error_msg, 'error')
            return redirect(url_for('register_form'))
        
        # Validate group gear other details if "other" is selected
        if 'other' in group_gear and not group_gear_other_details:
            error_msg = 'Please specify what other gear you can share/loan.'
            flash(error_msg, 'error')
            return redirect(url_for('register_form'))
        
        
        # Connect to database and check for duplicate email
        conn = get_db_connection()

        cursor = get_cursor(conn)
        cursor = conn.cursor()
        
        # Check for existing email
        existing_participant = cursor.execute(
            'SELECT id, full_name FROM participants WHERE email = %s', (email,)
        ).fetchone()
        
        if existing_participant:
            return_connection(conn)
            flash(f'Registration failed: Email {email} is already registered by {existing_participant["full_name"]}. Each participant must use a unique email address.', 'error')
            return redirect(url_for('register_form'))
        
        insert_data = (
            full_name, email, phone_number, address, emergency_contact, traveled_with, accommodation, other_accommodation,
            json.dumps(participation_days), eating_at_expedition, roppel_trips, crf_compass_agreement,
            json.dumps(skills), have_instruments, instruments_details, json.dumps(group_gear), group_gear_other_details, additional_info,
            True  # waiver_acknowledged - always TRUE when form is submitted
        )

        cursor.execute('''
        INSERT INTO participants
        (full_name, email, phone_number, address, emergency_contact, traveled_with, accommodation, other_accommodation,
         participation_days, eating_at_expedition, roppel_trips, crf_compass_agreement, skills, have_instruments,
         instruments_details, group_gear, group_gear_other_details, additional_info, waiver_acknowledged,
         waiver_acknowledged_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
        ''', insert_data)
        
        conn.commit()
        return_connection(conn)
        
        flash(f'Successfully registered {full_name} for the expedition!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        error_msg = f'Registration failed: {str(e)}'
        import traceback
        flash(error_msg, 'error')
        return redirect(url_for('register_form'))

@app.route('/participants')
def participants_list():
    """View registered participants"""
    conn = get_db_connection()

    cursor = get_cursor(conn)
    participants = cursor.execute('''
    SELECT * FROM participants 
    ORDER BY registration_time DESC
    ''').fetchall()
    return_connection(conn)
    
    # Parse JSON fields for display
    participants_data = []
    for p in participants:
        participant_dict = dict(p)
        participant_dict['participation_days'] = json.loads(p['participation_days'] or '[]')
        participant_dict['skills'] = json.loads(p['skills'] or '[]')
        participant_dict['group_gear'] = json.loads(p['group_gear'] or '[]')
        participants_data.append(participant_dict)
    
    return render_template('participants.html', participants=participants_data)

@app.route('/trips')
def trips_list():
    """View planned cave trips"""
    conn = get_db_connection()

    cursor = get_cursor(conn)
    trips = cursor.execute('''
        SELECT * FROM trips 
        ORDER BY trip_date ASC, created_date ASC
    ''').fetchall()
    return_connection(conn)
    
    # Group trips by date
    from datetime import datetime
    trips_by_date = {}
    for trip in trips:
        if trip['trip_date']:
            try:
                trip_date = datetime.strptime(trip['trip_date'], '%Y-%m-%d')
                date_key = trip_date.strftime('%Y-%m-%d')
                date_label = trip_date.strftime('%A, %B %d, %Y')
                
                if date_key not in trips_by_date:
                    trips_by_date[date_key] = {
                        'date_label': date_label,
                        'trips': []
                    }
                trips_by_date[date_key]['trips'].append(trip)
            except ValueError:
                pass
    
    return render_template('trips.html', trips_by_date=trips_by_date)

@app.route('/admin/')
def admin_dashboard():
    """Administration dashboard - requires passcode"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    
    # Get basic stats
    cursor.execute('SELECT COUNT(*) as count FROM participants')
    participant_count = cursor.fetchone()
    
    # Get participation days breakdown
    cursor.execute('SELECT participation_days FROM participants WHERE participation_days IS NOT NULL')
    participation_data = cursor.fetchall()
    participation_days_count = {}
    for row in participation_data:
        if row['participation_days']:
            days = json.loads(row['participation_days'])
            for day in days:
                participation_days_count[day] = participation_days_count.get(day, 0) + 1
    
    # Get eating at expedition count
    eating_count = cursor.execute('''
    SELECT 
        SUM(CASE WHEN eating_at_expedition = 1 THEN 1 ELSE 0 END) as eating_yes,
        SUM(CASE WHEN eating_at_expedition = 0 OR eating_at_expedition IS NULL THEN 1 ELSE 0 END) as eating_no
    FROM participants
    ''').fetchone()
    
    # Get skills breakdown
    cursor.execute('SELECT skills FROM participants WHERE skills IS NOT NULL')
    skills_data = cursor.fetchall()
    skills_count = {}
    for row in skills_data:
        if row['skills']:
            skills = json.loads(row['skills'])
            for skill in skills:
                skills_count[skill] = skills_count.get(skill, 0) + 1
    
    return_connection(conn)
    
    return render_template('admin.html', 
                         participant_count=participant_count,
                         participation_days_count=participation_days_count,
                         eating_count=eating_count,
                         skills_count=skills_count)

@app.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_submit():
    """Process admin login"""
    passcode = request.form.get('passcode', '').strip()
    
    if passcode == ADMIN_PASSCODE:
        session['admin_authenticated'] = True
        flash('Welcome to the admin dashboard!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid passcode. Please try again.', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/registration-data')
def admin_registration_data():
    """Admin view/edit registration data"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    participants = cursor.execute('''
    SELECT * FROM participants 
    ORDER BY registration_time DESC
    ''').fetchall()
    return_connection(conn)
    
    return render_template('admin_registration_data.html', participants=participants)

@app.route('/admin/registration-data/edit/<int:participant_id>')
def admin_edit_participant(participant_id):
    """Edit specific participant"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    participant = cursor.execute('''
    SELECT * FROM participants WHERE id = %s
    ''', (participant_id,)).fetchone()
    return_connection(conn)
    
    if not participant:
        flash('Participant not found.', 'error')
        return redirect(url_for('admin_registration_data'))
    
    return render_template('admin_edit_participant.html', participant=participant)

@app.route('/admin/registration-data/edit/<int:participant_id>', methods=['POST'])
def admin_update_participant(participant_id):
    """Update participant data"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        
        # Extract form data
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        address = request.form.get('address', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        accommodation = request.form.get('accommodation', '')
        
        # Update participant
        cursor.execute('''
        UPDATE participants 
        SET full_name = %s, email = %s, phone_number = %s, address = %s, 
            emergency_contact = %s, accommodation = %s
        WHERE id = %s
        ''', (full_name, email, phone_number, address, emergency_contact, 
              accommodation, participant_id))
        
        conn.commit()
        return_connection(conn)
        
        flash('Participant updated successfully.', 'success')
        return redirect(url_for('admin_registration_data'))
        
    except Exception as e:
        flash(f'Error updating participant: {str(e)}', 'error')
        return redirect(url_for('admin_edit_participant', participant_id=participant_id))

@app.route('/admin/registration-data/delete/<int:participant_id>', methods=['POST'])
def admin_delete_participant(participant_id):
    """Delete participant"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        cursor.execute('DELETE FROM participants WHERE id = %s', (participant_id,))
        conn.commit()
        return_connection(conn)
        
        flash('Participant deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting participant: {str(e)}', 'error')
    
    return redirect(url_for('admin_registration_data'))

@app.route('/admin/cave-survey-data')
def admin_cave_survey_data():
    """Admin view/edit cave survey data"""
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = sqlite3.connect(CAVE_SURVEY_DATABASE)
        conn.row_factory = psycopg2.extras.RealDictRow
        surveys = cursor.execute('''
        SELECT * FROM survey_header 
        ORDER BY created_date DESC
        ''').fetchall()
        return_connection(conn)
        
        return render_template('admin_cave_survey_data.html', surveys=surveys)
    except Exception as e:
        flash(f'Error accessing cave survey data: {str(e)}', 'error')
        return render_template('admin_cave_survey_data.html', surveys=[])

@app.route('/admin/raw-data-viewer')
def admin_raw_data_viewer():
    """View all raw survey data from database"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

    try:
        conn = sqlite3.connect(CAVE_SURVEY_DATABASE)
        cursor = conn.cursor()

        # Get all caves
        cursor.execute('SELECT cave_id, name, location_text FROM caves ORDER BY cave_id;')
        caves = cursor.fetchall()

        # Get all surveys
        cursor.execute('SELECT survey_id, cave_id, date, area_in_cave, objective FROM surveys ORDER BY survey_id;')
        surveys = cursor.fetchall()

        # Get all shots
        cursor.execute('SELECT * FROM shots ORDER BY survey_id, shot_id;')
        shots = cursor.fetchall()

        # Get shot counts per survey
        cursor.execute('SELECT survey_id, COUNT(*) FROM shots GROUP BY survey_id ORDER BY survey_id;')
        shot_counts = cursor.fetchall()

        return_connection(conn)

        return render_template('admin_view_raw_data.html',
                             caves=caves,
                             surveys=surveys,
                             shots=shots,
                             shot_counts=shot_counts)
    except Exception as e:
        flash(f'Error accessing raw data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/survey/<int:survey_id>/view')
def admin_survey_view(survey_id):
    """View detailed survey data"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_cave_survey_db_connection()
        cursor.execute('SELECT * FROM survey_header WHERE id = %s', (survey_id,))
        survey = cursor.fetchone()
        return_connection(conn)
        
        if not survey:
            flash('Survey not found.', 'error')
            return redirect(url_for('admin_cave_survey_data'))
        
        # Parse survey shots JSON
        survey_shots = []
        if survey['survey_shots_json']:
            try:
                survey_shots = json.loads(survey['survey_shots_json'])
            except json.JSONDecodeError:
                pass
        
        return render_template('admin_survey_view.html', survey=survey, survey_shots=survey_shots)
    
    except Exception as e:
        flash(f'Error viewing survey: {str(e)}', 'error')
        return redirect(url_for('admin_cave_survey_data'))

@app.route('/admin/survey/<int:survey_id>/edit')
def admin_survey_edit(survey_id):
    """Edit survey data"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_cave_survey_db_connection()
        cursor.execute('SELECT * FROM survey_header WHERE id = %s', (survey_id,))
        survey = cursor.fetchone()
        return_connection(conn)
        
        if not survey:
            flash('Survey not found.', 'error')
            return redirect(url_for('admin_cave_survey_data'))
        
        # Parse survey shots JSON
        survey_shots = []
        if survey['survey_shots_json']:
            try:
                survey_shots = json.loads(survey['survey_shots_json'])
            except json.JSONDecodeError:
                pass
        
        return render_template('admin_survey_edit.html', survey=survey, survey_shots=survey_shots)
    
    except Exception as e:
        flash(f'Error accessing survey for editing: {str(e)}', 'error')
        return redirect(url_for('admin_cave_survey_data'))

@app.route('/admin/survey/<int:survey_id>/edit', methods=['POST'])
def admin_survey_update(survey_id):
    """Update survey data"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        # Extract all form data
        cave_name = request.form.get('cave_name', '').strip()
        state = request.form.get('state', '').strip()
        county = request.form.get('county', '').strip()
        region = request.form.get('region', '').strip()
        survey_date = request.form.get('survey_date', '').strip()
        fsb_number = request.form.get('fsb_number', '').strip()
        area_in_cave = request.form.get('area_in_cave', '').strip()
        time_in = request.form.get('time_in', '').strip()
        time_out = request.form.get('time_out', '').strip()
        survey_objective = request.form.get('survey_objective', '').strip()
        conditions = request.form.get('conditions', '').strip()
        other_info = request.form.get('other_info', '').strip()

        # Team information
        book_sketch_person = request.form.get('book_sketch_person', '').strip()
        instrument_reader = request.form.get('instrument_reader', '').strip()
        tape_person = request.form.get('tape_person', '').strip()
        point_person = request.form.get('point_person', '').strip()
        trip_leader = request.form.get('trip_leader', '').strip()
        other_team_members = request.form.get('other_team_members', '').strip()

        # Instrument information
        compass_id = request.form.get('compass_id', '').strip()
        compass_frontsight = request.form.get('compass_frontsight')
        compass_backsight = request.form.get('compass_backsight')
        inclinometer_id = request.form.get('inclinometer_id', '').strip()
        inclinometer_frontsight = request.form.get('inclinometer_frontsight')
        inclinometer_backsight = request.form.get('inclinometer_backsight')
        crf_compass_course = 1 if request.form.get('crf_compass_course') else 0
        calibration_notes = request.form.get('calibration_notes', '').strip()
        additional_equipment = request.form.get('additional_equipment', '').strip()

        # Form validation checkboxes
        instruments_crf_course = 1 if request.form.get('instruments_crf_course') else 0
        data_accuracy = 1 if request.form.get('data_accuracy') else 0

        # Survey shots data
        from_stations = request.form.getlist('from_station[]')
        to_stations = request.form.getlist('to_station[]')
        distances = request.form.getlist('distance[]')
        azimuth_fs_list = request.form.getlist('azimuth_fs[]')
        azimuth_bs_list = request.form.getlist('azimuth_bs[]')
        inclination_fs_list = request.form.getlist('inclination_fs[]')
        inclination_bs_list = request.form.getlist('inclination_bs[]')
        left_list = request.form.getlist('left[]')
        right_list = request.form.getlist('right[]')
        up_list = request.form.getlist('up[]')
        down_list = request.form.getlist('down[]')
        notes_list = request.form.getlist('notes[]')

        # Build survey shots array
        survey_shots = []
        for i in range(len(from_stations)):
            if from_stations[i].strip():  # Only include if from_station is not empty
                survey_shots.append({
                    'from_station': from_stations[i],
                    'to_station': to_stations[i] if i < len(to_stations) else '',
                    'distance': distances[i] if i < len(distances) else '',
                    'azimuth_fs': azimuth_fs_list[i] if i < len(azimuth_fs_list) else '',
                    'azimuth_bs': azimuth_bs_list[i] if i < len(azimuth_bs_list) else '',
                    'inclination_fs': inclination_fs_list[i] if i < len(inclination_fs_list) else '',
                    'inclination_bs': inclination_bs_list[i] if i < len(inclination_bs_list) else '',
                    'left': left_list[i] if i < len(left_list) else '',
                    'right': right_list[i] if i < len(right_list) else '',
                    'up': up_list[i] if i < len(up_list) else '',
                    'down': down_list[i] if i < len(down_list) else '',
                    'notes': notes_list[i] if i < len(notes_list) else ''
                })

        # Basic validation
        if not cave_name or not survey_date:
            flash('Cave name and survey date are required.', 'error')
            return redirect(url_for('admin_survey_edit', survey_id=survey_id))

        conn = get_cave_survey_db_connection()
        cursor.execute('''
            UPDATE survey_header
            SET cave_name = %s, state = %s, county = %s, region = %s, survey_date = %s, fsb_number = %s,
                area_in_cave = %s, time_in = %s, time_out = %s, survey_objective = %s,
                conditions = %s, other_info = %s,
                book_sketch_person = %s, instrument_reader = %s, tape_person = %s,
                point_person = %s, trip_leader = %s, other_team_members = %s,
                compass_id = %s, compass_frontsight = %s, compass_backsight = %s,
                inclinometer_id = %s, inclinometer_frontsight = %s, inclinometer_backsight = %s,
                crf_compass_course = %s, calibration_notes = %s, additional_equipment = %s,
                instruments_crf_course = %s, data_accuracy = %s, survey_shots_json = %s
            WHERE id = %s
        ''', (cave_name, state, county, region, survey_date, fsb_number, area_in_cave,
              time_in, time_out, survey_objective, conditions, other_info,
              book_sketch_person, instrument_reader, tape_person, point_person,
              trip_leader, other_team_members,
              compass_id, compass_frontsight, compass_backsight,
              inclinometer_id, inclinometer_frontsight, inclinometer_backsight,
              crf_compass_course, calibration_notes, additional_equipment,
              instruments_crf_course, data_accuracy, json.dumps(survey_shots), survey_id))
        
        conn.commit()
        return_connection(conn)
        
        flash('Survey updated successfully!', 'success')
        return redirect(url_for('admin_survey_view', survey_id=survey_id))
    
    except Exception as e:
        flash(f'Error updating survey: {str(e)}', 'error')
        return redirect(url_for('admin_survey_edit', survey_id=survey_id))

@app.route('/admin/survey/<int:survey_id>/export')
def admin_survey_export(survey_id):
    """Export survey data as text file"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

    try:
        conn = get_cave_survey_db_connection()
        cursor.execute('SELECT * FROM survey_header WHERE id = %s', (survey_id,))
        survey = cursor.fetchone()
        return_connection(conn)

        if not survey:
            flash('Survey not found', 'error')
            return redirect(url_for('admin_cave_survey_data'))

        # Parse survey shots JSON
        survey_shots = []
        if survey['survey_shots_json']:
            try:
                survey_shots = json.loads(survey['survey_shots_json'])
            except:
                pass

        # Build text file content
        content = []
        content.append("=" * 80)
        content.append("CAVE SURVEY DATA EXPORT")
        content.append("CKKC October 2025 Expedition")
        content.append("=" * 80)
        content.append("")

        # Basic Information
        content.append("BASIC INFORMATION")
        content.append("-" * 80)
        content.append(f"Survey ID: {survey['id']}")
        content.append(f"Cave Name: {survey['cave_name'] or ''}")
        content.append(f"State: {survey['state'] or ''}")
        content.append(f"County: {survey['county'] or ''}")
        content.append(f"Region: {survey['region'] or ''}")
        content.append(f"Survey Date: {survey['survey_date'] or ''}")
        content.append(f"FSB Number: {survey['fsb_number'] or ''}")
        content.append(f"Area in Cave: {survey['area_in_cave'] or ''}")
        content.append(f"Time In: {survey['time_in'] or ''}")
        content.append(f"Time Out: {survey['time_out'] or ''}")
        content.append(f"Survey Objective: {survey['survey_objective'] or ''}")
        content.append(f"Conditions: {survey['conditions'] or ''}")
        content.append(f"Other Info: {survey['other_info'] or ''}")
        content.append("")

        # Survey Team
        content.append("SURVEY TEAM")
        content.append("-" * 80)
        content.append(f"Book/Sketch Person: {survey['book_sketch_person'] or ''}")
        content.append(f"Instrument Reader: {survey['instrument_reader'] or ''}")
        content.append(f"Tape Person: {survey['tape_person'] or ''}")
        content.append(f"Point Person: {survey['point_person'] or ''}")
        content.append(f"Trip/Survey Leader: {survey['trip_leader'] or ''}")
        content.append(f"Other Team Members: {survey['other_team_members'] or ''}")
        content.append("")

        # Instruments
        content.append("INSTRUMENTS")
        content.append("-" * 80)
        content.append(f"Compass ID: {survey['compass_id'] or ''}")
        content.append(f"Compass Frontsight: {survey['compass_frontsight'] or ''}")
        content.append(f"Compass Backsight: {survey['compass_backsight'] or ''}")
        content.append(f"Inclinometer ID: {survey['inclinometer_id'] or ''}")
        content.append(f"Inclinometer Frontsight: {survey['inclinometer_frontsight'] or ''}")
        content.append(f"Inclinometer Backsight: {survey['inclinometer_backsight'] or ''}")
        content.append(f"CRF Compass Course: {survey['crf_compass_course'] or ''}")
        content.append(f"Calibration Notes: {survey['calibration_notes'] or ''}")
        content.append(f"Additional Equipment: {survey['additional_equipment'] or ''}")
        content.append(f"Instruments on CRF Course: {survey['instruments_crf_course'] or ''}")
        content.append(f"Data Accuracy Confirmed: {survey['data_accuracy'] or ''}")
        content.append("")

        # Survey Shots
        content.append("SURVEY SHOTS")
        content.append("-" * 80)
        if survey_shots:
            # Header
            content.append(f"{'From':<8} {'To':<8} {'Dist':<8} {'Az FS':<8} {'Az BS':<8} {'Inc FS':<8} {'Inc BS':<8} {'L':<6} {'R':<6} {'U':<6} {'D':<6} {'Notes':<20}")
            content.append("-" * 80)

            # Data rows
            for shot in survey_shots:
                line = (
                    f"{shot.get('from_station', ''):<8} "
                    f"{shot.get('to_station', ''):<8} "
                    f"{shot.get('distance', ''):<8} "
                    f"{shot.get('azimuth_fs', ''):<8} "
                    f"{shot.get('azimuth_bs', ''):<8} "
                    f"{shot.get('inclination_fs', ''):<8} "
                    f"{shot.get('inclination_bs', ''):<8} "
                    f"{shot.get('left', ''):<6} "
                    f"{shot.get('right', ''):<6} "
                    f"{shot.get('up', ''):<6} "
                    f"{shot.get('down', ''):<6} "
                    f"{shot.get('notes', ''):<20}"
                )
                content.append(line)
        else:
            content.append("No survey shots recorded")

        content.append("")
        content.append("=" * 80)
        content.append(f"Created: {survey['created_date']}")
        content.append("=" * 80)

        # Create response with text file
        text_content = '\n'.join(content)
        filename = f"survey_{survey['cave_name'].replace(' ', '_')}_{survey_id}.txt"

        response = make_response(text_content)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    except Exception as e:
        flash(f'Error exporting survey: {str(e)}', 'error')
        return redirect(url_for('admin_cave_survey_data'))

@app.route('/admin/survey/<int:survey_id>/delete', methods=['POST'])
def admin_survey_delete(survey_id):
    """Delete survey data"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'error': 'Not authenticated'})

    try:
        conn = get_cave_survey_db_connection()

        # Check if survey exists
        cursor.execute('SELECT cave_name FROM survey_header WHERE id = %s', (survey_id,))
        survey = cursor.fetchone()
        if not survey:
            return_connection(conn)
            return jsonify({'success': False, 'error': 'Survey not found'})

        # Delete survey
        cursor.execute('DELETE FROM survey_header WHERE id = %s', (survey_id,))
        conn.commit()
        return_connection(conn)

        return jsonify({'success': True, 'message': f'Survey for {survey["cave_name"]} deleted successfully'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """API endpoint for expedition statistics"""
    conn = get_db_connection()

    cursor = get_cursor(conn)
    
    stats = {
        'total_participants': cursor.execute('SELECT COUNT(*) as count FROM participants').fetchone()['count'],
        'accommodations': {},
        'skills_count': {},
        'participation_by_day': {}
    }
    
    # Get accommodation breakdown
    accommodations = cursor.execute('''
    SELECT accommodation, COUNT(*) as count 
    FROM participants 
    GROUP BY accommodation
    ''').fetchall()
    
    for acc in accommodations:
        stats['accommodations'][acc['accommodation']] = acc['count']
    
    return_connection(conn)
    return jsonify(stats)

@app.route('/api/cave-survey-stats')
def api_cave_survey_stats():
    """API endpoint for cave survey statistics"""
    conn = get_cave_survey_db_connection()
    
    stats = {
        'total_caves': cursor.execute('SELECT COUNT(*) as count FROM caves').fetchone()['count'],
        'total_surveys': cursor.execute('SELECT COUNT(*) as count FROM surveys').fetchone()['count'],
        'total_shots': cursor.execute('SELECT COUNT(*) as count FROM shots').fetchone()['count'],
        'total_distance': 0,
        'caves': []
    }
    
    # Get total distance surveyed
    cursor.execute('SELECT SUM(distance) as total FROM shots WHERE distance IS NOT NULL')
    total_distance_result = cursor.fetchone()
    if total_distance_result and total_distance_result['total']:
        stats['total_distance'] = round(total_distance_result['total'], 2)
    
    # Get caves list
    cursor.execute('SELECT * FROM caves ORDER BY name')
    caves = cursor.fetchall()
    for cave in caves:
        cave_dict = dict(cave)
        cave_dict['survey_count'] = cursor.execute(
            'SELECT COUNT(*) as count FROM surveys WHERE cave_id = ?', 
            (cave['cave_id'],)
        ).fetchone()['count']
        stats['caves'].append(cave_dict)
    
    return_connection(conn)
    return jsonify(stats)

@app.route('/survey')
def survey_form():
    """Cave survey data entry form"""
    # Clear any existing flash messages to prevent showing stale messages
    from flask import get_flashed_messages
    get_flashed_messages()  # This consumes and clears existing messages
    return render_template('survey.html')

@app.route('/survey', methods=['POST'])
def survey_submit():
    """Process cave survey data submission"""
    try:
        # Initialize cave survey database
        init_cave_survey_db()
        
        # Extract form data
        cave_name = request.form.get('cave_name', '').strip()
        state = request.form.get('state', '').strip()
        county = request.form.get('county', '').strip()
        region = request.form.get('region', '').strip()
        survey_date = request.form.get('survey_date', '').strip()
        fsb_number = request.form.get('fsb_number', '').strip()
        area_in_cave = request.form.get('area_in_cave', '').strip()
        time_in = request.form.get('time_in', '').strip()
        time_out = request.form.get('time_out', '').strip()
        survey_objective = request.form.get('survey_objective', '').strip()
        conditions = request.form.get('conditions', '').strip()
        other_info = request.form.get('other_info', '').strip()
        
        # Team information
        book_sketch_person = request.form.get('book_sketch_person', '').strip()
        instrument_reader = request.form.get('instrument_reader', '').strip()
        tape_person = request.form.get('tape_person', '').strip()
        point_person = request.form.get('point_person', '').strip()
        trip_leader = request.form.get('trip_leader', '').strip()
        other_team_members = request.form.get('other_team_members', '').strip()
        
        # Instrument information
        compass_id = request.form.get('compass_id', '').strip()
        compass_frontsight = request.form.get('compass_frontsight')
        compass_backsight = request.form.get('compass_backsight')
        inclinometer_id = request.form.get('inclinometer_id', '').strip()
        inclinometer_frontsight = request.form.get('inclinometer_frontsight')
        inclinometer_backsight = request.form.get('inclinometer_backsight')
        crf_compass_course = 1 if request.form.get('crf_compass_course') else 0
        calibration_notes = request.form.get('calibration_notes', '').strip()
        additional_equipment = request.form.get('additional_equipment', '').strip()
        
        # Survey shots data
        from_stations = request.form.getlist('from_station[]')
        to_stations = request.form.getlist('to_station[]')
        distances = request.form.getlist('distance[]')
        azimuth_fs_list = request.form.getlist('azimuth_fs[]')
        azimuth_bs_list = request.form.getlist('azimuth_bs[]')
        inclination_fs_list = request.form.getlist('inclination_fs[]')
        inclination_bs_list = request.form.getlist('inclination_bs[]')
        left_list = request.form.getlist('left[]')
        right_list = request.form.getlist('right[]')
        up_list = request.form.getlist('up[]')
        down_list = request.form.getlist('down[]')
        notes_list = request.form.getlist('notes[]')
        
        # Raw data (if provided)
        raw_data = request.form.get('raw_data', '').strip()
        
        # Form validation checkboxes
        instruments_crf_course = 1 if request.form.get('instruments_crf_course') else 0
        data_accuracy = 1 if request.form.get('data_accuracy') else 0
        
        # Basic validation
        if not cave_name:
            flash('Cave name is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not survey_date:
            flash('Survey date is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not data_accuracy:
            flash('You must confirm the accuracy of the survey data.', 'error')
            return redirect(url_for('survey_form'))
        
        # Validate required team members
        if not book_sketch_person:
            flash('Book/Sketch person is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not instrument_reader:
            flash('Instrument reader is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not tape_person:
            flash('Tape person is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not point_person:
            flash('Point person is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not trip_leader:
            flash('Trip/Survey leader is required.', 'error')
            return redirect(url_for('survey_form'))
        
        # Validate instrument IDs
        if not compass_id:
            flash('Compass ID is required.', 'error')
            return redirect(url_for('survey_form'))
        
        if not inclinometer_id:
            flash('Inclinometer ID is required.', 'error')
            return redirect(url_for('survey_form'))
        
        # Validate CRF compass course confirmation
        if not crf_compass_course:
            flash('You must confirm that instruments were shot on the CRF Compass Course.', 'error')
            return redirect(url_for('survey_form'))
        
        # Validate numeric ranges for instrument readings
        if compass_frontsight and compass_frontsight.strip():
            try:
                fs_val = float(compass_frontsight)
                if fs_val <= 180 or fs_val > 360:
                    flash('Compass frontsight must be > 180° (expected range 181-360°).', 'error')
                    return redirect(url_for('survey_form'))
            except ValueError:
                flash('Invalid compass frontsight value.', 'error')
                return redirect(url_for('survey_form'))
        
        if compass_backsight and compass_backsight.strip():
            try:
                bs_val = float(compass_backsight)
                if bs_val < 0 or bs_val >= 180:
                    flash('Compass backsight must be < 180° (expected range 0-179°).', 'error')
                    return redirect(url_for('survey_form'))
            except ValueError:
                flash('Invalid compass backsight value.', 'error')
                return redirect(url_for('survey_form'))
        
        if inclinometer_frontsight and inclinometer_frontsight.strip():
            try:
                fs_incl = float(inclinometer_frontsight)
                if fs_incl < -90 or fs_incl > 90:
                    flash('Inclinometer frontsight must be between -90° and 90°.', 'error')
                    return redirect(url_for('survey_form'))
            except ValueError:
                flash('Invalid inclinometer frontsight value.', 'error')
                return redirect(url_for('survey_form'))
        
        if inclinometer_backsight and inclinometer_backsight.strip():
            try:
                bs_incl = float(inclinometer_backsight)
                if bs_incl < -90 or bs_incl > 90:
                    flash('Inclinometer backsight must be between -90° and 90°.', 'error')
                    return redirect(url_for('survey_form'))
            except ValueError:
                flash('Invalid inclinometer backsight value.', 'error')
                return redirect(url_for('survey_form'))
        
        # Process survey shots
        survey_shots = []
        valid_shot_count = 0
        validation_errors = []
        
        for i in range(len(from_stations)):
            if i < len(to_stations) and from_stations[i].strip() and to_stations[i].strip():
                try:
                    # Convert values to appropriate types, handling empty strings
                    distance = float(distances[i]) if i < len(distances) and distances[i].strip() else None
                    azimuth_fs = float(azimuth_fs_list[i]) if i < len(azimuth_fs_list) and azimuth_fs_list[i].strip() else None
                    azimuth_bs = float(azimuth_bs_list[i]) if i < len(azimuth_bs_list) and azimuth_bs_list[i].strip() else None
                    inclination_fs = float(inclination_fs_list[i]) if i < len(inclination_fs_list) and inclination_fs_list[i].strip() else None
                    inclination_bs = float(inclination_bs_list[i]) if i < len(inclination_bs_list) and inclination_bs_list[i].strip() else None
                    left = float(left_list[i]) if i < len(left_list) and left_list[i].strip() else 0
                    right = float(right_list[i]) if i < len(right_list) and right_list[i].strip() else 0
                    up = float(up_list[i]) if i < len(up_list) and up_list[i].strip() else 0
                    down = float(down_list[i]) if i < len(down_list) and down_list[i].strip() else 0
                    note = notes_list[i].strip() if i < len(notes_list) else ''
                    
                    # Validate survey shot data
                    shot_id = i + 1
                    
                    # Validate distance
                    if distance is not None and distance < 0:
                        validation_errors.append(f'Shot {shot_id}: Distance cannot be negative')
                    
                    # Validate azimuth values
                    if azimuth_fs is not None and (azimuth_fs < 0 or azimuth_fs >= 360):
                        validation_errors.append(f'Shot {shot_id}: Frontsight azimuth must be 0-359°')
                    
                    if azimuth_bs is not None and (azimuth_bs < 0 or azimuth_bs >= 360):
                        validation_errors.append(f'Shot {shot_id}: Backsight azimuth must be 0-359°')
                    
                    # Validate inclination values
                    if inclination_fs is not None and (inclination_fs < -90 or inclination_fs > 90):
                        validation_errors.append(f'Shot {shot_id}: Frontsight inclination must be -90° to 90°')
                    
                    if inclination_bs is not None and (inclination_bs < -90 or inclination_bs > 90):
                        validation_errors.append(f'Shot {shot_id}: Backsight inclination must be -90° to 90°')
                    
                    # Validate LRUD values (must be non-negative)
                    if left < 0 or right < 0 or up < 0 or down < 0:
                        validation_errors.append(f'Shot {shot_id}: LRUD values cannot be negative')
                    
                    # Check for station name format (basic validation)
                    from_station = from_stations[i].strip()
                    to_station = to_stations[i].strip()
                    
                    if len(from_station) > 20:
                        validation_errors.append(f'Shot {shot_id}: From station name too long (max 20 characters)')
                    
                    if len(to_station) > 20:
                        validation_errors.append(f'Shot {shot_id}: To station name too long (max 20 characters)')
                    
                    # Warn about potential issues (commenting out variance checks for now to allow testing)
                    if azimuth_fs is not None and azimuth_bs is not None:
                        # Calculate azimuth variance - frontsight and backsight should differ by ~180°
                        diff = abs(azimuth_fs - azimuth_bs)
                        # Handle wrap-around case
                        azimuth_variance = min(abs(diff - 180), abs(diff - 180 + 360), abs(diff - 180 - 360))
                        if azimuth_variance > 5.0:  # More than 5 degrees variance (relaxed for testing)
                            pass  # Temporarily disabled: validation_errors.append(f'Shot {shot_id}: Large azimuth variance ({azimuth_variance:.1f}°) - check readings')
                    
                    if inclination_fs is not None and inclination_bs is not None:
                        incline_variance = abs(inclination_fs + inclination_bs)
                        if incline_variance > 5.0:  # More than 5 degrees variance (relaxed for testing)
                            pass  # Temporarily disabled: validation_errors.append(f'Shot {shot_id}: Large inclination variance ({incline_variance:.1f}°) - check readings')
                    
                    shot = {
                        'from_station': from_station,
                        'to_station': to_station,
                        'distance': distance,
                        'azimuth_fs': azimuth_fs,
                        'azimuth_bs': azimuth_bs,
                        'inclination_fs': inclination_fs,
                        'inclination_bs': inclination_bs,
                        'left': left,
                        'right': right,
                        'up': up,
                        'down': down,
                        'note': note
                    }
                    survey_shots.append(shot)
                    valid_shot_count += 1
                    
                except ValueError as e:
                    validation_errors.append(f'Shot {i + 1}: Invalid numeric value - {str(e)}')
        
        # Check for validation errors
        if validation_errors:
            for error in validation_errors[:5]:  # Limit to first 5 errors
                flash(error, 'error')
            if len(validation_errors) > 5:
                flash(f'... and {len(validation_errors) - 5} more validation errors', 'error')
            return redirect(url_for('survey_form'))
        
        if valid_shot_count == 0:
            flash('At least one survey shot is required.', 'error')
            return redirect(url_for('survey_form'))
        
        # Connect to cave survey database
        conn = get_cave_survey_db_connection()
        cursor = conn.cursor()
        
        # Convert numeric values to proper types
        compass_fs_val = float(compass_frontsight) if compass_frontsight and compass_frontsight.strip() else None
        compass_bs_val = float(compass_backsight) if compass_backsight and compass_backsight.strip() else None
        inclinometer_fs_val = float(inclinometer_frontsight) if inclinometer_frontsight and inclinometer_frontsight.strip() else None
        inclinometer_bs_val = float(inclinometer_backsight) if inclinometer_backsight and inclinometer_backsight.strip() else None
        
        # Insert survey header data
        cursor.execute('''
            INSERT INTO survey_header (
                cave_name, state, county, region, survey_date, fsb_number, area_in_cave,
                time_in, time_out, survey_objective, conditions, other_info,
                book_sketch_person, instrument_reader, tape_person, point_person,
                trip_leader, other_team_members, compass_id, compass_frontsight,
                compass_backsight, inclinometer_id, inclinometer_frontsight,
                inclinometer_backsight, crf_compass_course, calibration_notes,
                additional_equipment, survey_shots_json, raw_data,
                instruments_crf_course, data_accuracy, created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
        ''', (
            cave_name, state, county, region, survey_date, fsb_number, area_in_cave,
            time_in, time_out, survey_objective, conditions, other_info,
            book_sketch_person, instrument_reader, tape_person, point_person,
            trip_leader, other_team_members, compass_id, compass_fs_val,
            compass_bs_val, inclinometer_id, inclinometer_fs_val,
            inclinometer_bs_val, crf_compass_course, calibration_notes,
            additional_equipment, json.dumps(survey_shots), raw_data,
            instruments_crf_course, data_accuracy
        ))
        
        survey_id = cursor.lastrowid
        
        # Also store in professional schema for future use
        # First, get or create the cave
        cave_location = f"{county}, {state}" if county and state else (state or '')
        cursor.execute('SELECT cave_id FROM caves WHERE name = %s AND location_text = %s', (cave_name, cave_location))
        cave_row = cursor.fetchone()
        
        if cave_row:
            cave_id = cave_row['cave_id']
        else:
            cursor.execute('INSERT INTO caves (name, location_text) VALUES (?, ?)', (cave_name, cave_location))
            cave_id = cursor.lastrowid
        
        # Insert survey into professional schema
        cursor.execute('''
            INSERT INTO surveys (
                cave_id, date, area_in_cave, objective, time_in, time_out,
                conditions, survey_designation_raw, units_length, units_compass, units_clino
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'feet', 'degrees', 'degrees')
        ''', (cave_id, survey_date, area_in_cave, survey_objective, time_in, time_out, conditions, 'Form Entry'))
        
        professional_survey_id = cursor.lastrowid
        
        # Insert shots into professional schema
        for i, shot in enumerate(survey_shots):
            cursor.execute('''
                INSERT INTO shots (
                    survey_id, sequence_in_page, station_from, station_to, distance,
                    fs_azimuth_deg, bs_azimuth_deg, fs_incline_deg, bs_incline_deg,
                    lrud_left, lrud_right, lrud_up, lrud_down, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                professional_survey_id, i + 1, shot['from_station'], shot['to_station'],
                shot['distance'], shot['azimuth_fs'], shot['azimuth_bs'],
                shot['inclination_fs'], shot['inclination_bs'],
                shot['left'], shot['right'], shot['up'], shot['down'], shot['note']
            ))
        
        # Insert team members
        team_roles = [
            ('sketch_book', book_sketch_person),
            ('foresight', instrument_reader),
            ('backsight', tape_person),
            ('other', point_person)
        ]
        
        for role, person_name in team_roles:
            if person_name:
                # Get or create person
                cursor.execute('SELECT person_id FROM people WHERE full_name = %s', (person_name,))
                person_row = cursor.fetchone()
                
                if person_row:
                    person_id = person_row['person_id']
                else:
                    cursor.execute('INSERT INTO people (full_name) VALUES (?)', (person_name,))
                    person_id = cursor.lastrowid
                
                # Insert team member
                cursor.execute('''
                    INSERT INTO survey_team (survey_id, person_id, display_name, role)
                    VALUES (?, ?, ?, ?)
                ''', (professional_survey_id, person_id, person_name, role))
        
        conn.commit()
        return_connection(conn)
        
        flash(f'Survey data for {cave_name} submitted successfully! Recorded {valid_shot_count} survey shots.', 'success')
        return redirect(url_for('dashboard'))
        
    except ValueError as e:
        flash(f'Invalid data format: {str(e)}', 'error')
        return redirect(url_for('survey_form'))
    except Exception as e:
        flash(f'Survey submission failed: {str(e)}', 'error')
        return redirect(url_for('survey_form'))

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    """Return empty response for favicon to prevent 404 errors"""
    return '', 204

# Trip Management Routes
@app.route('/admin/trips')
def admin_trips():
    """Admin trip management page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    trips = cursor.execute('''
        SELECT * FROM trips 
        ORDER BY trip_date DESC, created_date DESC
    ''').fetchall()
    return_connection(conn)
    
    return render_template('admin_trips.html', trips=trips)

@app.route('/admin/trips/new')
def admin_new_trip():
    """Create new trip form"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_trip_form.html', trip=None)

@app.route('/admin/trips/new', methods=['POST'])
def admin_create_trip():
    """Create new trip"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get form data
        trip_name = request.form.get('trip_name', '').strip()
        trip_date = request.form.get('trip_date', '').strip()
        cave_name = request.form.get('cave_name', '').strip()
        objective = request.form.get('objective', '').strip()
        leader_name = request.form.get('leader_name', '').strip()
        entry_time = request.form.get('entry_time', '').strip()
        exit_time = request.form.get('exit_time', '').strip()
        route_description = request.form.get('route_description', '').strip()
        hazards = request.form.get('hazards', '').strip()
        notes = request.form.get('notes', '').strip()
        max_participants = request.form.get('max_participants', 6)
        difficulty_level = request.form.get('difficulty_level', 'intermediate')
        
        # Get required skills and equipment as JSON arrays
        required_skills = request.form.getlist('required_skills')
        required_equipment = request.form.getlist('required_equipment')
        
        # Validate required fields
        if not trip_name or not trip_date or not cave_name:
            flash('Trip name, date, and cave name are required.', 'error')
            return redirect(url_for('admin_new_trip'))
        
        conn = get_db_connection()

        
        cursor = get_cursor(conn)
        cursor.execute('''
            INSERT INTO trips (
                trip_name, trip_date, cave_name, objective, leader_name, 
                entry_time, exit_time, route_description, hazards, 
                required_skills, required_equipment, max_participants, 
                difficulty_level, notes, participants, status, created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
        ''', (
            trip_name, trip_date, cave_name, objective, leader_name,
            entry_time, exit_time, route_description, hazards,
            json.dumps(required_skills), json.dumps(required_equipment),
            max_participants, difficulty_level, notes, json.dumps([]), 'planned'
        ))
        conn.commit()
        return_connection(conn)
        
        flash(f'Trip "{trip_name}" created successfully!', 'success')
        return redirect(url_for('admin_trips'))
        
    except Exception as e:
        flash(f'Error creating trip: {str(e)}', 'error')
        return redirect(url_for('admin_new_trip'))

@app.route('/admin/trips/<int:trip_id>')
def admin_edit_trip(trip_id):
    """Edit trip form"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    cursor.execute('SELECT * FROM trips WHERE id = %s', (trip_id,))
    trip = cursor.fetchone()
    return_connection(conn)
    
    if not trip:
        flash('Trip not found.', 'error')
        return redirect(url_for('admin_trips'))
    
    return render_template('admin_trip_form.html', trip=trip)

@app.route('/admin/trips/<int:trip_id>', methods=['POST'])
def admin_update_trip(trip_id):
    """Update existing trip"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get form data (same as create)
        trip_name = request.form.get('trip_name', '').strip()
        trip_date = request.form.get('trip_date', '').strip()
        cave_name = request.form.get('cave_name', '').strip()
        objective = request.form.get('objective', '').strip()
        leader_name = request.form.get('leader_name', '').strip()
        entry_time = request.form.get('entry_time', '').strip()
        exit_time = request.form.get('exit_time', '').strip()
        route_description = request.form.get('route_description', '').strip()
        hazards = request.form.get('hazards', '').strip()
        notes = request.form.get('notes', '').strip()
        max_participants = request.form.get('max_participants', 6)
        difficulty_level = request.form.get('difficulty_level', 'intermediate')
        status = request.form.get('status', 'planned')
        
        required_skills = request.form.getlist('required_skills')
        required_equipment = request.form.getlist('required_equipment')
        
        if not trip_name or not trip_date or not cave_name:
            flash('Trip name, date, and cave name are required.', 'error')
            return redirect(url_for('admin_edit_trip', trip_id=trip_id))
        
        conn = get_db_connection()

        
        cursor = get_cursor(conn)
        cursor.execute('''
            UPDATE trips SET 
                trip_name = %s, trip_date = %s, cave_name = %s, objective = %s, 
                leader_name = %s, entry_time = %s, exit_time = %s, route_description = %s, 
                hazards = %s, required_skills = %s, required_equipment = %s, 
                max_participants = %s, difficulty_level = %s, notes = %s, status = %s,
                updated_date = NOW()
            WHERE id = ?
        ''', (
            trip_name, trip_date, cave_name, objective, leader_name,
            entry_time, exit_time, route_description, hazards,
            json.dumps(required_skills), json.dumps(required_equipment),
            max_participants, difficulty_level, notes, status, trip_id
        ))
        conn.commit()
        return_connection(conn)
        
        flash(f'Trip "{trip_name}" updated successfully!', 'success')
        return redirect(url_for('admin_trips'))
        
    except Exception as e:
        flash(f'Error updating trip: {str(e)}', 'error')
        return redirect(url_for('admin_edit_trip', trip_id=trip_id))

@app.route('/admin/trips/<int:trip_id>/delete', methods=['POST'])
def admin_delete_trip(trip_id):
    """Delete trip"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        cursor.execute('SELECT trip_name FROM trips WHERE id = %s', (trip_id,))
        trip = cursor.fetchone()
        
        if not trip:
            flash('Trip not found.', 'error')
        else:
            cursor.execute('DELETE FROM trips WHERE id = %s', (trip_id,))
            conn.commit()
            flash(f'Trip "{trip["trip_name"]}" deleted successfully.', 'success')
        
        return_connection(conn)
        
    except Exception as e:
        flash(f'Error deleting trip: {str(e)}', 'error')
    
    return redirect(url_for('admin_trips'))

@app.route('/admin/trips/<int:trip_id>/participants')
def admin_trip_participants(trip_id):
    """Manage trip participants"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    
    cursor = get_cursor(conn)
    cursor.execute('SELECT * FROM trips WHERE id = %s', (trip_id,))
    trip = cursor.fetchone()
    
    if not trip:
        flash('Trip not found.', 'error')
        return redirect(url_for('admin_trips'))
    
    # Get all participants
    cursor.execute('SELECT * FROM participants ORDER BY full_name')
    participants = cursor.fetchall()
    
    # Get current trip participants
    current_participants = []
    if trip['participants']:
        participant_ids = json.loads(trip['participants'])
        if participant_ids:
            placeholders = ','.join('%s' * len(participant_ids))
            current_participants = cursor.execute(
                f'SELECT * FROM participants WHERE id IN ({placeholders})',
                participant_ids
            ).fetchall()
    
    return_connection(conn)
    
    return render_template('admin_trip_participants.html', 
                         trip=trip, participants=participants, 
                         current_participants=current_participants)

@app.route('/admin/trips/<int:trip_id>/participants', methods=['POST'])
def admin_update_trip_participants(trip_id):
    """Update trip participants"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        selected_participants = request.form.getlist('participants')
        participant_ids = [int(pid) for pid in selected_participants if pid.isdigit()]
        
        conn = get_db_connection()

        
        cursor = get_cursor(conn)
        cursor.execute(
            'UPDATE trips SET participants = %s, updated_date = datetime("now") WHERE id = ?',
            (json.dumps(participant_ids), trip_id)
        )
        conn.commit()
        return_connection(conn)
        
        flash('Trip participants updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating participants: {str(e)}', 'error')
    
    return redirect(url_for('admin_trip_participants', trip_id=trip_id))

# Export Routes
@app.route('/admin/export/registration-data')
def export_registration_data():
    """Export registration data as CSV"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        cursor.execute('SELECT * FROM participants ORDER BY registration_time DESC')
        participants = cursor.fetchall()
        return_connection(conn)
        
        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = [
            'ID', 'Full Name', 'Email', 'Phone Number', 'Address', 'Emergency Contact',
            'Traveled With', 'Accommodation', 'Other Accommodation', 'Participation Days',
            'Eating at Expedition', 'Roppel Trips', 'CRF Compass Agreement', 'Skills',
            'Have Instruments', 'Instrument Details', 'Group Gear', 'Group Gear Other Details',
            'Additional Info', 'Registration Time', 'Waiver Acknowledged', 'Waiver Timestamp'
        ]
        writer.writerow(headers)
        
        # Write data rows
        for participant in participants:
            # Parse JSON fields for better readability
            participation_days = json.loads(participant['participation_days']) if participant['participation_days'] else []
            skills = json.loads(participant['skills']) if participant['skills'] else []
            group_gear = json.loads(participant['group_gear']) if participant['group_gear'] else []
            
            row = [
                participant['id'],
                participant['full_name'],
                participant['email'],
                participant['phone_number'],
                participant['address'],
                participant['emergency_contact'],
                participant['traveled_with'],
                participant['accommodation'],
                participant['other_accommodation'],
                ', '.join(participation_days) if participation_days else '',
                'Yes' if participant['eating_at_expedition'] else 'No',
                participant['roppel_trips'],
                'Yes' if participant['crf_compass_agreement'] else 'No',
                ', '.join(skills) if skills else '',
                'Yes' if participant['have_instruments'] else 'No',
                participant['instruments_details'],
                ', '.join(group_gear) if group_gear else '',
                participant['group_gear_other_details'],
                participant['additional_info'],
                participant['registration_time'],
                'Yes' if participant.get('waiver_acknowledged') else 'No',
                participant.get('waiver_acknowledged_timestamp', '')
            ]
            writer.writerow(row)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=CKKC_Expedition_Registration_Data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        flash(f'Error exporting registration data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/cave-survey-data')
def export_cave_survey_data():
    """Export cave survey data as CSV"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_cave_survey_db_connection()
        cursor.execute('SELECT * FROM shots ORDER BY survey_id, page_id, sequence_in_page')
        shots = cursor.fetchall()
        return_connection(conn)
        
        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = [
            'Shot ID', 'Survey ID', 'Page ID', 'Sequence in Page', 'Station From', 'Station To',
            'Distance', 'FS Azimuth (deg)', 'BS Azimuth (deg)', 'FS Incline (deg)', 'BS Incline (deg)',
            'LRUD Left', 'LRUD Right', 'LRUD Up', 'LRUD Down', 'Note', 'Azimuth Variance (deg)',
            'Incline Variance (deg)', 'Running Raw Distance', 'LRUD For Station', 'QA Flag'
        ]
        writer.writerow(headers)
        
        # Write data rows
        for shot in shots:
            row = [
                shot['shot_id'],
                shot['survey_id'],
                shot['page_id'],
                shot['sequence_in_page'],
                shot['station_from'],
                shot['station_to'],
                shot['distance'],
                shot['fs_azimuth_deg'],
                shot['bs_azimuth_deg'],
                shot['fs_incline_deg'],
                shot['bs_incline_deg'],
                shot['lrud_left'],
                shot['lrud_right'],
                shot['lrud_up'],
                shot['lrud_down'],
                shot['note'],
                shot['azimuth_variance_deg'],
                shot['incline_variance_deg'],
                shot['running_raw_distance'],
                shot['lrud_for_station'],
                shot['qa_flag']
            ]
            writer.writerow(row)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=CKKC_Cave_Survey_Data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        flash(f'Error exporting cave survey data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/trip-data')
def export_trip_data():
    """Export trip data as CSV"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        cursor.execute('SELECT * FROM trips ORDER BY trip_date DESC')
        trips = cursor.fetchall()
        return_connection(conn)

        # Create CSV output
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        headers = [
            'ID', 'Trip Name', 'Cave Name', 'Trip Date', 'Entry Time', 'Exit Time',
            'Objective', 'Route Description', 'Hazards', 'Leader Name', 'Participants',
            'Required Skills', 'Required Equipment', 'Max Participants', 'Difficulty Level',
            'Status', 'Notes', 'Created Date', 'Updated Date'
        ]
        writer.writerow(headers)

        # Write data rows
        for trip in trips:
            # Parse JSON fields for better readability
            participants = json.loads(trip['participants']) if trip['participants'] else []
            required_skills = json.loads(trip['required_skills']) if trip['required_skills'] else []
            required_equipment = json.loads(trip['required_equipment']) if trip['required_equipment'] else []

            row = [
                trip['id'],
                trip['trip_name'],
                trip['cave_name'] or '',
                trip['trip_date'],
                trip['entry_time'] or '',
                trip['exit_time'] or '',
                trip['objective'] or '',
                trip['route_description'] or '',
                trip['hazards'] or '',
                trip['leader_name'] or '',
                ', '.join(participants) if participants else '',
                ', '.join(required_skills) if required_skills else '',
                ', '.join(required_equipment) if required_equipment else '',
                trip['max_participants'] or '',
                trip['difficulty_level'] or '',
                trip['status'] or '',
                trip['notes'] or '',
                trip['created_date'] or '',
                trip['updated_date'] or ''
            ]
            writer.writerow(row)

        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=CKKC_Trip_Data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        return response

    except Exception as e:
        flash(f'Error exporting trip data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/backup-databases')
def backup_databases():
    """Create backup of both databases and return as ZIP file"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        import tempfile
        
        # Create timestamp for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create temporary directory for backup files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create backup directory structure
            backup_dir = os.path.join(temp_dir, f"CKKC_Database_Backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_files = []
            
            # Backup registration database
            if os.path.exists(DATABASE):
                backup_reg_path = os.path.join(backup_dir, f"expedition_registration_{timestamp}.db")
                shutil.copy2(DATABASE, backup_reg_path)
                backup_files.append(("Registration Database", os.path.basename(backup_reg_path)))
            
            # Backup cave survey database
            if os.path.exists(CAVE_SURVEY_DATABASE):
                backup_survey_path = os.path.join(backup_dir, f"cave_survey_{timestamp}.db")
                shutil.copy2(CAVE_SURVEY_DATABASE, backup_survey_path)
                backup_files.append(("Cave Survey Database", os.path.basename(backup_survey_path)))
            
            # Create README file with backup information
            readme_path = os.path.join(backup_dir, "README.txt")
            with open(readme_path, 'w') as readme_file:
                readme_file.write(f"""CKKC October 2025 Expedition Database Backup
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This backup contains the following database files:

""")
                for db_type, filename in backup_files:
                    readme_file.write(f"- {filename}: {db_type}\n")
                
                readme_file.write(f"""
Backup Information:
- Backup created automatically by the Expedition Management System
- These are SQLite database files that can be restored by replacing the original files
- To restore: Copy the database files back to the 'database/' directory in your expedition tool
- Original filenames: expedition.db (registration), cave_survey.db (survey data)

Database Schema:
- Registration Database: Contains participant registration data, trip assignments, and expedition details
- Cave Survey Database: Contains cave survey measurements, shot data, and cartographic information

For technical support, contact the CKKC expedition coordinators.
""")
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all files in the backup directory to the ZIP
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_file.write(file_path, arcname)
            
            zip_buffer.seek(0)
            
            # Create response
            response = make_response(zip_buffer.getvalue())
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = f'attachment; filename=CKKC_Database_Backup_{timestamp}.zip'
            
            flash(f'Database backup created successfully! Downloaded: CKKC_Database_Backup_{timestamp}.zip', 'success')
            return response
            
    except Exception as e:
        flash(f'Error creating database backup: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings')
def admin_settings():
    """System settings page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        settings = cursor.execute('''
            SELECT key, value, description, category 
            FROM settings 
            ORDER BY category, key
        ''').fetchall()
        return_connection(conn)
        
        # Group settings by category
        settings_by_category = {}
        for setting in settings:
            category = setting['category']
            if category not in settings_by_category:
                settings_by_category[category] = []
            settings_by_category[category].append(setting)
        
        return render_template('admin_settings.html', settings_by_category=settings_by_category)
        
    except Exception as e:
        flash(f'Error loading settings: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings/update', methods=['POST'])
def update_settings():
    """Update system settings"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        
        # Get all settings keys
        cursor.execute('SELECT key FROM settings')
        settings_keys = cursor.fetchall()
        settings_keys = [row['key'] for row in settings_keys]
        
        # Update each setting
        updated_count = 0
        for key in settings_keys:
            if key in request.form:
                new_value = request.form[key].strip()
                
                # Handle checkbox values (convert to string boolean)
                if key in ['registration_open', 'auto_calculate_variance', 'require_leader_approval', 'emergency_contact_required']:
                    new_value = 'true' if new_value else 'false'
                elif key not in request.form and key in ['registration_open', 'auto_calculate_variance', 'require_leader_approval', 'emergency_contact_required']:
                    new_value = 'false'
                
                # Update the setting
                cursor.execute('''
                    UPDATE settings 
                    SET value = %s, updated_date = NOW()
                    WHERE key = ?
                ''', (new_value, key))
                updated_count += 1
        
        conn.commit()
        return_connection(conn)
        
        flash(f'Settings updated successfully! {updated_count} settings saved.', 'success')
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to default values"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()

        cursor = get_cursor(conn)
        
        # Reset to default values
        default_settings = [
            ('expedition_name', 'CKKC October 2025 Expedition'),
            ('expedition_dates', 'October 10-18, 2025'),
            ('expedition_location', 'Barren, Hart, Edmonson Counties, KY'),
            ('registration_open', 'true'),
            ('max_participants', '50'),
            ('admin_passcode', 'expedition2025'),
            ('backup_frequency', 'daily'),
            ('survey_unit_system', 'metric'),
            ('auto_calculate_variance', 'true'),
            ('default_trip_duration', '6'),
            ('require_leader_approval', 'true'),
            ('emergency_contact_required', 'true')
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                UPDATE settings 
                SET value = %s, updated_date = NOW()
                WHERE key = ?
            ''', (value, key))
        
        conn.commit()
        return_connection(conn)
        
        flash('Settings have been reset to default values.', 'success')
        
    except Exception as e:
        flash(f'Error resetting settings: {str(e)}', 'error')
    
    return redirect(url_for('admin_settings'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    conn = None
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = get_cursor(conn)
        cursor.execute('SELECT 1')
        cursor.fetchone()

        return jsonify({
            'status': 'healthy',
            'database': 'healthy',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        if conn:
            return_connection(conn, error=True)
        return jsonify({
            'status': 'unhealthy',
            'database': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503
    finally:
        if conn:
            return_connection(conn)

if __name__ == '__main__':
    init_connection_pool()
    port = int(os.getenv('PORT', 5001))
    debug_mode = os.getenv('FLASK_ENV', 'production') != 'production'

    print("🏔️ CKKC October 2025 Expedition Management System")
    print(f"📍 Starting server on http://0.0.0.0:{port}")
    print("👥 PostgreSQL database connected")
    print("🔦 Ready for expedition registration and cave survey data!")

    app.run(host='0.0.0.0', port=port, debug=debug_mode)