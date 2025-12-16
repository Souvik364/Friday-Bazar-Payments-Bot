# Quick Start Guide

## Setup in 5 Minutes

### Step 1: Install Dependencies
```bash
cd telegram-premium-bot
pip install -r requirements.txt
```

### Step 2: Get Bot Token
1. Open Telegram
2. Search for @BotFather
3. Send: `/newbot`
4. Follow instructions
5. Copy the token

### Step 3: Get Your Admin ID
1. Open Telegram
2. Search for @userinfobot
3. Send: `/start`
4. Copy your ID number

### Step 4: Configure Bot
Create `.env` file:
```
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
```

### Step 5: Run Bot
```bash
python bot.py
```

### Step 6: Test Bot
1. Open your bot in Telegram
2. Send: `/start`
3. Click: "💎 Premium Plan"
4. Select a plan
5. View QR code
6. Wait 5 minutes
7. Upload fake payment screenshot
8. Check admin account for notification
9. Approve/Reject as admin

## Bot Flow

```
User Journey:
/start → Premium Plan → Select Plan → QR Code → Timer (5 min) → Upload Screenshot → Wait for Admin

Admin Journey:
Receive Notification → Review Screenshot → Approve/Reject → User Notified
```

## Common Commands

**For testing timer (modify duration):**
Edit `handlers/premium.py` line with `duration=300` to `duration=30` (30 seconds)

**Change prices:**
Edit `handlers/premium.py` in `get_plan_selection_keyboard()` function

**Change QR to real payment:**
Edit `utils/qr_generator.py` in `generate_payment_qr()` function

## Troubleshooting

**Bot doesn't start:**
- Check `.env` file exists
- Verify BOT_TOKEN is correct
- Ensure Python 3.10.11 is installed

**Admin not receiving messages:**
- Verify ADMIN_ID is correct (number only, no quotes)
- Send `/start` to bot from admin account first
- Check admin didn't block the bot

**Timer not working:**
- Check terminal for errors
- Ensure async operations are not blocked
- Verify bot.py is running

## Test Checklist

- [ ] Bot starts without errors
- [ ] /start command shows welcome message
- [ ] "Premium Plan" button appears
- [ ] Clicking button shows 2 plan options
- [ ] Selecting plan shows QR code
- [ ] Timer message appears
- [ ] After 5 minutes, prompt for screenshot appears
- [ ] Uploading photo sends confirmation
- [ ] Admin receives notification with photo
- [ ] Admin can approve/reject
- [ ] User receives approval/rejection message

## Need Help?

Check `README.md` for detailed documentation!
