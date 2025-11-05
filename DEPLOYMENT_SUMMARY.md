# CKKC Expedition Management System - Deployment Summary

## Conversion Overview

Successfully converted the CKKC Expedition Management System from **SQLite (offline)** to **PostgreSQL (web-deployable)** deployment.

## What Was Changed

### Backend Database
- **Before**: SQLite (file-based database in `database/` folder)
- **After**: PostgreSQL (enterprise-grade relational database)
- **Why**: Support concurrent users, better data integrity, production-ready

### Database Operations
- Replaced `sqlite3` library with `psycopg2` (PostgreSQL adapter)
- Updated all SQL queries:
  - `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
  - `?` placeholders → `%s` placeholders
  - `datetime('now')` → `NOW()`
  - `INSERT OR IGNORE` → `INSERT ... ON CONFLICT DO NOTHING`
- Implemented connection pooling for efficient database access
- Updated cursor handling to use `RealDictCursor` for dictionary-like row access

### Configuration
- **Before**: Hardcoded configuration in `app.py`
- **After**: Environment variables via `.env` file
- Added configurable: DATABASE_URL, FLASK_SECRET_KEY, ADMIN_PASSCODE

### Deployment Method
- **Before**: Local Python execution (`python3 app.py`)
- **After**: Docker containerization with Docker Compose
- Added production-grade WSGI server (Gunicorn) instead of Flask development server

## What Stayed the Same

### Frontend (100% Unchanged)
- All HTML templates in `templates/` folder
- All CSS, JavaScript, and images in `static/` folder
- User interface and experience identical to original
- All forms, layouts, and styling preserved

### Application Logic
- Registration workflow
- Cave survey data entry
- Trip management features
- Admin dashboard functionality
- All business logic and validation rules

## Files in Deployment Package

### Core Application Files
```
app.py                 - Main Flask application (converted to PostgreSQL)
templates/            - HTML templates (unchanged from original)
static/               - CSS, JS, images (unchanged from original)
requirements.txt      - Python dependencies
```

### Database Files
```
init_db.sql           - PostgreSQL schema definition
                       (replaces init_db() and init_cave_survey_db() functions)
```

### Deployment Files
```
Dockerfile            - Container image definition
docker-compose.yml    - Multi-container orchestration (web + database)
.env.example          - Environment variable template
.env                  - Actual environment configuration (not in git)
.dockerignore         - Files to exclude from Docker image
.gitignore            - Files to exclude from version control
```

### Utility Scripts
```
deploy.sh             - Automated deployment script
test_deployment.sh    - Validation and health check script
```

### Documentation
```
README.md             - Comprehensive deployment guide
DEPLOYMENT_SUMMARY.md - This file
```

## Database Schema

### Registration Tables
- `participants` - Expedition participant information
- `trips` - Planned cave trips

### Cave Survey Tables
- `caves` - Cave information
- `surveys` - Survey metadata
- `survey_series` - Survey series codes
- `people` - Survey team members
- `survey_team` - Team member roles per survey
- `instruments` - Survey instruments
- `survey_instruments` - Instruments used per survey
- `survey_ties` - Survey connection ties
- `survey_notes` - Survey notes
- `book_pages` - Survey book pages
- `shots` - Individual survey measurements
- `survey_header` - Legacy survey form data

### Configuration Tables
- `settings` - Application settings and configuration

### Views
- `v_shots_export` - Export-ready view of shot data

## Deployment Methods Supported

1. **Docker Compose** (Recommended)
   - Simple one-command deployment
   - Includes PostgreSQL database
   - Perfect for development, testing, and small production deployments

2. **Cloud Platforms**
   - Heroku
   - Railway.app
   - Render.com
   - AWS, DigitalOcean, Google Cloud, Azure

3. **VPS** (DigitalOcean, Linode, etc.)
   - Full control over infrastructure
   - Can use provided Docker Compose setup
   - Or deploy natively with systemd

## Quick Start Commands

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 2. Deploy
./deploy.sh

# 3. Test deployment
./test_deployment.sh

# 4. Access application
# Web: http://localhost:5001
# Admin: http://localhost:5001/admin
```

## Production Considerations

### Security
- ✅ Environment-based configuration
- ✅ Password protection for admin access
- ⚠️ Add HTTPS reverse proxy (nginx) for production
- ⚠️ Change all default passwords
- ⚠️ Use strong Flask secret key

### Performance
- ✅ Connection pooling (1-20 connections)
- ✅ Gunicorn with 4 workers
- ⚠️ Scale workers based on CPU cores (2-4 × CPU count)
- ⚠️ Add caching layer (Redis) for high traffic

### Reliability
- ✅ Health checks for containers
- ✅ Automatic restarts on failure
- ⚠️ Set up automated backups
- ⚠️ Monitor logs and metrics

### Scalability
- ✅ Stateless application design
- ✅ Database connection pooling
- ⚠️ Can add multiple web instances behind load balancer
- ⚠️ Database can be scaled separately

## Backup Strategy

### Automated Daily Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U ckkc_user expedition_db > backups/backup_$DATE.sql
find backups/ -name "backup_*.sql" -mtime +7 -delete  # Keep 7 days
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/ckkc-web-deployment/backup.sh
```

### Restore from Backup
```bash
docker-compose exec -T db psql -U ckkc_user expedition_db < backups/backup_20251104_020000.sql
```

## Migration from SQLite Version

If you have existing data in the SQLite version:

### Option 1: CSV Export/Import
1. In old version: Admin Dashboard → Export Data → Download CSV
2. Deploy new version
3. In new version: Admin Dashboard → Import Data → Upload CSV

### Option 2: Direct Database Migration (Advanced)
```bash
# Export from SQLite
sqlite3 database/expedition.db .dump > sqlite_dump.sql

# Convert SQL dialect (manual adjustments needed)
# Import to PostgreSQL
psql -U ckkc_user -d expedition_db -f converted_dump.sql
```

## Testing Checklist

Before going live:

- [ ] Update all passwords in `.env`
- [ ] Generate secure Flask secret key
- [ ] Test participant registration flow
- [ ] Test cave survey data entry
- [ ] Test trip management
- [ ] Test admin login and dashboard
- [ ] Test data export functionality
- [ ] Verify database backups work
- [ ] Load test with expected user count
- [ ] Set up monitoring and alerting
- [ ] Configure HTTPS/SSL
- [ ] Test disaster recovery procedure

## Support and Maintenance

### View Logs
```bash
docker-compose logs -f web    # Application logs
docker-compose logs -f db     # Database logs
```

### Database Console
```bash
docker-compose exec db psql -U ckkc_user -d expedition_db
```

### Update Application
```bash
git pull
./deploy.sh
```

### Restart Services
```bash
docker-compose restart web    # Restart web app only
docker-compose restart        # Restart all services
```

### Stop Services
```bash
docker-compose stop           # Stop (can restart)
docker-compose down           # Stop and remove containers
docker-compose down -v        # Stop, remove containers AND data (⚠️ DANGER)
```

## Technical Specifications

- **Web Framework**: Flask 3.1.2
- **Database**: PostgreSQL 16
- **Python**: 3.12
- **WSGI Server**: Gunicorn
- **Container Runtime**: Docker + Docker Compose
- **Minimum Resources**: 2GB RAM, 5GB disk, 1 CPU core
- **Recommended**: 4GB RAM, 20GB disk, 2+ CPU cores

## Known Limitations

1. **File Uploads**: Currently no file upload functionality
2. **Real-time Updates**: No WebSocket support (page refresh required)
3. **Multi-tenancy**: Designed for single expedition use
4. **Internationalization**: English only

## Future Enhancements (Optional)

- Add Redis for caching and session management
- Implement real-time collaboration with WebSockets
- Add file upload for survey sketches/photos
- API endpoints for mobile app integration
- Advanced reporting and analytics dashboard
- Multi-expedition support with tenant isolation
- Email notifications for trip assignments
- Integration with cave survey software (Compass, Therion)

---

**Conversion Date**: November 4, 2025
**Original Version**: CKKC October 2025 Expedition Management System (SQLite)
**New Version**: CKKC Expedition Management System v1.0.0 (PostgreSQL Web)
