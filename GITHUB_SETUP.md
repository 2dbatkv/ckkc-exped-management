# GitHub Setup & Cloud Deployment Guide

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `ckkc-expedition-web`
   - **Description**: `CKKC Expedition Management System - PostgreSQL Web Deployment`
   - **Visibility**: Choose Private or Public
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click **Create repository**
4. Copy the repository URL (will look like: `https://github.com/YOUR_USERNAME/ckkc-expedition-web.git`)

### Option B: Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Create repository
gh repo create ckkc-expedition-web --private --description "CKKC Expedition Management System - PostgreSQL Web Deployment"

# The CLI will give you the repository URL
```

## Step 2: Push Code to GitHub

From the `/home/ajbir/ckkc-web-deployment` directory:

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ckkc-expedition-web.git

# Verify remote was added
git remote -v

# Push code to GitHub
git push -u origin main
```

If you get a password prompt, you'll need to use a Personal Access Token (not your password):
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (all)
4. Copy the token
5. Use the token as your password when prompted

## Step 3: Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/ckkc-expedition-web`
2. Verify you see all files:
   - ✓ app.py
   - ✓ templates/ folder
   - ✓ static/ folder
   - ✓ requirements.txt
   - ✓ Dockerfile
   - ✓ docker-compose.yml
   - ✓ render.yaml
   - ✓ README.md
   - ✗ .env (should NOT be visible - it's gitignored)

## Step 4: Deploy to Render.com

### Quick Deploy with Render Blueprint

1. Go to https://dashboard.render.com
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create:
   - PostgreSQL database
   - Web service
   - Automatically configure environment variables

### Manual Deploy (Alternative)

Follow the detailed instructions in `RENDER_DEPLOYMENT.md`

## Step 5: Initialize Database

After deployment, the database schema needs to be initialized:

### Option A: Via Render Dashboard Shell

1. Go to your PostgreSQL service in Render
2. Click **Shell** tab
3. Run:
```sql
-- Copy and paste the contents of init_db.sql
-- Or upload the file and run:
\i init_db.sql
```

### Option B: Via psql from Local Machine

```bash
# Get the External Database URL from Render dashboard
# It will look like: postgresql://user:pass@host/dbname

# Run initialization
psql "postgresql://user:pass@host/dbname" < init_db.sql
```

### Option C: Via Render CLI

```bash
# Install Render CLI
npm install -g @render-com/cli

# Login
render login

# Find your database service
render services list

# Connect and initialize
render shell ckkc-expedition-db
\i init_db.sql
```

## Step 6: Configure Environment Variables

In Render dashboard, go to your Web Service → Environment tab:

**Required Variables:**
| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | Auto-set by Render | From PostgreSQL service |
| `FLASK_SECRET_KEY` | Generate new | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSCODE` | Your choice | Change from default "expedition2025" |
| `FLASK_ENV` | `production` | |

**Optional Variables:**
| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | 10000 | Render sets this automatically |

## Step 7: Verify Deployment

Once deployed (usually takes 3-5 minutes):

1. **Health Check**: Visit `https://your-app.onrender.com/health`
   - Should return: `{"status": "healthy", "database": "healthy"}`

2. **Main App**: Visit `https://your-app.onrender.com/`
   - Should see the CKKC Expedition Dashboard

3. **Admin**: Visit `https://your-app.onrender.com/admin`
   - Use your ADMIN_PASSCODE to login

4. **Test Registration**: Try registering a test participant

## Step 8: Set Up Custom Domain (Optional)

### In Render:
1. Go to your Web Service → Settings
2. Scroll to **Custom Domain**
3. Add domain: `expedition.yourdomain.com`
4. Render provides DNS instructions

### In Your DNS Provider:
1. Add CNAME record:
   - Name: `expedition`
   - Value: `your-app.onrender.com`
2. Wait for DNS propagation (5-60 minutes)
3. Render automatically provisions SSL certificate

## Deployment Options Comparison

| Platform | Setup | Cost | Auto-Deploy | Database |
|----------|-------|------|-------------|----------|
| **Render.com** | Easy | $0-14/mo | ✓ | Managed PostgreSQL |
| **Heroku** | Easy | $0-16/mo | ✓ | Managed PostgreSQL |
| **Railway.app** | Easy | Pay-as-go | ✓ | Managed PostgreSQL |
| **Docker on VPS** | Medium | VPS cost | Manual | Self-hosted |
| **Docker Compose** | Medium | VPS cost | Manual | Self-hosted |

## Continuous Deployment

Once connected to GitHub, Render automatically deploys when you push to main:

```bash
# Make changes to code
git add .
git commit -m "Update feature X"
git push

# Render automatically detects the push and deploys
# Monitor deployment in Render dashboard
```

## Troubleshooting

### Push Failed: Authentication

**Problem**: `fatal: Authentication failed`

**Solution**: Use Personal Access Token instead of password
1. Create token at https://github.com/settings/tokens
2. Use token as password when prompted

### Push Failed: Large Files

**Problem**: `remote: error: File too large`

**Solution**:
```bash
# Check for large files
find . -size +50M

# Add large files to .gitignore
echo "large-file.ext" >> .gitignore

# Remove from git cache
git rm --cached large-file.ext
git commit -m "Remove large file"
git push
```

### Render Build Failed

**Problem**: Build fails with dependency errors

**Solution**:
- Check `requirements.txt` for correct versions
- Verify Python version in `runtime.txt` matches available versions
- Check build logs in Render dashboard

### Database Connection Failed

**Problem**: App can't connect to database

**Solution**:
- Verify `DATABASE_URL` is set correctly
- Use **Internal Database URL** (not External) in Render
- Check database service is running
- Verify database is initialized (run init_db.sql)

### Health Check Failing

**Problem**: Render shows health check failures

**Solution**:
```bash
# Test health endpoint locally
curl https://your-app.onrender.com/health

# Check logs
render logs ckkc-expedition-web

# Common issues:
# - Database not initialized
# - DATABASE_URL incorrect
# - App crashed during startup
```

## Security Checklist Before Going Live

- [ ] Changed `ADMIN_PASSCODE` from default
- [ ] Generated secure `FLASK_SECRET_KEY`
- [ ] Set repository to Private (if it contains sensitive info)
- [ ] `.env` is in `.gitignore` (verify it's not in GitHub)
- [ ] Database password is strong
- [ ] Tested all functionality
- [ ] Set up automated backups (Render Starter plan or higher)
- [ ] Configured custom domain with HTTPS
- [ ] Reviewed admin access controls

## Next Steps

1. Test all features thoroughly
2. Add real expedition data
3. Train users on the system
4. Set up monitoring and alerts
5. Configure automated backups
6. Plan for scaling if needed

## Support Resources

- **Render Docs**: https://render.com/docs
- **GitHub Docs**: https://docs.github.com
- **This Project README**: See README.md for full documentation

---

**Ready to deploy?** Follow the steps above in order.

**Current Status:**
- ✓ Code converted to PostgreSQL
- ✓ Git repository initialized
- ✓ Local commit created
- ⏳ Waiting for GitHub push
- ⏳ Waiting for cloud deployment
