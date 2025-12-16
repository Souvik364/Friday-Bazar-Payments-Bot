# 🚀 Complete Setup & Deployment Guide

## 📦 Project Overview

**Telegram Premium Plan Sales Bot** - A production-ready, async bot for selling premium subscriptions with automated payment verification.

### ✨ Key Features
- 💎 Two premium plans (1 Month ₹20, 3 Months ₹55)
- 📱 QR code payment display
- ⏰ 5-minute non-blocking timer
- 📸 Screenshot upload system
- 👨‍💼 Admin approval workflow
- 🚀 Fully async (fast & responsive)
- 🛡️ Secure & robust

---

## 📋 Prerequisites

- ✅ Python 3.10.11 installed
- ✅ Telegram account
- ✅ Internet connection
- ✅ Basic command line knowledge

---

## 🔧 Installation Steps

### Step 1: Verify Python Version
```bash
python --version
```
Should show: `Python 3.10.11` (or 3.10+)

### Step 2: Navigate to Project
```bash
cd telegram-premium-bot
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Installing aiogram...
Installing python-dotenv...
Installing qrcode...
Installing Pillow...
Successfully installed!
```

### Step 4: Verify Installation
```bash
python verify_setup.py
```

This checks:
- ✅ Python version
- ✅ Dependencies installed
- ✅ File structure complete
- ✅ Configuration ready

---

## 🔑 Configuration

### Get Bot Token from BotFather

1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Enter bot name: `My Premium Bot`
5. Enter username: `mypremium_bot` (must end with 'bot')
6. Copy the token (looks like: `123456789:ABCdefGHI...`)

### Get Your Admin ID

1. Open Telegram
2. Search: `@userinfobot`
3. Send: `/start`
4. Copy your User ID (e.g., `123456789`)

### Create .env File

**Windows:**
```bash
copy .env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

**Edit .env file:**
```env
BOT_TOKEN=paste_your_bot_token_here
ADMIN_ID=paste_your_user_id_here
```

**Example:**
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=987654321
```

⚠️ **Important**: 
- No quotes around values
- ADMIN_ID must be a number
- Don't share your .env file

---

## ▶️ Running the Bot

### Start Bot
```bash
python bot.py
```

### Expected Output
```
INFO - Bot started
```

### Keep Bot Running
- Bot must stay running to process messages
- Don't close the terminal
- Press `Ctrl+C` to stop

---

## 🧪 Testing the Bot

### User Testing Checklist

**1. Start Bot**
- Open your bot in Telegram
- Send: `/start`
- ✅ Should see welcome message with "💎 Premium Plan" button

**2. Select Plan**
- Click: "💎 Premium Plan"
- ✅ Should see two plan options (1 Month, 3 Months)

**3. View Payment**
- Click: "1 Month - ₹20"
- ✅ Should see QR code image
- ✅ Should see timer notification

**4. Wait for Timer**
- Wait 5 minutes (or modify timer for testing)
- ✅ Should receive prompt: "If you paid then share a payment screenshot..."

**5. Upload Screenshot**
- Send any photo as screenshot
- ✅ Should see confirmation: "Your payment screenshot has been submitted..."

### Admin Testing Checklist

**1. Receive Notification**
- Check admin account (your Telegram)
- ✅ Should receive message with:
  - User details (ID, username, name)
  - Plan details (type, amount)
  - Screenshot image
  - Approve/Reject buttons

**2. Approve Payment**
- Click: "✅ Approve"
- ✅ User receives approval message
- ✅ Admin message updates to show "APPROVED"

**3. Reject Payment**
- Test with another payment
- Click: "❌ Reject"
- ✅ User receives rejection message
- ✅ Admin message updates to show "REJECTED"

---

## ⚙️ Customization

### Change Timer Duration (for testing)

Edit `handlers/premium.py`, line ~96:

```python
# Change from 300 seconds (5 min) to 30 seconds
start_payment_timer(bot, callback.message.chat.id, state, duration=30)
```

### Change to Real Payment QR

Edit `utils/qr_generator.py`, line ~25:

```python
# Replace test data
qr_data = f"TEST_PAYMENT|Plan:{plan_name}|Amount:{amount}"

# With real UPI payment
qr_data = f"upi://pay?pa=yourUPI@bank&pn=YourName&am={amount}&cu=INR&tn=Plan:{plan_name}"
```

### Change Plan Prices

Edit `handlers/premium.py`:

**1. Update buttons (line ~22):**
```python
[InlineKeyboardButton(text="1 Month - ₹50", callback_data="plan_1month_50")],
[InlineKeyboardButton(text="3 Months - ₹120", callback_data="plan_3months_120")]
```

**2. Update handler (line ~67):**
```python
if callback_data == "plan_1month_50":
    plan_name = "1 Month"
    amount = 50
elif callback_data == "plan_3months_120":
    plan_name = "3 Months"
    amount = 120
```

### Add More Plans

**1. Add button in `get_plan_selection_keyboard()`:**
```python
[InlineKeyboardButton(text="6 Months - ₹100", callback_data="plan_6months_100")]
```

**2. Add handler in `process_plan_selection()`:**
```python
elif callback_data == "plan_6months_100":
    plan_name = "6 Months"
    amount = 100
```

---

## 🐛 Troubleshooting

### Bot Doesn't Start

**Error**: `BOT_TOKEN is not set`
```
Solution: Check .env file exists and contains BOT_TOKEN
```

**Error**: `ADMIN_ID must be a valid integer`
```
Solution: Remove quotes from ADMIN_ID in .env
Correct: ADMIN_ID=123456789
Wrong: ADMIN_ID="123456789"
```

**Error**: `No module named 'aiogram'`
```
Solution: Install dependencies
Command: pip install -r requirements.txt
```

### Bot Not Responding

**Check 1**: Is bot running?
```
Look for "INFO - Bot started" in terminal
If not, start with: python bot.py
```

**Check 2**: Is token correct?
```
Verify BOT_TOKEN in .env matches token from BotFather
No extra spaces or quotes
```

**Check 3**: Internet connection
```
Check if you can access telegram.org
```

### Admin Not Receiving Messages

**Issue**: Admin doesn't get notifications

**Solution 1**: Start the bot
```
Admin must send /start to bot first
Bot can't message users who haven't started it
```

**Solution 2**: Check ADMIN_ID
```
Use @userinfobot to verify your correct User ID
Update ADMIN_ID in .env
Restart bot (Ctrl+C then python bot.py)
```

**Solution 3**: Unblock bot
```
Check if you blocked the bot
Unblock: Settings → Privacy → Blocked Users
```

### Timer Not Working

**Issue**: Timer doesn't complete

**Check terminal for errors:**
```
Look for error messages in console
Timer runs asynchronously in background
```

**Verify state:**
```
Don't click other buttons during timer
User must stay in "timer_running" state
```

### QR Code Not Showing

**Error**: `No module named 'qrcode'`
```
Solution: pip install qrcode Pillow
```

**Error**: Image sending failed
```
Check internet connection
Verify bot has permission to send photos
```

---

## 🔒 Security Best Practices

### Protect Credentials
- ✅ Never commit `.env` file to git
- ✅ Don't share bot token publicly
- ✅ Keep admin ID private
- ✅ Use `.gitignore` (already included)

### Admin Access
- ✅ Only authorized users should know bot username
- ✅ Verify ADMIN_ID is correct
- ✅ Don't share admin credentials

### Code Security
- ✅ Review code before running
- ✅ Don't modify security checks
- ✅ Keep dependencies updated

---

## 📊 Monitoring

### View Logs

**In Terminal:**
```
Watch for:
- User interactions
- Plan selections
- Timer completions
- Admin actions
- Errors
```

**Log Levels:**
- `INFO`: Normal operations
- `ERROR`: Something failed
- `WARNING`: Potential issues

### Common Log Messages

**Normal:**
```
INFO - Bot started
INFO - User 123456789 selected plan: 1 Month (₹20)
INFO - Timer completed for user 123456789
INFO - Payment screenshot from user 123456789 forwarded to admin
INFO - Admin approved payment for user 123456789
```

**Errors:**
```
ERROR - Failed to notify admin: [details]
ERROR - Unhandled error: [details]
```

---

## 🚀 Production Deployment

### Option 1: Keep Running Locally
```bash
# Simple but requires computer always on
python bot.py
```

### Option 2: Run in Background (Linux/Mac)
```bash
nohup python bot.py > bot.log 2>&1 &
```

### Option 3: Use Screen (Linux)
```bash
screen -S telegram-bot
python bot.py
# Press Ctrl+A then D to detach
# Reattach: screen -r telegram-bot
```

### Option 4: Systemd Service (Linux)

Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Premium Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-premium-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot
```

### Option 5: Cloud Hosting
- **Heroku**: Deploy with Procfile
- **PythonAnywhere**: Use always-on task
- **AWS EC2**: Run on virtual server
- **DigitalOcean**: Deploy on droplet
- **Railway**: Easy deployment

---

## 📈 Usage Statistics

Track manually or add database:
- Number of users
- Plans purchased
- Revenue generated
- Approval/rejection rates

---

## 🎯 Success Checklist

Before going live:

- [ ] Python 3.10+ installed
- [ ] All dependencies installed
- [ ] .env file configured
- [ ] Bot token from BotFather
- [ ] Admin ID verified
- [ ] Bot starts without errors
- [ ] /start command works
- [ ] Premium plan buttons work
- [ ] QR code displays
- [ ] Timer completes
- [ ] Screenshot upload works
- [ ] Admin receives notifications
- [ ] Approve/reject works
- [ ] QR code changed to real payment (if needed)
- [ ] Plan prices correct
- [ ] Timer duration appropriate
- [ ] Tested complete flow
- [ ] Reviewed all settings

---

## 📚 Additional Resources

### Documentation
- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick setup guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `.env.example` - Configuration template

### Scripts
- `verify_setup.py` - Setup verification
- `bot.py` - Main bot file

### Support
- Check terminal logs for errors
- Review troubleshooting section
- Test with verify_setup.py

---

## 🎉 You're Ready!

Your Telegram Premium Bot is now set up and ready to sell premium plans!

**Next Steps:**
1. ✅ Complete setup checklist
2. ✅ Test complete flow
3. ✅ Replace fake QR with real payment
4. ✅ Deploy to production
5. ✅ Start selling premium plans!

**Need Help?**
- Review documentation files
- Check logs in terminal
- Run verify_setup.py

---

**Built with ❤️ using Python 3.10.11 and aiogram 3.x**  
**Fast • Smooth • Responsive • Production-Ready**
