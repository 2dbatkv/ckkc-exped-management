#!/usr/bin/env python3
"""
Populate CKKC Expedition Database with Dummy Demo Data
Uses fictional animation characters for demonstration purposes
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import json
import random

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/expedition_db')

def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def clear_existing_data(conn):
    """Clear existing demo data"""
    print("🧹 Clearing existing data...")
    cursor = conn.cursor()

    # Delete in order respecting foreign keys
    cursor.execute("DELETE FROM shots")
    cursor.execute("DELETE FROM book_pages")
    cursor.execute("DELETE FROM survey_notes")
    cursor.execute("DELETE FROM survey_ties")
    cursor.execute("DELETE FROM survey_instruments")
    cursor.execute("DELETE FROM survey_team")
    cursor.execute("DELETE FROM survey_series")
    cursor.execute("DELETE FROM surveys")
    cursor.execute("DELETE FROM survey_header")
    cursor.execute("DELETE FROM trips")
    cursor.execute("DELETE FROM participants")
    cursor.execute("DELETE FROM people")
    cursor.execute("DELETE FROM instruments")
    cursor.execute("DELETE FROM caves")

    conn.commit()
    print("✓ Cleared existing data")

def populate_participants(conn):
    """Add fictional animation character participants"""
    print("👥 Adding participants (fictional animation characters)...")

    participants = [
        {
            'full_name': 'Shaggy Rogers',
            'email': 'shaggy@mysteryinc.demo',
            'phone': '555-0101',
            'address': '123 Mystery Lane, Coolsville, OH',
            'emergency_contact': 'Scooby-Doo (Dog): 555-0102',
            'traveled_with': 'Scooby-Doo',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12', '2025-10-13']),
            'eating_at_expedition': True,
            'roppel_trips': 'Maybe interested in seeing the underground kitchen',
            'crf_compass_agreement': True,
            'skills': json.dumps(['vertical', 'sketching', 'photography']),
            'have_instruments': False,
            'group_gear': json.dumps(['tent', 'cooking_gear'])
        },
        {
            'full_name': 'Scooby-Doo',
            'email': 'scooby@mysteryinc.demo',
            'phone': '555-0102',
            'address': '123 Mystery Lane, Coolsville, OH',
            'emergency_contact': 'Shaggy Rogers: 555-0101',
            'traveled_with': 'Shaggy Rogers',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12']),
            'eating_at_expedition': True,
            'roppel_trips': 'Interested in Scooby Snacks Underground Tour',
            'crf_compass_agreement': True,
            'skills': json.dumps(['vertical', 'navigation']),
            'have_instruments': False,
            'group_gear': json.dumps(['tent'])
        },
        {
            'full_name': 'Velma Dinkley',
            'email': 'velma@mysteryinc.demo',
            'phone': '555-0103',
            'address': '456 Research Blvd, Coolsville, OH',
            'emergency_contact': 'Daphne Blake: 555-0104',
            'accommodation': 'cabin',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12', '2025-10-13', '2025-10-14']),
            'eating_at_expedition': True,
            'roppel_trips': 'Very interested in geological formations',
            'crf_compass_agreement': True,
            'skills': json.dumps(['surveying', 'sketching', 'navigation', 'vertical']),
            'have_instruments': True,
            'instruments_details': 'Brunton Compass, Suunto Clino',
            'group_gear': json.dumps(['rope', 'survey_instruments'])
        },
        {
            'full_name': 'Daphne Blake',
            'email': 'daphne@mysteryinc.demo',
            'phone': '555-0104',
            'address': '789 Fashion Ave, Coolsville, OH',
            'emergency_contact': 'Fred Jones: 555-0105',
            'accommodation': 'cabin',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12', '2025-10-13']),
            'eating_at_expedition': True,
            'roppel_trips': 'Interested in photography opportunities',
            'crf_compass_agreement': True,
            'skills': json.dumps(['photography', 'vertical']),
            'have_instruments': False,
            'group_gear': json.dumps(['cooking_gear'])
        },
        {
            'full_name': 'Fred Jones',
            'email': 'fred@mysteryinc.demo',
            'phone': '555-0105',
            'address': '321 Leadership St, Coolsville, OH',
            'emergency_contact': 'Velma Dinkley: 555-0103',
            'accommodation': 'rv',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12', '2025-10-13', '2025-10-14', '2025-10-15']),
            'eating_at_expedition': True,
            'roppel_trips': 'Leading several trips',
            'crf_compass_agreement': True,
            'skills': json.dumps(['navigation', 'vertical', 'rigging', 'rescue']),
            'have_instruments': True,
            'instruments_details': 'Complete survey kit with laser rangefinder',
            'group_gear': json.dumps(['rope', 'rigging_equipment', 'survey_instruments'])
        },
        {
            'full_name': 'SpongeBob SquarePants',
            'email': 'spongebob@bikinibottom.demo',
            'phone': '555-0201',
            'address': '124 Conch Street, Bikini Bottom',
            'emergency_contact': 'Patrick Star: 555-0202',
            'traveled_with': 'Patrick Star',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-12', '2025-10-13']),
            'eating_at_expedition': True,
            'roppel_trips': 'Ready for underwater... I mean underground adventure!',
            'crf_compass_agreement': True,
            'skills': json.dumps(['vertical']),
            'have_instruments': False,
            'group_gear': json.dumps(['tent'])
        },
        {
            'full_name': 'Patrick Star',
            'email': 'patrick@bikinibottom.demo',
            'phone': '555-0202',
            'address': '120 Conch Street, Bikini Bottom',
            'emergency_contact': 'SpongeBob SquarePants: 555-0201',
            'traveled_with': 'SpongeBob SquarePants',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-12', '2025-10-13']),
            'eating_at_expedition': True,
            'crf_compass_agreement': True,
            'skills': json.dumps([]),
            'have_instruments': False,
            'group_gear': json.dumps(['tent'])
        },
        {
            'full_name': 'Sandy Cheeks',
            'email': 'sandy@bikinibottom.demo',
            'phone': '555-0203',
            'address': 'Treedome, Bikini Bottom',
            'emergency_contact': 'SpongeBob SquarePants: 555-0201',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-11', '2025-10-12', '2025-10-13', '2025-10-14']),
            'eating_at_expedition': True,
            'roppel_trips': 'Science expedition participant',
            'crf_compass_agreement': True,
            'skills': json.dumps(['surveying', 'vertical', 'rigging', 'navigation']),
            'have_instruments': True,
            'instruments_details': 'Scientific equipment and survey tools',
            'group_gear': json.dumps(['rope', 'survey_instruments', 'scientific_equipment'])
        },
        {
            'full_name': 'Finn the Human',
            'email': 'finn@adventuretime.demo',
            'phone': '555-0301',
            'address': 'Tree Fort, Land of Ooo',
            'emergency_contact': 'Jake the Dog: 555-0302',
            'traveled_with': 'Jake the Dog',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-13', '2025-10-14', '2025-10-15']),
            'eating_at_expedition': True,
            'roppel_trips': 'Mathematical cave adventures!',
            'crf_compass_agreement': True,
            'skills': json.dumps(['vertical', 'rigging', 'rescue']),
            'have_instruments': False,
            'group_gear': json.dumps(['rope', 'tent'])
        },
        {
            'full_name': 'Jake the Dog',
            'email': 'jake@adventuretime.demo',
            'phone': '555-0302',
            'address': 'Tree Fort, Land of Ooo',
            'emergency_contact': 'Finn the Human: 555-0301',
            'traveled_with': 'Finn the Human',
            'accommodation': 'tent',
            'participation_days': json.dumps(['2025-10-13', '2025-10-14', '2025-10-15']),
            'eating_at_expedition': True,
            'roppel_trips': 'Stretchy abilities useful for tight passages',
            'crf_compass_agreement': True,
            'skills': json.dumps(['navigation', 'vertical']),
            'have_instruments': False,
            'group_gear': json.dumps(['tent'])
        }
    ]

    cursor = conn.cursor()
    for p in participants:
        cursor.execute('''
            INSERT INTO participants
            (full_name, email, phone_number, address, emergency_contact, traveled_with,
             accommodation, other_accommodation, participation_days, eating_at_expedition,
             roppel_trips, crf_compass_agreement, skills, have_instruments,
             instruments_details, group_gear, group_gear_other_details, additional_info,
             waiver_acknowledged, waiver_acknowledged_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (
            p['full_name'], p['email'], p['phone'], p['address'],
            p['emergency_contact'], p.get('traveled_with', ''),
            p['accommodation'], p.get('other_accommodation', ''),
            p['participation_days'], p['eating_at_expedition'],
            p.get('roppel_trips', ''), p['crf_compass_agreement'],
            p['skills'], p.get('have_instruments', False),
            p.get('instruments_details', ''),
            p.get('group_gear', '[]'), p.get('group_gear_other_details', ''),
            p.get('additional_info', ''), True
        ))

    conn.commit()
    print(f"✓ Added {len(participants)} participants")

def populate_trips(conn):
    """Add sample cave trips"""
    print("🏔️ Adding cave trips...")

    base_date = datetime(2025, 10, 11)

    trips = [
        {
            'trip_name': 'Mystery Machine Cave Tour',
            'trip_date': base_date,
            'cave_name': 'Mammoth Cave',
            'objective': 'Survey new passages in Historic Section',
            'leader_name': 'Fred Jones',
            'participants': json.dumps(['Fred Jones', 'Velma Dinkley', 'Daphne Blake']),
            'status': 'planned',
            'entry_time': '09:00',
            'exit_time': '15:00',
            'route_description': 'Enter via Historic Entrance, survey Gothic Avenue extension',
            'hazards': 'Low crawls, tight squeezes',
            'required_skills': json.dumps(['vertical', 'surveying']),
            'required_equipment': json.dumps(['helmet', 'headlamp', 'survey_instruments']),
            'max_participants': 6,
            'difficulty_level': 'intermediate',
            'notes': 'Looking for clues... I mean cave passages'
        },
        {
            'trip_name': 'Scooby Snacks Underground Expedition',
            'trip_date': base_date + timedelta(days=1),
            'cave_name': 'Roppel Cave',
            'objective': 'Push leads in the lunch room area',
            'leader_name': 'Shaggy Rogers',
            'participants': json.dumps(['Shaggy Rogers', 'Scooby-Doo', 'Velma Dinkley']),
            'status': 'planned',
            'entry_time': '10:00',
            'exit_time': '16:00',
            'route_description': 'Looking for the legendary underground kitchen',
            'hazards': 'Possible hungry cavers',
            'required_skills': json.dumps(['navigation']),
            'required_equipment': json.dumps(['helmet', 'headlamp', 'extra_snacks']),
            'max_participants': 4,
            'difficulty_level': 'beginner',
            'notes': 'Like, bring extra Scooby Snacks, man!'
        },
        {
            'trip_name': 'Scientific Survey Expedition',
            'trip_date': base_date + timedelta(days=2),
            'cave_name': 'Crystal Onyx Cave',
            'objective': 'Geological formations documentation',
            'leader_name': 'Sandy Cheeks',
            'participants': json.dumps(['Sandy Cheeks', 'Velma Dinkley', 'Fred Jones']),
            'status': 'planned',
            'entry_time': '08:00',
            'exit_time': '17:00',
            'route_description': 'Full scientific survey of formation room',
            'hazards': 'Delicate formations, watch your step',
            'required_skills': json.dumps(['surveying', 'photography', 'vertical']),
            'required_equipment': json.dumps(['survey_instruments', 'camera', 'measuring_tape']),
            'max_participants': 5,
            'difficulty_level': 'advanced',
            'notes': 'Texas-sized science expedition, y\'all!'
        },
        {
            'trip_name': 'Mathematical Cave Adventure',
            'trip_date': base_date + timedelta(days=3),
            'cave_name': 'Hidden River Cave',
            'objective': 'Explore uncharted passages',
            'leader_name': 'Finn the Human',
            'participants': json.dumps(['Finn the Human', 'Jake the Dog', 'Fred Jones']),
            'status': 'planned',
            'entry_time': '09:30',
            'exit_time': '16:30',
            'route_description': 'Adventure through new discoveries',
            'hazards': 'Unknown passages, water features',
            'required_skills': json.dumps(['vertical', 'navigation', 'rigging']),
            'required_equipment': json.dumps(['helmet', 'headlamp', 'rope', 'webbing']),
            'max_participants': 6,
            'difficulty_level': 'intermediate',
            'notes': 'Algebraic cave passages!'
        },
        {
            'trip_name': 'Bikini Bottom Cave Dive... Er, Hike',
            'trip_date': base_date + timedelta(days=1),
            'cave_name': 'Morrison Cave',
            'objective': 'Easy introduction trip',
            'leader_name': 'SpongeBob SquarePants',
            'participants': json.dumps(['SpongeBob SquarePants', 'Patrick Star', 'Sandy Cheeks']),
            'status': 'planned',
            'entry_time': '11:00',
            'exit_time': '14:00',
            'route_description': 'Gentle walking passages',
            'hazards': 'Minimal, beginner-friendly',
            'required_skills': json.dumps([]),
            'required_equipment': json.dumps(['helmet', 'headlamp']),
            'max_participants': 8,
            'difficulty_level': 'beginner',
            'notes': 'I\'m ready, I\'m ready, I\'m ready!'
        }
    ]

    cursor = conn.cursor()
    for trip in trips:
        cursor.execute('''
            INSERT INTO trips
            (trip_name, trip_date, cave_name, objective, leader_name,
             entry_time, exit_time, route_description, hazards,
             required_skills, required_equipment, max_participants,
             difficulty_level, notes, participants, status, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (
            trip['trip_name'], trip['trip_date'], trip['cave_name'],
            trip['objective'], trip['leader_name'], trip['entry_time'],
            trip['exit_time'], trip['route_description'], trip['hazards'],
            trip['required_skills'], trip['required_equipment'],
            trip['max_participants'], trip['difficulty_level'],
            trip['notes'], trip['participants'], trip['status']
        ))

    conn.commit()
    print(f"✓ Added {len(trips)} cave trips")

def populate_caves_and_surveys(conn):
    """Add sample caves and survey data"""
    print("🗺️ Adding caves and survey data...")

    cursor = conn.cursor()

    # Add caves
    caves = [
        ('Mystery Cave', 'Coolsville, OH - Fictional Location'),
        ('Mammoth Cave', 'Kentucky - Demo Data'),
        ('Roppel Cave', 'Kentucky - Demo Data'),
        ('Crystal Onyx Cave', 'Fictional Location'),
        ('Hidden River Cave', 'Kentucky - Demo Data')
    ]

    cave_ids = []
    for cave_name, location in caves:
        cursor.execute('INSERT INTO caves (name, location_text) VALUES (%s, %s) RETURNING cave_id',
                      (cave_name, location))
        cave_ids.append(cursor.fetchone()[0])

    # Add a sample survey
    cursor.execute('''
        INSERT INTO surveys
        (cave_id, date, area_in_cave, objective, time_in, time_out, conditions,
         survey_designation_raw, units_length, units_compass, units_clino)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING survey_id
    ''', (cave_ids[0], '2025-10-11', 'Mystery Passage', 'Initial Survey',
          '09:00', '15:00', 'Dry, excellent', 'DEMO-SURVEY-001',
          'feet', 'degrees', 'degrees'))

    survey_id = cursor.fetchone()[0]

    # Add people for survey team
    people_names = ['Velma Dinkley', 'Fred Jones', 'Daphne Blake']
    for name in people_names:
        cursor.execute('INSERT INTO people (full_name) VALUES (%s) RETURNING person_id', (name,))
        person_id = cursor.fetchone()[0]

        role = 'sketch_book' if name == 'Velma Dinkley' else ('foresight' if name == 'Fred Jones' else 'backsight')
        cursor.execute('''
            INSERT INTO survey_team (survey_id, person_id, display_name, role)
            VALUES (%s, %s, %s, %s)
        ''', (survey_id, person_id, name, role))

    # Add sample shots
    shots = [
        ('A1', 'A2', 25.5, 45.0, 225.0, 5.0, -5.0, 4.0, 3.0, 8.0, 6.0),
        ('A2', 'A3', 32.0, 90.0, 270.0, 0.0, 0.0, 5.0, 4.0, 10.0, 8.0),
        ('A3', 'A4', 18.3, 135.0, 315.0, -10.0, 10.0, 3.0, 3.0, 6.0, 5.0),
    ]

    for i, shot in enumerate(shots, 1):
        cursor.execute('''
            INSERT INTO shots
            (survey_id, sequence_in_page, station_from, station_to, distance,
             fs_azimuth_deg, bs_azimuth_deg, fs_incline_deg, bs_incline_deg,
             lrud_left, lrud_right, lrud_up, lrud_down, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (survey_id, i, *shot, 'Demo survey shot'))

    conn.commit()
    print(f"✓ Added {len(caves)} caves and sample survey data")

def add_disclaimer_setting(conn):
    """Add or update the disclaimer setting"""
    print("⚠️ Adding demonstration disclaimer...")

    cursor = conn.cursor()
    disclaimer_text = ("Mockup for demonstration purposes only. The data shown here does not reflect "
                      "the actual registration, cave trip, or survey data collected during the "
                      "October 2025 CKKC Expedition in Kentucky.")

    cursor.execute('''
        INSERT INTO settings (key, value, description, category, updated_date)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_date = NOW()
    ''', ('demo_mode_disclaimer', disclaimer_text, 'Disclaimer for demo/mockup mode', 'system'))

    cursor.execute('''
        INSERT INTO settings (key, value, description, category, updated_date)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_date = NOW()
    ''', ('demo_mode_enabled', 'true', 'Whether demo mode is active', 'system'))

    conn.commit()
    print("✓ Added demonstration disclaimer")

def main():
    """Main function to populate all dummy data"""
    print("=" * 70)
    print("🎬 CKKC Expedition - Dummy Data Population Script")
    print("   Using fictional animation characters for demonstration")
    print("=" * 70)
    print()

    try:
        conn = get_connection()
        print(f"✓ Connected to database: {DATABASE_URL[:50]}...")
        print()

        # Populate data
        clear_existing_data(conn)
        populate_participants(conn)
        populate_trips(conn)
        populate_caves_and_surveys(conn)
        add_disclaimer_setting(conn)

        conn.close()

        print()
        print("=" * 70)
        print("✅ SUCCESS! Dummy data populated successfully!")
        print()
        print("📊 Summary:")
        print("   - 10 Fictional participants (Scooby-Doo, SpongeBob, Adventure Time)")
        print("   - 5 Demo cave trips")
        print("   - 5 Demo caves with sample survey data")
        print("   - Disclaimer added to settings")
        print()
        print("⚠️  REMINDER: This is demonstration data using fictional characters.")
        print("   Clear this data before collecting real expedition information!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
