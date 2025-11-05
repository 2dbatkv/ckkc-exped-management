# Render Deployment Instructions for CKKC Expedition Management

## Your Deployment Details

- **Render Web Service**: https://ckkc-exped-management.onrender.com/
- **PostgreSQL Database**: `postgresql://ckkc_expedition_user:naC6cVFNQBxSfGNIDXNVd8WiLFbJWtSZ@dpg-d455ueili9vc73cgu69g-a/ckkc_expedition`
- **GitHub Repository**: https://github.com/2dbatkv/ckkc-exped-management
- **Branch**: main

## Important: Netlify Not Needed

The new unified Flask application serves both frontend and backend together. You can:
1. **Keep Netlify** - Set it to redirect all traffic to Render (optional)
2. **Remove Netlify** - Access the app directly via Render URL

---

## Step 1: Update Render Web Service Configuration

Go to: https://dashboard.render.com/web/srv-YOUR_SERVICE_ID/settings

### Build & Deploy Settings

**Build Command:**
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application
```

**Health Check Path:**
```
/health
```

### Auto-Deploy

- ✅ Enable "Auto-Deploy" for branch: `main`

---

## Step 2: Configure Environment Variables

Go to: Environment tab in your Render service

**Required Variables:**

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://ckkc_expedition_user:naC6cVFNQBxSfGNIDXNVd8WiLFbJWtSZ@dpg-d455ueili9vc73cgu69g-a.oregon-postgres.render.com/ckkc_expedition` |
| `FLASK_SECRET_KEY` | Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSCODE` | `expedition2025` (change to something secure!) |
| `FLASK_ENV` | `production` |

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and paste as FLASK_SECRET_KEY
```

---

## Step 3: Initialize PostgreSQL Database

### Option A: Via Render Dashboard Shell

1. Go to your PostgreSQL database in Render dashboard
2. Click **"Shell"** tab
3. You'll be connected to psql

4. Copy the entire content from `init_db.sql` and paste into the shell

**OR** run section by section:

```sql
-- Create participants table
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    -- ... (rest of the schema from init_db.sql)
);

-- Continue with all other tables...
```

### Option B: Via Local psql Command

From your local machine:

```bash
# Make sure you're in the project directory
cd /home/ajbir/ckkc-web-deployment

# Connect and initialize (use External connection string)
psql "postgresql://ckkc_expedition_user:naC6cVFNQBxSfGNIDXNVd8WiLFbJWtSZ@dpg-d455ueili9vc73cgu69g-a.oregon-postgres.render.com/ckkc_expedition" < init_db.sql
```

**Note:** You may need to use the **External** database URL (with `.oregon-postgres.render.com`) for connections from outside Render.

### Option C: Via Render CLI

```bash
# Install Render CLI
npm install -g @render-com/cli

# Login
render login

# Connect to database shell
render shell [YOUR_POSTGRES_SERVICE_NAME]

# Then paste init_db.sql content
```

---

## Step 4: Deploy the Application

### If Auto-Deploy is Enabled:

Your service should already be deploying! Check the "Events" tab in Render dashboard.

### If Manual Deploy:

1. Go to your web service in Render
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Monitor deployment in "Events" tab

---

## Step 5: Verify Deployment

### Health Check
```bash
curl https://ckkc-exped-management.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2025-11-04T20:15:00.000000"
}
```

### Main Application
Visit: https://ckkc-exped-management.onrender.com/

You should see the CKKC Expedition Dashboard

### Test Registration
1. Visit: https://ckkc-exped-management.onrender.com/register
2. Fill out the form
3. Submit
4. Check participants list: https://ckkc-exped-management.onrender.com/participants

### Test Admin Access
1. Visit: https://ckkc-exped-management.onrender.com/admin
2. Enter your ADMIN_PASSCODE
3. Verify you can access the admin dashboard

---

## Step 6: Netlify Options

### Option 1: Keep Netlify as a Domain Proxy (Optional)

If you want to keep using https://ckkc.netlify.app/ as your main URL:

1. Delete all existing files in your Netlify site
2. Create a single `_redirects` file with:
```
/* https://ckkc-exped-management.onrender.com/:splat 200!
```

This redirects ALL traffic to your Render deployment.

### Option 2: Remove Netlify (Recommended)

Since the app is fully served by Render now:

1. Go to Netlify dashboard
2. Delete the site or unpublish it
3. Use Render URL directly: https://ckkc-exped-management.onrender.com/

### Option 3: Set Up Custom Domain on Render

1. Go to your Render web service → Settings
2. Scroll to **Custom Domain**
3. Add: `ckkc.yourdomain.com` (or buy a domain)
4. Update DNS as instructed
5. Render auto-provisions SSL certificate

---

## Troubleshooting

### Issue: Deployment Fails

**Check Build Logs:**
1. Go to Render service → Events
2. Click on the failed deployment
3. Check logs for errors

**Common Fixes:**
- Verify `requirements.txt` has all dependencies
- Check Python version in `runtime.txt` (should be python-3.12.7)
- Ensure `wsgi.py` exists in repository

### Issue: Health Check Failing

**Check:**
```bash
curl -v https://ckkc-exped-management.onrender.com/health
```

**Common Issues:**
- Database URL incorrect (check environment variable)
- Database not initialized (run init_db.sql)
- Application not starting (check logs)

### Issue: Database Connection Error

**Verify DATABASE_URL:**
1. In Render service → Environment
2. Should be: `postgresql://ckkc_expedition_user:PASSWORD@HOST/ckkc_expedition`
3. Use **Internal** database URL for connections from Render
4. Use **External** database URL for local connections

**Test Database:**
```bash
# From Render shell
psql $DATABASE_URL -c "SELECT 1;"
```

### Issue: Static Files Not Loading

**Check:**
1. Verify `static/` folder exists in GitHub
2. Check browser console for 404 errors
3. Verify Flask is serving static files (should work by default)

### Issue: Templates Not Found

**Check:**
1. Verify `templates/` folder exists in GitHub
2. Check deployment logs for template errors
3. Ensure templates have correct file names (case-sensitive)

---

## Post-Deployment Checklist

- [ ] Health check returns "healthy"
- [ ] Home page loads correctly
- [ ] Registration form works
- [ ] Can submit a test registration
- [ ] Participant list shows registered users
- [ ] Cave survey form loads
- [ ] Admin login works with ADMIN_PASSCODE
- [ ] Admin dashboard displays data
- [ ] Can export data to CSV
- [ ] All CSS/styling loads correctly
- [ ] No console errors in browser
- [ ] Changed ADMIN_PASSCODE from default
- [ ] Generated secure FLASK_SECRET_KEY
- [ ] Database backups configured (Render: upgrade to Starter plan for automated backups)

---

## Monitoring & Maintenance

### View Logs
```bash
# Via Render CLI
render logs ckkc-exped-management

# Or in Render dashboard → Logs tab
```

### Database Backup (Manual)
```bash
# Export database
pg_dump "postgresql://ckkc_expedition_user:PASSWORD@HOST/ckkc_expedition" > backup_$(date +%Y%m%d).sql

# Restore database
psql "postgresql://ckkc_expedition_user:PASSWORD@HOST/ckkc_expedition" < backup_20251104.sql
```

### Database Backup (Automated)
Render Starter plan ($7/mo for database) includes:
- Daily automated backups
- 7-day retention
- Point-in-time recovery

### Update Application
```bash
# Make changes locally
git add .
git commit -m "Update description"
git push origin main

# Render auto-deploys within 1-2 minutes
```

---

## Security Reminders

⚠️ **Before Going Live:**

1. **Change ADMIN_PASSCODE** from default "expedition2025"
2. **Generate new FLASK_SECRET_KEY** (don't use example keys)
3. **Use strong database password** (current password is exposed here - consider rotating)
4. **Enable database backups** (upgrade to Starter plan)
5. **Set up monitoring** (Render includes basic monitoring on paid plans)
6. **Review environment variables** - ensure no secrets in code

---

## Cost Estimate

| Service | Current | Recommended |
|---------|---------|-------------|
| Render Web Service | Free or Starter | Starter ($7/mo) - no cold starts |
| PostgreSQL | Free or Starter | Starter ($7/mo) - includes backups |
| **Total** | **$0-14/mo** | **$14/mo** |

**Free Tier Limitations:**
- Web service spins down after 15 min inactivity (slow first load)
- No automated database backups
- 750 hours/month

---

## Next Steps

1. ✅ Update Render service configuration
2. ✅ Set environment variables
3. ✅ Initialize database with init_db.sql
4. ✅ Deploy and verify
5. ⏳ Test all functionality
6. ⏳ Update security credentials
7. ⏳ Set up monitoring/backups
8. ⏳ Train users
9. ⏳ Go live!

---

**Need Help?**
- Render Docs: https://render.com/docs
- Check deployment logs in Render dashboard
- Review RENDER_DEPLOYMENT.md in repository

**Your App URL:** https://ckkc-exped-management.onrender.com/
