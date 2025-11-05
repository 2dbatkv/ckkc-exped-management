# Deploying to Render.com

## Overview

Render.com provides a simple way to deploy the CKKC Expedition Management System with managed PostgreSQL. This guide shows how to deploy using Render's free/starter tier.

## Prerequisites

- GitHub account with your code repository
- Render.com account (free tier available)

## Architecture

- **Web Service**: Flask application with Gunicorn
- **PostgreSQL**: Managed database (free tier: 90 days, then $7/month)
- **Static Assets**: Served directly by Flask

## Step-by-Step Deployment

### 1. Prepare Repository

Ensure your repository has:
```
ckkc-web-deployment/
├── app.py
├── requirements.txt
├── templates/
├── static/
└── init_db.sql
```

### 2. Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `ckkc-expedition-db`
   - **Database**: `expedition_db`
   - **User**: `ckkc_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (90 days) or Starter ($7/month)
4. Click **Create Database**
5. **Important**: Copy the **Internal Database URL** (starts with `postgresql://`)

### 3. Initialize Database Schema

After database is created:

1. Click on your database in Render dashboard
2. Go to **Shell** tab (or connect via CLI)
3. Run the initialization:

```bash
# In Render database shell
\i init_db.sql
```

Or from your local machine:
```bash
# Download your init_db.sql, then:
psql [YOUR_INTERNAL_DATABASE_URL] < init_db.sql
```

### 4. Create Web Service

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:

**Basic Settings:**
- **Name**: `ckkc-expedition-web`
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: Leave blank (or specify if in subdirectory)
- **Runtime**: Python 3

**Build & Deploy:**
- **Build Command**:
  ```bash
  pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
  ```

**Advanced:**
- **Health Check Path**: `/health`

### 5. Set Environment Variables

In the Web Service dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `[Internal Database URL]` | Copy from PostgreSQL service |
| `FLASK_SECRET_KEY` | `[Generate random]` | Use: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSCODE` | `your_secure_passcode` | Change from default |
| `FLASK_ENV` | `production` | |
| `PORT` | `10000` | Render provides this automatically |

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the application
   - Run health checks

3. Monitor deployment in the **Logs** tab

### 7. Verify Deployment

Once deployed, you'll get a URL like: `https://ckkc-expedition-web.onrender.com`

Test endpoints:
- Health check: `https://your-app.onrender.com/health`
- Main app: `https://your-app.onrender.com/`
- Admin: `https://your-app.onrender.com/admin`

## Configuration for Render

### Update app.py for PORT binding

Render uses the `PORT` environment variable. Ensure your app.py uses:

```python
if __name__ == '__main__':
    init_connection_pool()
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Static File Serving

Flask serves static files by default. For better performance in production, consider:

1. Using Render's CDN with `whitenoise`:
```bash
pip install whitenoise
```

2. Update app.py:
```python
from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
```

## Cost Estimate

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| PostgreSQL | 90 days free | $7/month (Starter) |
| Web Service | Free (limited) | $7/month (Starter) |
| **Total** | **$0 (90 days)** | **$14/month** |

**Free Tier Limitations:**
- Web service spins down after 15 minutes of inactivity (30-60 second cold start)
- 750 hours/month (suitable for hobby/testing)

**Starter Tier Benefits:**
- Always-on (no cold starts)
- Better performance
- More resources

## Custom Domain

1. Go to **Settings** → **Custom Domain**
2. Add your domain: `expedition.yourdomain.com`
3. Update DNS records as instructed
4. Render provides free SSL certificates automatically

## Monitoring & Maintenance

### View Logs
```bash
# Install Render CLI
npm install -g render-cli

# Login and view logs
render login
render logs ckkc-expedition-web
```

Or view in dashboard: **Logs** tab

### Database Backups

Render automatically backs up PostgreSQL databases:
- Free tier: Not included
- Starter tier: Daily backups, 7-day retention
- Pro tier: Daily backups, 30-day retention

Manual backup:
```bash
# Export database
pg_dump [DATABASE_URL] > backup.sql

# Restore
psql [DATABASE_URL] < backup.sql
```

### Scaling

Upgrade plan in dashboard:
- **Starter**: $7/month, 512MB RAM, 0.5 CPU
- **Standard**: $25/month, 2GB RAM, 1 CPU
- **Pro**: $85/month, 4GB RAM, 2 CPU

## Troubleshooting

### Issue: Build Fails

**Check:**
- `requirements.txt` has all dependencies
- Python version compatibility
- Build logs for specific errors

### Issue: Database Connection Errors

**Check:**
- `DATABASE_URL` is set correctly
- Use **Internal Database URL** (not External)
- Database is running and accessible

### Issue: Application Won't Start

**Check:**
- Start command is correct: `gunicorn app:app`
- Port binding uses `$PORT` environment variable
- Health check endpoint returns 200

### Issue: Static Files Not Loading

**Check:**
- `static/` and `templates/` directories are in repository
- File paths are correct (case-sensitive)
- Verify in Render dashboard: **Shell** → `ls -la static/`

## Advanced: Render Blueprint (Infrastructure as Code)

Create `render.yaml` for automated deployment:

```yaml
services:
  - type: web
    name: ckkc-expedition-web
    runtime: python3
    plan: starter
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
    healthCheckPath: /health
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: ckkc-expedition-db
          property: connectionString

databases:
  - name: ckkc-expedition-db
    plan: starter
    databaseName: expedition_db
    user: ckkc_user
```

Deploy with:
```bash
render blueprint launch
```

## Migration from Docker to Render

If you have data in Docker deployment:

1. Export database:
```bash
docker-compose exec db pg_dump -U ckkc_user expedition_db > backup.sql
```

2. Import to Render:
```bash
psql [RENDER_DATABASE_URL] < backup.sql
```

## Comparison with Docker Deployment

| Feature | Docker Compose | Render.com |
|---------|----------------|------------|
| Setup Complexity | Medium | Easy |
| Cost | Self-hosted (VPS cost) | $0-14/month |
| Maintenance | Manual updates | Automatic |
| Scaling | Manual | One-click |
| SSL/HTTPS | Manual (nginx) | Automatic |
| Backups | Manual | Automatic (paid) |
| Monitoring | Self-setup | Built-in |

## Support

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

---

**Ready to deploy?** Follow the steps above or use the Render Blueprint for automated deployment.
