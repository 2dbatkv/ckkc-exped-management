# CKKC Expedition Management System - Web Deployment

## Overview

This is the web-deployable version of the CKKC October 2025 Expedition Management System, converted from SQLite to PostgreSQL for production use.

**Features:**
- Participant registration and management
- Cave survey data entry and tracking
- Trip planning and management
- Admin dashboard with data export capabilities
- PostgreSQL backend for concurrent users
- Docker containerization for easy deployment

## Architecture Changes from Original

| Component | Original (Offline) | Web Deployment |
|-----------|-------------------|----------------|
| Database | SQLite (file-based) | PostgreSQL |
| Frontend | HTML/CSS/JS (unchanged) | HTML/CSS/JS (unchanged) |
| Backend | Flask + SQLite | Flask + psycopg2 |
| Deployment | Local Python | Docker + Docker Compose |
| Configuration | Hardcoded | Environment variables |

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- 2GB RAM minimum
- 5GB disk space

### 1. Clone and Configure

```bash
# Navigate to the deployment directory
cd ckkc-web-deployment

# Copy and configure environment variables
cp .env.example .env

# Edit .env with secure values
nano .env
```

**Important:** Update these values in `.env`:
- `POSTGRES_PASSWORD`: Use a strong password
- `FLASK_SECRET_KEY`: Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `ADMIN_PASSCODE`: Change from default

### 2. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 3. Initialize Database (First Time Only)

The database schema is automatically initialized from `init_db.sql` when the PostgreSQL container starts for the first time.

To manually run the initialization:

```bash
docker-compose exec db psql -U ckkc_user -d expedition_db -f /docker-entrypoint-initdb.d/init_db.sql
```

### 4. Access the Application

- **Main Application**: http://localhost:5001
- **Admin Dashboard**: http://localhost:5001/admin
- **Default Admin Passcode**: Set in your `.env` file

## Deployment Options

### Option 1: Docker Compose (Recommended for Development/Testing)

See "Quick Start" above.

### Option 2: Deploy to Cloud Platform

#### Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create ckkc-expedition

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ADMIN_PASSCODE=your_secure_passcode

# Deploy
git push heroku main

# Initialize database
heroku pg:psql < init_db.sql
```

#### Railway.app

1. Go to https://railway.app
2. Create new project → Deploy from GitHub
3. Add PostgreSQL database service
4. Set environment variables in the Variables tab
5. Deploy

#### Render.com

1. Create Web Service from GitHub repo
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

### Option 3: VPS Deployment (DigitalOcean, AWS EC2, etc.)

```bash
# SSH into your server
ssh user@your-server-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Clone your repository
git clone <your-repo-url>
cd ckkc-web-deployment

# Configure environment
cp .env.example .env
nano .env

# Deploy
docker-compose up -d

# Set up nginx reverse proxy (optional)
sudo apt install nginx
# Configure nginx to proxy to port 5001
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `FLASK_SECRET_KEY` | Yes | - | Flask session secret key |
| `ADMIN_PASSCODE` | No | `expedition2025` | Admin dashboard access code |
| `FLASK_ENV` | No | `production` | Flask environment |
| `PORT` | No | `5001` | Application port |

### Database Connection String Format

```
postgresql://username:password@host:port/database
```

**Examples:**
```bash
# Docker Compose
DATABASE_URL=postgresql://ckkc_user:mypassword@db:5432/expedition_db

# Heroku
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Local PostgreSQL
DATABASE_URL=postgresql://localhost:5432/expedition_db
```

## Database Management

### Backup Database

```bash
# Using Docker Compose
docker-compose exec db pg_dump -U ckkc_user expedition_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T db psql -U ckkc_user expedition_db < backup_20251104.sql
```

### Access Database Console

```bash
docker-compose exec db psql -U ckkc_user -d expedition_db
```

### View Tables

```sql
\dt  -- List all tables
SELECT * FROM participants LIMIT 10;
SELECT * FROM surveys LIMIT 10;
```

## Monitoring and Logs

### View Application Logs

```bash
# Follow logs
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100 web

# View database logs
docker-compose logs db
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Web app health endpoint
curl http://localhost:5001/

# Database health
docker-compose exec db pg_isready -U ckkc_user
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Database not ready - wait 30 seconds and retry
docker-compose restart web

# 2. Connection pool error - check DATABASE_URL
docker-compose exec web printenv DATABASE_URL

# 3. Port already in use
# Change PORT in .env or docker-compose.yml
```

### Database Connection Errors

```bash
# Test database connectivity
docker-compose exec web python3 -c "import psycopg2; psycopg2.connect('postgresql://ckkc_user:password@db:5432/expedition_db')"

# Check database is running
docker-compose exec db pg_isready

# Recreate database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Permission Errors

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Scaling and Performance

### Increase Workers

Edit `Dockerfile` and change gunicorn workers:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "8", "--timeout", "120", "app:app"]
```

### Database Connection Pooling

The app uses a connection pool (1-20 connections by default). To adjust, edit `app.py`:

```python
db_pool = pool.SimpleConnectionPool(1, 50, DATABASE_URL)  # Increase max to 50
```

### Add Load Balancer

For high traffic, deploy multiple instances behind a load balancer (nginx, HAProxy, or cloud load balancer).

## Security Considerations

1. **Change default credentials** - Never use default passwords in production
2. **Use HTTPS** - Deploy behind nginx with SSL/TLS certificates
3. **Firewall rules** - Restrict database access to application only
4. **Regular backups** - Automate daily database backups
5. **Update dependencies** - Keep Docker images and Python packages updated
6. **Environment variables** - Never commit `.env` file to git

## Maintenance

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d

# View startup logs
docker-compose logs -f web
```

### Database Migrations

For schema changes, create migration SQL files:

```bash
# Create migration file
cat > migrations/001_add_new_column.sql << 'EOF'
ALTER TABLE participants ADD COLUMN IF NOT EXISTS new_field TEXT;
EOF

# Apply migration
docker-compose exec db psql -U ckkc_user -d expedition_db -f /migrations/001_add_new_column.sql
```

## Development

### Local Development Without Docker

```bash
# Install PostgreSQL locally
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb expedition_db
sudo -u postgres createuser ckkc_user
sudo -u postgres psql -c "ALTER USER ckkc_user WITH PASSWORD 'dev_password';"

# Initialize schema
psql -U ckkc_user -d expedition_db -f init_db.sql

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://ckkc_user:dev_password@localhost:5432/expedition_db
export FLASK_SECRET_KEY=dev_secret_key
export FLASK_ENV=development

# Run application
python3 app.py
```

## Migration from SQLite Version

If you have existing data in the SQLite version:

1. Export data to CSV from the admin dashboard
2. Deploy this PostgreSQL version
3. Import CSV data through the admin dashboard's import feature
4. Or use the provided migration script (coming soon)

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review troubleshooting section above
- Ensure all environment variables are set correctly
- Verify database is initialized: `docker-compose exec db psql -U ckkc_user -d expedition_db -c '\dt'`

## File Structure

```
ckkc-web-deployment/
├── app.py                  # Main Flask application (PostgreSQL version)
├── requirements.txt        # Python dependencies
├── init_db.sql            # PostgreSQL schema initialization
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Multi-container orchestration
├── .env.example           # Environment variable template
├── .dockerignore          # Files to exclude from image
├── README.md              # This file
├── templates/             # HTML templates (unchanged from original)
│   ├── dashboard.html
│   ├── register_clean.html
│   ├── admin.html
│   └── ...
└── static/                # CSS, JS, images (unchanged)
    ├── css/
    ├── js/
    └── cave.png
```

## License

CKKC October 2025 Expedition Management System

---

**Last Updated:** November 4, 2025
**Version:** 1.0.0 - PostgreSQL Web Deployment
