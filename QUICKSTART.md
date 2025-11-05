# CKKC Expedition Management System - Quick Start Guide

## ⚡ Get Started in 3 Minutes

### Prerequisites
- Docker and Docker Compose installed on your system
- 2GB RAM and 5GB disk space available

### Step 1: Configure Environment (30 seconds)

```bash
cd /home/ajbir/ckkc-web-deployment

# Copy environment template
cp .env.example .env

# IMPORTANT: Edit .env and change these values:
nano .env
```

**Must Change:**
- `POSTGRES_PASSWORD` - Set a strong database password
- `FLASK_SECRET_KEY` - Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `ADMIN_PASSCODE` - Change from default "expedition2025"

### Step 2: Deploy (2 minutes)

```bash
# Make deploy script executable (if not already)
chmod +x deploy.sh

# Run automated deployment
./deploy.sh
```

The script will:
- ✓ Build Docker containers
- ✓ Start PostgreSQL database
- ✓ Initialize database schema
- ✓ Start Flask web application
- ✓ Perform health checks

### Step 3: Access Application (10 seconds)

Open your browser:
- **Main Application**: http://localhost:5001
- **Admin Dashboard**: http://localhost:5001/admin

## 🧪 Verify Deployment

```bash
./test_deployment.sh
```

This runs 8 automated tests to ensure everything works correctly.

## 📋 Common Commands

```bash
# View logs
docker-compose logs -f web

# Restart application
docker-compose restart web

# Stop everything
docker-compose down

# Backup database
docker-compose exec db pg_dump -U ckkc_user expedition_db > backup.sql

# Restore database
docker-compose exec -T db psql -U ckkc_user expedition_db < backup.sql
```

## 🔧 Troubleshooting

### Application won't start
```bash
# Check logs
docker-compose logs web db

# Restart services
docker-compose restart
```

### Database connection errors
```bash
# Verify database is running
docker-compose ps

# Test connection
docker-compose exec db pg_isready -U ckkc_user
```

### Port already in use
```bash
# Find process using port 5001
lsof -i :5001

# Change port in docker-compose.yml
# Edit: ports: - "8080:5001"
```

## 🌐 Deploy to Cloud

### Heroku (Free/Hobby Tier)
```bash
heroku create ckkc-expedition
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Railway.app (Simple, Modern)
1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

## 📚 More Information

- **Full Documentation**: See README.md
- **Deployment Details**: See DEPLOYMENT_SUMMARY.md
- **Original Location**: /mnt/c/Users/Public/ckkc2025app/lightweight-exped-tool

## 🎯 What's Different from Original?

| Feature | Original | Web Deployment |
|---------|----------|----------------|
| Database | SQLite (file) | PostgreSQL |
| Access | Local only | Network accessible |
| Users | Single user | Multiple concurrent users |
| Setup | Python venv | Docker containers |
| Frontend | Same | Same (unchanged) |

## ✅ Checklist Before Production

- [ ] Changed POSTGRES_PASSWORD
- [ ] Changed FLASK_SECRET_KEY
- [ ] Changed ADMIN_PASSCODE
- [ ] Tested registration flow
- [ ] Tested cave survey entry
- [ ] Tested admin dashboard
- [ ] Set up database backups
- [ ] Added HTTPS (nginx + Let's Encrypt)
- [ ] Configured firewall rules
- [ ] Set up monitoring

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f`
2. Run tests: `./test_deployment.sh`
3. Review README.md for detailed documentation
4. Check DEPLOYMENT_SUMMARY.md for technical details

---

**Ready to deploy? Run:** `./deploy.sh`
