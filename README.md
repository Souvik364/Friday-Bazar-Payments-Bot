# Telegram Premium Plan Sales Bot

A fast, responsive, and feature-rich Telegram bot for selling premium plans with automated payment verification workflow. Built with **aiogram 3.x** and Python 3.10.11 for maximum performance.

## Features

- ✨ **Menu-Driven Interface**: Easy-to-use button-based navigation
- 💳 **Multiple Premium Plans**: Offer 1 Month (₹20) and 3 Months (₹55) plans
- 📱 **QR Code Payment**: Display payment QR codes (easily customizable)
- ⏰ **5-Minute Timer**: Non-blocking countdown for payment completion
- 📸 **Screenshot Upload**: Users submit payment proof
- 👨‍💼 **Admin Approval System**: Approve or reject payments with one click
- 🚀 **Async Architecture**: Lightning-fast responses and smooth operation
- 🔄 **FSM State Management**: Robust flow control with Finite State Machine

## Requirements

- Python 3.10.11
- Telegram Bot Token (from BotFather)
- Admin Telegram User ID

## Installation

### 1. Clone or Download

Download this project to your local machine.

### 2. Install Dependencies

```bash
cd telegram-premium-bot
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
```

#### How to Get Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided
5. Paste it in `.env` as `BOT_TOKEN`

#### How to Get Your Admin ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Start the bot
3. It will reply with your User ID
4. Copy your User ID and paste it in `.env` as `ADMIN_ID`

### 4. Run the Bot

```bash
python bot.py
```

You should see:
```
INFO - Bot started
```

## Usage Guide

### For Users

1. **Start the bot**: Send `/start` command to the bot
2. **View plans**: Click the "💎 Premium Plan" button
3. **Select plan**: Choose between "1 Month - ₹20" or "3 Months - ₹55"
4. **Pay**: Scan the QR code and make payment
5. **Wait**: 5-minute timer will count down
6. **Upload screenshot**: After timer ends, upload payment screenshot
7. **Wait for approval**: Admin will review and approve/reject

### For Admins

1. **Receive notification**: When a user uploads a payment screenshot, you'll receive a notification with:
   - User details (username, ID, name)
   - Plan details (plan type, amount)
   - Payment screenshot
   - Approve/Reject buttons

2. **Review payment**: Check the screenshot

3. **Take action**: 
   - Click "✅ Approve" to activate user's premium plan
   - Click "❌ Reject" to deny the payment

4. **User notification**: User receives instant notification of your decision

## Bot Flow

```
User -> /start
     -> Click "Premium Plan"
     -> Select plan (1 Month or 3 Months)
     -> QR Code displayed
     -> 5-minute timer starts
     -> Timer ends
     -> User uploads payment screenshot
     -> Admin receives notification
     -> Admin approves/rejects
     -> User receives confirmation
```

## Project Structure

```
telegram-premium-bot/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your credentials (create this)
├── handlers/
│   ├── __init__.py       # FSM states definition
│   ├── start.py          # /start command handler
│   ├── premium.py        # Premium plan handlers
│   └── admin.py          # Admin approval handlers
└── utils/
    ├── __init__.py
    ├── qr_generator.py   # QR code generation
    └── timer.py          # Async timer implementation
```

## Customization

### Changing QR Code to Real Payment

The bot currently uses a **fake/test QR code** for demonstration. To use real payment:

1. Open `utils/qr_generator.py`
2. Find the `generate_payment_qr()` function
3. Replace this line:
   ```python
   qr_data = f"TEST_PAYMENT|Plan:{plan_name}|Amount:{amount}"
   ```
   
   With your actual UPI payment string:
   ```python
   qr_data = f"upi://pay?pa=yourUPI@bank&pn=YourName&am={amount}&cu=INR&tn=Premium Plan {plan_name}"
   ```

4. Or integrate with your payment gateway API to generate dynamic QR codes

### Changing Plan Prices

1. Open `handlers/premium.py`
2. Find the `get_plan_selection_keyboard()` function
3. Modify the button text and callback_data:
   ```python
   [InlineKeyboardButton(text="1 Month - ₹50", callback_data="plan_1month_50")],
   ```

4. Update the `process_plan_selection()` function to handle new prices:
   ```python
   if callback_data == "plan_1month_50":
       plan_name = "1 Month"
       amount = 50
   ```

### Changing Timer Duration

1. Open `handlers/premium.py`
2. Find this line in `process_plan_selection()`:
   ```python
   start_payment_timer(bot, callback.message.chat.id, state, duration=300)
   ```

3. Change `duration=300` (5 minutes) to your desired seconds:
   - 3 minutes: `duration=180`
   - 10 minutes: `duration=600`
   - 1 hour: `duration=3600`

### Adding More Plans

1. Open `handlers/premium.py`
2. Add new button in `get_plan_selection_keyboard()`:
   ```python
   [InlineKeyboardButton(text="6 Months - ₹100", callback_data="plan_6months_100")]
   ```

3. Add handler in `process_plan_selection()`:
   ```python
   elif callback_data == "plan_6months_100":
       plan_name = "6 Months"
       amount = 100
   ```

## Troubleshooting

### Bot doesn't start

**Error**: `BOT_TOKEN is not set in environment variables`

**Solution**: Make sure you created `.env` file with valid `BOT_TOKEN`

---

**Error**: `ADMIN_ID must be a valid integer`

**Solution**: Ensure `ADMIN_ID` in `.env` is a number (not string with quotes)

---

### Bot doesn't respond

**Solution**: 
1. Check if bot is running (`python bot.py`)
2. Verify bot token is correct
3. Check internet connection
4. Look for error messages in terminal

---

### Admin doesn't receive notifications

**Solution**:
1. Verify `ADMIN_ID` is correct (use @userinfobot to get your ID)
2. Make sure admin started the bot at least once (send `/start`)
3. Check if admin blocked the bot

---

### Timer not working

**Solution**: 
- Timer is asynchronous and runs in background
- Check terminal logs for errors
- Ensure user doesn't change state during timer

---

### QR code not displaying

**Solution**:
1. Ensure `qrcode` and `Pillow` are installed:
   ```bash
   pip install qrcode Pillow
   ```
2. Check terminal for error messages

## Technical Details

### Architecture

- **Framework**: aiogram 3.x (async Telegram bot library)
- **State Management**: FSM (Finite State Machine) with MemoryStorage
- **Async Operations**: All I/O operations are non-blocking
- **Error Handling**: Comprehensive try-catch blocks with logging

### State Flow

1. `None` → Initial state
2. `waiting_for_plan_selection` → After clicking "Premium Plan"
3. `viewing_qr` → QR code displayed
4. `timer_running` → Timer active (5 minutes)
5. `waiting_for_screenshot` → Timer ended, awaiting photo
6. `pending_approval` → Screenshot submitted to admin
7. `None` → State cleared after admin decision

### Security Features

- Admin-only callback verification
- User ID validation
- State-based access control
- Input validation for photos
- Error handling for blocked users

## Performance

- ⚡ **Instant responses**: Async architecture ensures no blocking
- 🚀 **Fast message delivery**: Optimized with aiogram 3.x
- 💾 **Memory efficient**: MemoryStorage for state (no database required)
- ⏱️ **Non-blocking timer**: Background task doesn't freeze bot

## Logging

The bot logs important events:
- Bot startup
- Plan selections
- Timer completions
- Payment submissions
- Admin actions
- Errors and exceptions

Check terminal output for detailed logs.

## Future Enhancements

Potential features for future versions:

- 💾 Database integration for payment history
- 📊 Analytics dashboard
- 🔔 Subscription expiry notifications
- 💬 Multi-language support
- 💳 Direct payment gateway integration
- 👥 Multiple admin support
- 📈 Sales statistics
- 🔄 Auto-renewal system

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review terminal logs for error messages
3. Verify all configuration is correct
4. Ensure Python 3.10.11 is installed

## License

This project is provided as-is for educational and commercial use.

## Credits

Built with:
- [aiogram 3.x](https://docs.aiogram.dev/) - Telegram Bot Framework
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Environment Management
- [qrcode](https://pypi.org/project/qrcode/) - QR Code Generation
- [Pillow](https://pillow.readthedocs.io/) - Image Processing

---

**Version**: 1.0.0  
**Python**: 3.10.11  
**Framework**: aiogram 3.x

Made with ❤️ for fast, smooth, and responsive premium plan sales!
