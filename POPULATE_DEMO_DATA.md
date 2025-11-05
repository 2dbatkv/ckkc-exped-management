# Populate Demonstration Data

This guide explains how to populate your CKKC Expedition database with fictional demonstration data.

## ⚠️ What This Does

The `populate_dummy_data.py` script will:
- **Clear all existing data** from your database
- Add **10 fictional participants** from popular animations:
  - Scooby-Doo gang: Shaggy, Scooby, Velma, Daphne, Fred
  - SpongeBob characters: SpongeBob, Patrick, Sandy
  - Adventure Time: Finn, Jake
- Create **5 demo cave trips** with these characters
- Add **sample caves and survey data**
- Enable **demo mode** with disclaimer banner

## 🚀 How to Run (From Local Machine)

### Prerequisites

You need the DATABASE_URL from your Render PostgreSQL database:
```
postgresql://ckkc_expedition_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/ckkc_expedition
```

### Option 1: Run Locally with Python

```bash
cd /home/ajbir/ckkc-web-deployment

# Set the database URL (use the EXTERNAL URL from Render)
export DATABASE_URL="postgresql://ckkc_expedition_user:naC6cVFNQBxSfGNIDXNVd8WiLFbJWtSZ@dpg-d455ueili9vc73cgu69g-a.oregon-postgres.render.com/ckkc_expedition"

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install psycopg2-binary python-dotenv

# Run the script
python3 populate_dummy_data.py

# Deactivate when done
deactivate
```

### Option 2: Run Directly with psql

```bash
# Connect to your database
export PGPASSWORD='naC6cVFNQBxSfGNIDXNVd8WiLFbJWtSZ'

psql -h dpg-d455ueili9vc73cgu69g-a.oregon-postgres.render.com \
     -U ckkc_expedition_user \
     -d ckkc_expedition \
     -c "DELETE FROM shots; DELETE FROM book_pages; DELETE FROM survey_notes; DELETE FROM survey_ties; DELETE FROM survey_instruments; DELETE FROM survey_team; DELETE FROM survey_series; DELETE FROM surveys; DELETE FROM survey_header; DELETE FROM trips; DELETE FROM participants; DELETE FROM people; DELETE FROM instruments; DELETE FROM caves;"

# Then run the populate script
python3 populate_dummy_data.py
```

### Option 3: Run via Render Shell (SSH)

1. **Install Render CLI** (if not already installed):
   ```bash
   npm install -g @render-com/cli
   render login
   ```

2. **SSH into your Render service**:
   ```bash
   render shell ckkc-expedition-web
   ```

3. **Inside the Render shell**:
   ```bash
   cd /opt/render/project/src
   python3 populate_dummy_data.py
   exit
   ```

## 📊 Expected Output

When the script runs successfully, you'll see:

```
======================================================================
🎬 CKKC Expedition - Dummy Data Population Script
   Using fictional animation characters for demonstration
======================================================================

✓ Connected to database...
🧹 Clearing existing data...
✓ Cleared existing data
👥 Adding participants (fictional animation characters)...
✓ Added 10 participants
🏔️ Adding cave trips...
✓ Added 5 cave trips
🗺️ Adding caves and survey data...
✓ Added 5 caves and sample survey data
⚠️ Adding demonstration disclaimer...
✓ Added demonstration disclaimer

======================================================================
✅ SUCCESS! Dummy data populated successfully!

📊 Summary:
   - 10 Fictional participants (Scooby-Doo, SpongeBob, Adventure Time)
   - 5 Demo cave trips
   - 5 Demo caves with sample survey data
   - Disclaimer added to settings

⚠️  REMINDER: This is demonstration data using fictional characters.
   Clear this data before collecting real expedition information!
======================================================================
```

## 🎭 What Gets Added

### Participants (10)
1. **Shaggy Rogers** - Mystery Inc., tent camping, vertical & photography skills
2. **Scooby-Doo** - Mystery Inc., tent camping, vertical & navigation
3. **Velma Dinkley** - Mystery Inc., cabin, advanced surveying skills
4. **Daphne Blake** - Mystery Inc., cabin, photography & vertical
5. **Fred Jones** - Mystery Inc., RV, trip leader with full survey kit
6. **SpongeBob SquarePants** - Bikini Bottom, tent, vertical skills
7. **Patrick Star** - Bikini Bottom, tent, beginner
8. **Sandy Cheeks** - Bikini Bottom, tent, science expedition leader
9. **Finn the Human** - Land of Ooo, tent, vertical & rigging
10. **Jake the Dog** - Land of Ooo, tent, navigation & vertical

### Cave Trips (5)
1. **Mystery Machine Cave Tour** - Fred leading survey in Mammoth Cave
2. **Scooby Snacks Underground Expedition** - Shaggy exploring Roppel Cave
3. **Scientific Survey Expedition** - Sandy's geological documentation
4. **Mathematical Cave Adventure** - Finn & Jake's exploration
5. **Bikini Bottom Cave Hike** - SpongeBob's beginner-friendly tour

### Caves (5)
- Mystery Cave (Coolsville, OH)
- Mammoth Cave (Kentucky)
- Roppel Cave (Kentucky)
- Crystal Onyx Cave (Fictional)
- Hidden River Cave (Kentucky)

## 🔄 How to Clear Demo Data

If you want to remove the demo data later:

```bash
# Connect via psql
psql "postgresql://ckkc_expedition_user:PASSWORD@HOST/ckkc_expedition"

# Delete all data
DELETE FROM shots;
DELETE FROM book_pages;
DELETE FROM survey_notes;
DELETE FROM survey_ties;
DELETE FROM survey_instruments;
DELETE FROM survey_team;
DELETE FROM survey_series;
DELETE FROM surveys;
DELETE FROM survey_header;
DELETE FROM trips;
DELETE FROM participants;
DELETE FROM people;
DELETE FROM instruments;
DELETE FROM caves;

# Disable demo mode
UPDATE settings SET value = 'false' WHERE key = 'demo_mode_enabled';
```

## ⚠️ Important Notes

1. **This script DELETES all existing data** - Only use on fresh databases or when you want to reset
2. **Use fictional data only for demonstrations** - Clear before real expedition
3. **The disclaimer banner will appear** on the dashboard automatically
4. All data is clearly marked as fictional/demonstration in character names and descriptions

## 🎨 Demo Mode Features

Once populated:
- Yellow disclaimer banner appears on dashboard
- All participant names are clearly fictional
- Cave trips have humorous references to source material
- Email addresses use `.demo` domain
- Survey data includes sample measurements

## 🔐 Security

The demo data script:
- ✅ Uses environment variables for database credentials
- ✅ Includes clear warnings about fictional data
- ✅ Marks all data as demonstration/mockup
- ✅ Can be easily cleared/reset

---

**Questions?** Check the main README.md or deployment documentation files.
