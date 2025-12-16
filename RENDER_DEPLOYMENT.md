# 🚀 Deploy to Render for 24/7 Hosting (FREE)

## Overview

**Render** is a cloud platform that offers FREE hosting for web services and background workers. Perfect for running your Telegram bot 24/7 without keeping your computer on!

### ✨ Why Render?

- ✅ **FREE Tier** - No credit card required
- ✅ **24/7 Uptime** - Bot runs continuously
- ✅ **Auto-Deploy** - Push to GitHub, auto-deploys
- ✅ **Environment Variables** - Secure config management
- ✅ **Logs** - Real-time monitoring
- ✅ **Easy Setup** - 5-10 minutes deployment

---

## 📋 Prerequisites

1. ✅ **GitHub Account** - To store your code
2. ✅ **Render Account** - Sign up at [render.com](https://render.com)
3. ✅ **Bot Token** - From @BotFather
4. ✅ **Admin ID** - Your Telegram user ID

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Project for Render

#### 1.1 Create `render.yaml`

Create a file named `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: telegram-premium-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: ADMIN_ID
        sync: false
```

#### 1.2 Update `requirements.txt`

Make sure your `requirements.txt` includes all dependencies:

```
aiogram>=3.0.0
python-dotenv>=1.0.0
qrcode>=7.4.2
Pillow>=10.0.0
```

#### 1.3 Create `runtime.txt` (Optional)

Specify Python version:

```
python-3.10.11
```

#### 1.4 Update `bot.py` (Add Port Binding)

Render's free tier requires a web service. Add this code to your `bot.py`:

```python
import os
from aiohttp import web

# Add this before main() function
async def health_check(request):
    """Health check endpoint for Render."""
    return web.Response(text="Bot is running!")

async def start_web_server():
    """Start a simple web server for Render's health checks."""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")

# Modify your main() function:
async def main():
    dp.include_router(start_router)
    dp.include_router(premium_router)
    dp.include_router(admin_router)
    
    logger.info("Bot started")
    
    # Start web server for Render
    await start_web_server()
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
```

---

### Step 2: Push to GitHub

#### 2.1 Initialize Git Repository

```bash
cd telegram-premium-bot
git init
git add .
git commit -m "Initial commit - Telegram premium bot"
```

#### 2.2 Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name: `telegram-premium-bot`
3. Make it **Private** (recommended for security)
4. Click "Create repository"

#### 2.3 Push Code to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-premium-bot.git
git branch -M main
git push -u origin main
```

⚠️ **Important**: Make sure `.env` file is in `.gitignore` (already done)

---

### Step 3: Deploy on Render

#### 3.1 Sign Up / Log In

1. Go to [render.com](https://render.com)
2. Sign up using GitHub account (easiest)
3. Authorize Render to access your repositories

#### 3.2 Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Click **"Next"**

#### 3.3 Connect GitHub Repository

1. Find your repository: `telegram-premium-bot`
2. Click **"Connect"**

#### 3.4 Configure Service

**Basic Settings:**
- **Name**: `telegram-premium-bot` (or any name)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`

**Plan:**
- Select **"Free"** plan

#### 3.5 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add two variables:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Your bot token from BotFather |
| `ADMIN_ID` | Your Telegram user ID |

**Example:**
```
BOT_TOKEN = 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID = 987654321
```

#### 3.6 Deploy!

1. Click **"Create Web Service"**
2. Wait 2-5 minutes for deployment
3. Watch the logs for "Bot started" message

---

### Step 4: Verify Deployment

#### 4.1 Check Logs

In Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Look for:
   ```
   INFO - Bot started
   INFO - Web server started on port 10000
   ```

#### 4.2 Test Bot

1. Open your bot in Telegram
2. Send `/start`
3. Check if bot responds

✅ **Success!** Your bot is now running 24/7 on Render!

---

## 🔄 Auto-Deploy Setup

Every time you push to GitHub, Render will automatically redeploy:

```bash
# Make changes to your code
git add .
git commit -m "Update bot features"
git push origin main
# Render automatically deploys!
```

---

## ⚙️ Render Configuration Options

### Keep Bot Always Running

Render's free tier may sleep after 15 minutes of inactivity. To prevent this:

**Option 1: Use Cron-Job.org** (Free)
1. Go to [cron-job.org](https://cron-job.org)
2. Create account
3. Add new cron job
4. URL: `https://your-bot-name.onrender.com/health`
5. Schedule: Every 10 minutes
6. This pings your bot to keep it awake

**Option 2: Upgrade to Paid Plan** ($7/month)
- Paid plans never sleep
- Better for production

---

## 📊 Monitoring Your Bot

### View Logs in Real-Time

1. Go to Render dashboard
2. Select your service
3. Click **"Logs"**
4. See all bot activity

### Check Bot Status

Visit: `https://your-bot-name.onrender.com/health`

Should show: `Bot is running!`

---

## 🔧 Troubleshooting

### Bot Not Starting

**Check Logs for:**

1. **Missing Environment Variables**
   ```
   Error: BOT_TOKEN is not set
   ```
   **Fix**: Add BOT_TOKEN in Render dashboard → Environment

2. **Invalid Token**
   ```
   Error: Unauthorized
   ```
   **Fix**: Get new token from @BotFather

3. **Port Binding Error**
   ```
   Error: Port already in use
   ```
   **Fix**: Make sure you added web server code to bot.py

### Bot Responds Slowly

**Reason**: Free tier has limited resources

**Solutions**:
- Optimize code
- Upgrade to paid plan
- Use webhook instead of polling (advanced)

### Bot Goes Offline

**Reason**: Free tier sleeps after 15 min inactivity

**Solution**: Use Cron-Job.org to ping every 10 min

---

## 💡 Optimization Tips

### 1. Use Webhooks (Advanced)

Instead of polling, use webhooks for faster response:

```python
# In bot.py, replace polling with webhook
async def main():
    # ... setup code ...
    
    # Webhook instead of polling
    await bot.set_webhook(f"https://your-bot.onrender.com/webhook")
    
    # Setup webhook handler
    app = web.Application()
    app.router.add_post('/webhook', webhook_handler)
    # ... rest of code
```

### 2. Reduce Logging

Less logging = faster performance:

```python
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Optimize Animations

Reduce sleep times in production:

```python
await asyncio.sleep(0.1)  # Instead of 0.5
```

---

## 🔒 Security Best Practices

### 1. Keep Repository Private

Your repo should be **private** on GitHub to protect:
- Bot logic
- Admin commands
- Internal configurations

### 2. Never Commit Secrets

✅ **Good**: Use environment variables
```python
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

❌ **Bad**: Hardcode secrets
```python
BOT_TOKEN = "123456:ABC..."  # Never do this!
```

### 3. Rotate Tokens Periodically

Every few months:
1. Generate new token from @BotFather
2. Update in Render environment variables
3. Redeploy

---

## 📈 Scaling to Production

### When to Upgrade?

Upgrade to paid plan if:
- ✅ More than 1000 users
- ✅ Need 100% uptime
- ✅ Faster response times
- ✅ More memory/CPU

### Render Paid Plans

| Plan | Price | Features |
|------|-------|----------|
| **Starter** | $7/month | Never sleeps, More resources |
| **Pro** | $25/month | Dedicated resources, Priority support |

---

## 🎯 Deployment Checklist

Before deploying to Render:

- [ ] Code tested locally
- [ ] `.env` in `.gitignore`
- [ ] `render.yaml` created
- [ ] Web server code added to bot.py
- [ ] GitHub repository created (private)
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Service configured on Render
- [ ] Environment variables added
- [ ] Bot deployed successfully
- [ ] Bot responds in Telegram
- [ ] Logs show "Bot started"
- [ ] Health check endpoint works
- [ ] Cron job configured (optional)

---

## 🆘 Getting Help

### Render Support

- **Docs**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Support**: support@render.com

### Common Issues

1. **"Service unavailable"**
   - Wait 2-3 minutes after deployment
   - Check logs for errors

2. **"Build failed"**
   - Check requirements.txt
   - Verify Python version

3. **"Bot not responding"**
   - Check environment variables
   - Verify bot token

---

## 🔄 Alternative Hosting Options

If Render doesn't work for you:

### Free Options:
1. **Railway** - [railway.app](https://railway.app)
2. **Fly.io** - [fly.io](https://fly.io)
3. **Heroku** - [heroku.com](https://heroku.com) (No longer free)
4. **PythonAnywhere** - [pythonanywhere.com](https://pythonanywhere.com)

### Paid Options:
1. **DigitalOcean** - $5/month droplet
2. **AWS EC2** - From $3/month
3. **Google Cloud** - Free tier available
4. **Azure** - Student free credits

---

## ✅ Success!

Your bot is now running 24/7 on Render! 🎉

**What's Next?**
- Monitor logs regularly
- Setup Cron-Job to prevent sleeping
- Collect user feedback
- Add more features
- Scale when needed

---

**Deployment Time**: 5-10 minutes  
**Cost**: FREE  
**Uptime**: 24/7 (with Cron-Job)  
**Maintenance**: Automatic updates via Git push

🚀 **Happy Hosting!**
