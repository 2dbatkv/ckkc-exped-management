-- CKKC Expedition Management System
-- PostgreSQL Database Initialization Script

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- EXPEDITION REGISTRATION DATABASE
-- ============================================

-- Participants table
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    address TEXT NOT NULL,
    emergency_contact TEXT NOT NULL,
    traveled_with TEXT,
    accommodation TEXT NOT NULL,
    other_accommodation TEXT,
    participation_days TEXT,  -- JSON array of selected days
    eating_at_expedition BOOLEAN DEFAULT FALSE,
    roppel_trips TEXT,
    crf_compass_agreement BOOLEAN DEFAULT FALSE,
    skills TEXT,  -- JSON array of skills
    have_instruments BOOLEAN DEFAULT FALSE,
    instruments_details TEXT,
    group_gear TEXT,  -- JSON array of gear
    group_gear_other_details TEXT,
    additional_info TEXT,
    waiver_acknowledged BOOLEAN DEFAULT TRUE,
    waiver_acknowledged_timestamp TIMESTAMP,
    registration_time TIMESTAMP DEFAULT NOW()
);

-- Trips table
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    trip_name TEXT NOT NULL,
    trip_date DATE,
    objective TEXT,
    leader_name TEXT,
    participants TEXT,  -- JSON array of participant IDs
    status TEXT DEFAULT 'planned',
    cave_name TEXT,
    entry_time TEXT,
    exit_time TEXT,
    route_description TEXT,
    hazards TEXT,
    required_skills TEXT,  -- JSON array
    required_equipment TEXT,  -- JSON array
    max_participants INTEGER DEFAULT 6,
    difficulty_level TEXT DEFAULT 'intermediate',
    notes TEXT,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CAVE SURVEY DATABASE
-- ============================================

-- Caves table
CREATE TABLE IF NOT EXISTS caves (
    cave_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location_text TEXT
);

-- Surveys table
CREATE TABLE IF NOT EXISTS surveys (
    survey_id SERIAL PRIMARY KEY,
    cave_id INTEGER REFERENCES caves(cave_id) ON DELETE SET NULL ON UPDATE CASCADE,
    date TEXT,
    area_in_cave TEXT,
    objective TEXT,
    prefix TEXT,
    time_in TEXT,
    time_out TEXT,
    conditions TEXT,
    survey_designation_raw TEXT,
    units_length TEXT DEFAULT 'feet',
    units_compass TEXT DEFAULT 'degrees',
    units_clino TEXT DEFAULT 'degrees',
    data_order_note TEXT,
    format_note TEXT,
    sheet_note TEXT,
    protection_note TEXT
);

-- Survey series table
CREATE TABLE IF NOT EXISTS survey_series (
    series_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    series_code TEXT
);

-- People table
CREATE TABLE IF NOT EXISTS people (
    person_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL
);

-- Survey team table
CREATE TABLE IF NOT EXISTS survey_team (
    survey_team_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    person_id INTEGER REFERENCES people(person_id) ON DELETE SET NULL ON UPDATE CASCADE,
    display_name TEXT,
    role TEXT CHECK (role IN ('sketch_book','foresight','backsight','other'))
);

-- Instruments table
CREATE TABLE IF NOT EXISTS instruments (
    instrument_id SERIAL PRIMARY KEY,
    model TEXT,
    serial_number TEXT,
    owner_name TEXT
);

-- Survey instruments table
CREATE TABLE IF NOT EXISTS survey_instruments (
    survey_instrument_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE ON UPDATE CASCADE,
    position_label TEXT
);

-- Survey ties table
CREATE TABLE IF NOT EXISTS survey_ties (
    survey_tie_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    tie_text TEXT,
    target_survey_code TEXT,
    target_station_label TEXT
);

-- Survey notes table
CREATE TABLE IF NOT EXISTS survey_notes (
    survey_note_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    note_index INTEGER,
    note_text TEXT
);

-- Book pages table
CREATE TABLE IF NOT EXISTS book_pages (
    page_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    page_number INTEGER
);

-- Shots table
CREATE TABLE IF NOT EXISTS shots (
    shot_id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE ON UPDATE CASCADE,
    page_id INTEGER REFERENCES book_pages(page_id) ON DELETE SET NULL ON UPDATE CASCADE,
    sequence_in_page INTEGER,
    station_from TEXT NOT NULL,
    station_to TEXT NOT NULL,
    distance REAL,
    fs_azimuth_deg REAL,
    bs_azimuth_deg REAL,
    fs_incline_deg REAL,
    bs_incline_deg REAL,
    lrud_left REAL DEFAULT 0,
    lrud_right REAL DEFAULT 0,
    lrud_up REAL DEFAULT 0,
    lrud_down REAL DEFAULT 0,
    note TEXT,
    azimuth_variance_deg REAL,
    incline_variance_deg REAL,
    running_raw_distance REAL,
    lrud_for_station TEXT,
    qa_flag INTEGER DEFAULT 0 CHECK (qa_flag IN (0,1)),
    CHECK (fs_azimuth_deg IS NULL OR (fs_azimuth_deg >= 0 AND fs_azimuth_deg < 360)),
    CHECK (bs_azimuth_deg IS NULL OR (bs_azimuth_deg >= 0 AND bs_azimuth_deg < 360)),
    CHECK (fs_incline_deg IS NULL OR (fs_incline_deg >= -90 AND fs_incline_deg <= 90)),
    CHECK (bs_incline_deg IS NULL OR (bs_incline_deg >= -90 AND bs_incline_deg <= 90)),
    CHECK (distance IS NULL OR distance >= 0),
    CHECK (lrud_left >= 0 AND lrud_right >= 0 AND lrud_up >= 0 AND lrud_down >= 0)
);

-- Survey header table (for backwards compatibility with forms)
CREATE TABLE IF NOT EXISTS survey_header (
    id SERIAL PRIMARY KEY,
    cave_name TEXT NOT NULL,
    state TEXT,
    county TEXT,
    region TEXT,
    survey_date TEXT,
    area_in_cave TEXT,
    time_in TEXT,
    time_out TEXT,
    survey_objective TEXT,
    conditions TEXT,
    other_info TEXT,
    book_sketch_person TEXT,
    instrument_reader TEXT,
    tape_person TEXT,
    point_person TEXT,
    trip_leader TEXT,
    other_team_members TEXT,
    compass_id TEXT,
    compass_frontsight REAL,
    compass_backsight REAL,
    inclinometer_id TEXT,
    inclinometer_frontsight REAL,
    inclinometer_backsight REAL,
    crf_compass_course INTEGER DEFAULT 0,
    calibration_notes TEXT,
    additional_equipment TEXT,
    survey_shots_json TEXT,
    raw_data TEXT,
    instruments_crf_course INTEGER DEFAULT 0,
    data_accuracy INTEGER DEFAULT 0,
    fsb_number TEXT,
    created_date TIMESTAMP DEFAULT NOW()
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    category TEXT,
    updated_date TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_shots_survey_from ON shots(survey_id, station_from);
CREATE INDEX IF NOT EXISTS idx_shots_survey_to ON shots(survey_id, station_to);
CREATE INDEX IF NOT EXISTS idx_shots_page_seq ON shots(page_id, sequence_in_page);
CREATE INDEX IF NOT EXISTS idx_survey_team_role ON survey_team(survey_id, role);

-- ============================================
-- VIEWS
-- ============================================

CREATE OR REPLACE VIEW v_shots_export AS
SELECT
    station_from AS "From",
    station_to AS "To",
    distance AS "Distance",
    fs_azimuth_deg AS "Azimuth",
    fs_incline_deg AS "Inclination",
    lrud_left AS "Left",
    lrud_right AS "Right",
    lrud_up AS "Up",
    lrud_down AS "Down",
    note AS "Comment",
    survey_id
FROM shots;

-- ============================================
-- DEFAULT SETTINGS
-- ============================================

INSERT INTO settings (key, value, description, category, updated_date)
VALUES
    ('expedition_name', 'CKKC October 2025 Expedition', 'Name of the expedition', 'expedition', NOW()),
    ('expedition_dates', 'October 10-18, 2025', 'Date range for the expedition', 'expedition', NOW()),
    ('expedition_location', 'Barren, Hart, Edmonson Counties, KY', 'Location of the expedition', 'expedition', NOW()),
    ('registration_open', 'true', 'Whether registration is open for new participants', 'registration', NOW()),
    ('max_participants', '50', 'Maximum number of participants allowed', 'registration', NOW()),
    ('admin_passcode', 'expedition2025', 'Administrator access passcode', 'security', NOW()),
    ('backup_frequency', 'daily', 'How often to remind about backups', 'database', NOW()),
    ('survey_unit_system', 'metric', 'Default unit system for cave surveys (metric/imperial)', 'survey', NOW()),
    ('auto_calculate_variance', 'true', 'Automatically calculate azimuth/incline variance', 'survey', NOW()),
    ('default_trip_duration', '6', 'Default trip duration in hours', 'trips', NOW()),
    ('require_leader_approval', 'true', 'Require trip leader approval for participants', 'trips', NOW()),
    ('emergency_contact_required', 'true', 'Require emergency contact information', 'safety', NOW())
ON CONFLICT (key) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✓ Database initialized successfully';
END $$;
