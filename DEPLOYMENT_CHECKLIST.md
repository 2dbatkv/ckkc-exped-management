# CKKC Expedition Management System - Deployment Checklist

Use this checklist to track your deployment progress.

## ✅ Pre-Deployment (Completed)

- [x] Convert SQLite to PostgreSQL
- [x] Create database schema (init_db.sql)
- [x] Update app.py for cloud deployment
- [x] Add health check endpoint
- [x] Create Docker configuration
- [x] Create Render configuration
- [x] Add environment variable support
- [x] Copy all frontend templates
- [x] Copy all static files
- [x] Initialize Git repository
- [x] Create initial commit

## 📋 GitHub Setup (Your Next Steps)

- [ ] Create GitHub account (if needed)
- [ ] Create new repository on GitHub
  - Name: `ckkc-expedition-web` (or your choice)
  - Visibility: Private (recommended) or Public
  - Do NOT initialize with README
- [ ] Get repository URL
- [ ] Add GitHub as remote: `git remote add origin <URL>`
- [ ] Push code: `git push -u origin main`
- [ ] Verify code is on GitHub
- [ ] Verify .env is NOT visible (it should be gitignored)

**Your Repository URL:**
```
https://github.com/YOUR_USERNAME/ckkc-expedition-web
```
_(Replace YOUR_USERNAME with your actual GitHub username)_

## ☁️ Cloud Deployment (Choose One)

### Option 1: Render.com (Recommended - Easiest)

- [ ] Create Render account at https://render.com
- [ ] Connect GitHub account to Render
- [ ] Choose deployment method:
  - [ ] **Blueprint** (Automated - uses render.yaml) OR
  - [ ] **Manual** (Follow RENDER_DEPLOYMENT.md)

#### If Using Blueprint:
- [ ] Click "New" → "Blueprint"
- [ ] Select your GitHub repository
- [ ] Render auto-creates database and web service
- [ ] Wait for deployment (3-5 minutes)

#### If Manual:
- [ ] Create PostgreSQL database
  - Name: `ckkc-expedition-db`
  - Plan: Starter ($7/mo) or Free (90 days)
  - Copy Internal Database URL
- [ ] Initialize database schema
  - Run init_db.sql in database shell
- [ ] Create Web Service
  - Connect to GitHub repo
  - Build command: `pip install --upgrade pip && pip install -r requirements.txt`
  - Start command: `gunicorn wsgi:application`
  - Health check: `/health`
- [ ] Set environment variables:
  - [ ] `DATABASE_URL` (from PostgreSQL service)
  - [ ] `FLASK_SECRET_KEY` (generate: `python3 -c "import secrets; print(secrets.token_hex(32))"`)
  - [ ] `ADMIN_PASSCODE` (change from default)
  - [ ] `FLASK_ENV=production`

### Option 2: Docker on VPS (DigitalOcean, etc.)

- [ ] Provision VPS server (2GB RAM minimum)
- [ ] Install Docker and Docker Compose
- [ ] Clone repository to server
- [ ] Copy .env.example to .env
- [ ] Update .env with production values
- [ ] Run: `./deploy.sh`
- [ ] Configure nginx reverse proxy (for HTTPS)
- [ ] Set up SSL certificate (Let's Encrypt)

### Option 3: Heroku

- [ ] Create Heroku account
- [ ] Install Heroku CLI
- [ ] Create app: `heroku create ckkc-expedition`
- [ ] Add PostgreSQL: `heroku addons:create heroku-postgresql:mini`
- [ ] Set environment variables
- [ ] Push to Heroku: `git push heroku main`
- [ ] Initialize database: `heroku pg:psql < init_db.sql`

## 🧪 Verify Deployment

- [ ] Health check works: `https://your-app-url/health`
  - Should return: `{"status": "healthy", "database": "healthy"}`
- [ ] Home page loads: `https://your-app-url/`
- [ ] Registration page works: `https://your-app-url/register`
- [ ] Participant list page: `https://your-app-url/participants`
- [ ] Cave survey page: `https://your-app-url/survey`
- [ ] Admin login works: `https://your-app-url/admin`
- [ ] Can register a test participant
- [ ] Can enter test cave survey data
- [ ] Can export data from admin dashboard
- [ ] Static files (CSS, images) load correctly
- [ ] All forms submit correctly
- [ ] No console errors in browser

## 🔒 Security Hardening

- [ ] Changed `ADMIN_PASSCODE` from default "expedition2025"
- [ ] Generated secure `FLASK_SECRET_KEY` (32+ character random string)
- [ ] Set strong database password
- [ ] Verified `.env` is NOT in GitHub (should be gitignored)
- [ ] Set repository to Private (if contains any sensitive info)
- [ ] Reviewed admin access controls
- [ ] Tested that health check doesn't expose sensitive info
- [ ] Configured HTTPS (automatic on Render, manual on VPS)
- [ ] Set up firewall rules (if on VPS)

## 📊 Production Readiness

- [ ] Set up automated database backups
  - Render: Starter plan or higher
  - VPS: Cron job with pg_dump
  - Heroku: Automated with paid plan
- [ ] Configure monitoring/alerting
  - Render: Built-in monitoring
  - VPS: Set up monitoring tool (e.g., UptimeRobot)
- [ ] Test database restore procedure
- [ ] Document admin credentials (in secure location)
- [ ] Create admin user guide
- [ ] Test all critical workflows
- [ ] Load test with expected user count
- [ ] Set up error tracking (optional: Sentry)

## 🌐 Optional Enhancements

- [ ] Set up custom domain
  - Purchase domain
  - Configure DNS CNAME
  - Verify SSL certificate
- [ ] Add multiple admin users (requires code changes)
- [ ] Set up staging environment
- [ ] Configure email notifications
- [ ] Add data export scheduling
- [ ] Implement API rate limiting
- [ ] Add CAPTCHA to registration form
- [ ] Set up CDN for static assets

## 📝 Documentation

- [ ] Document deployment process (completed ✓)
- [ ] Create user manual for expedition participants
- [ ] Create admin guide for managing data
- [ ] Document backup/restore procedures
- [ ] Create troubleshooting guide
- [ ] Document environment variables
- [ ] Create runbook for common tasks

## 🎓 Training & Launch

- [ ] Train admin users
- [ ] Test with small group of users
- [ ] Gather feedback
- [ ] Fix any issues found
- [ ] Announce to expedition participants
- [ ] Provide support during initial rollout
- [ ] Monitor usage and performance
- [ ] Collect user feedback

## 📅 Ongoing Maintenance

- [ ] Schedule regular database backups (daily recommended)
- [ ] Monitor application logs
- [ ] Check for security updates
- [ ] Update dependencies periodically
- [ ] Review and rotate secrets annually
- [ ] Test disaster recovery procedure quarterly
- [ ] Monitor costs (if on paid tier)
- [ ] Review and archive old expedition data

## 🆘 Emergency Contacts

**Technical Issues:**
- Render Support: https://render.com/support
- GitHub Support: https://support.github.com
- Your email: _________________

**Application Admin:**
- Name: _________________
- Email: _________________
- Phone: _________________

**Backup Admin:**
- Name: _________________
- Email: _________________
- Phone: _________________

## 📊 Deployment Status

**Current Phase:** Pre-Deployment Complete ✓

**Next Steps:**
1. Create GitHub repository
2. Push code to GitHub
3. Deploy to Render.com (or chosen platform)
4. Initialize database
5. Verify deployment
6. Secure the application
7. Go live!

**Deployment URL:** _________________________ (fill in after deployment)

**Database URL:** _________________________ (keep secure, don't share)

**Admin Passcode:** _________________________ (keep secure, don't share)

---

## Quick Command Reference

```bash
# Push to GitHub (run once)
git remote add origin https://github.com/YOUR_USERNAME/ckkc-expedition-web.git
git push -u origin main

# Future updates
git add .
git commit -m "Description of changes"
git push

# Generate Flask secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Test health endpoint
curl https://your-app-url/health

# View logs (Render)
render logs ckkc-expedition-web

# Backup database (Docker)
docker-compose exec db pg_dump -U ckkc_user expedition_db > backup.sql

# Restore database (Docker)
docker-compose exec -T db psql -U ckkc_user expedition_db < backup.sql
```

---

**Print this checklist and check off items as you complete them!**
