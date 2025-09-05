# 🌐 Cloud Deployment Guide

## Quick Start - Railway (Recommended)

### Step 1: Prepare Your Code
```bash
# Run this script first
python deploy_cloud.py
```

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect and deploy your Flask app

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:
```
DATABASE_TYPE=postgresql
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### Step 4: Add Database
1. In Railway, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically set DATABASE_URL
3. Your app will restart and migrate data automatically

---

## Alternative: Render Deployment

### Step 1: Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python enhanced_app.py`
   - **Environment**: `Python 3`

### Step 3: Add Database
1. Create "PostgreSQL" service in Render
2. Copy the database URL
3. Add environment variables in your web service:
   ```
   DATABASE_URL=your-postgresql-url
   DATABASE_TYPE=postgresql
   FLASK_ENV=production
   ```

---

## Alternative: Heroku Deployment

### Step 1: Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Login
heroku login
```

### Step 2: Create Heroku App
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
```

### Step 3: Deploy
```bash
git push heroku main
```

---

## 🔐 Security Configuration

### Environment Variables (Required)
```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Add these to your cloud platform:
```
SECRET_KEY=your-generated-secret-key
FLASK_ENV=production
DATABASE_TYPE=postgresql
```

### Optional Configuration
```
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

---

## 📱 Access Your Deployed App

Once deployed, your app will be available at:
- **Railway**: `https://your-app-name.up.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **Heroku**: `https://your-app-name.herokuapp.com`

### Share with Residents
1. Share the URL with all residents
2. They can access from any device with internet
3. No network restrictions - works from anywhere
4. Mobile-friendly interface

---

## 🔧 Troubleshooting

### Common Issues

**App won't start:**
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure requirements.txt is complete

**Database connection failed:**
- Verify DATABASE_URL is set correctly
- Check if database service is running
- Ensure DATABASE_TYPE matches your database

**502/503 Errors:**
- App might be starting up (wait 1-2 minutes)
- Check if port configuration is correct
- Verify start command is `python enhanced_app.py`

### Getting Help
- Railway: Check deployment logs in dashboard
- Render: View logs in service dashboard
- Heroku: Use `heroku logs --tail`

---

## 💰 Cost Breakdown

### Railway (Recommended)
- **Free Tier**: $5 credit monthly (enough for small apartments)
- **Pro**: $20/month for unlimited usage
- **Database**: Included in free tier

### Render
- **Free Tier**: Limited hours, sleeps after inactivity
- **Starter**: $7/month for always-on service
- **Database**: $7/month for PostgreSQL

### Heroku
- **Free Tier**: Discontinued
- **Basic**: $7/month + $9/month for database

**Recommendation**: Railway offers the best value with generous free tier.