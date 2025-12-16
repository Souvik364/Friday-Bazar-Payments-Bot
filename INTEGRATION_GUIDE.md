# 🚀 INTEGRATION GUIDE - Activate Multi-Language & Support Bot

## ⚡ QUICK INTEGRATION STEPS

This guide shows you exactly how to integrate the new multi-language and support bot features into your bot.

---

## 📋 WHAT'S READY TO INTEGRATE

✅ Translation system (`utils/translations.py`) - CREATED  
✅ Language handler (`handlers/language.py`) - CREATED  
✅ Support bot config (`config.py`) - UPDATED  
✅ User guide (`USER_GUIDE.md`) - CREATED  
✅ Complete documentation - DONE  

**Now we just need to connect everything!**

---

## 🔧 STEP 1: Setup Support Bot (5 Minutes)

### 1.1 Create Support Bot

```
1. Open Telegram
2. Search @BotFather
3. Send: /newbot
4. Name: "YouTube Premium Support"
5. Username: "your_youtube_support_bot"
6. Save the username (e.g., @your_youtube_support_bot)
```

### 1.2 Configure .env

Edit your `.env` file and add:

```env
SUPPORT_BOT=@your_youtube_support_bot
```

**Example:**
```env
BOT_TOKEN=123456789:ABCdef...
ADMIN_ID=987654321
SUPPORT_BOT=@YourCustomerSupport_Bot
```

---

## 🔧 STEP 2: Update Bot.py (Add Language Router)

### Current bot.py:
```python
dp.include_router(start_router)
dp.include_router(premium_router)
dp.include_router(admin_router)
```

### Update to:
```python
from handlers.language import language_router  # Add this import

dp.include_router(language_router)  # Add this FIRST
dp.include_router(start_router)
dp.include_router(premium_router)
dp.include_router(admin_router)
```

**Complete updated imports section:**
```python
from config import BOT_TOKEN
from handlers.start import start_router
from handlers.premium import premium_router
from handlers.admin import admin_router
from handlers.language import language_router  # NEW
```

---

## 🔧 STEP 3: Update start.py (Language Selection on First Start)

### Add at the top of start.py:

```python
from utils.translations import get_text, get_language_keyboard
from handlers.language import get_user_language
```

### Update get_main_menu_keyboard() function:

**Current:**
```python
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 YouTube Premium")],
            [KeyboardButton(text="ℹ️ Help"), KeyboardButton(text="📊 My Status")]
        ],
        resize_keyboard=True
    )
    return keyboard
```

**Update to:**
```python
def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    from utils.translations import get_text
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "youtube_premium"))],
            [KeyboardButton(text=get_text(lang, "help")), 
             KeyboardButton(text=get_text(lang, "my_status"))],
            [KeyboardButton(text=get_text(lang, "support")),
             KeyboardButton(text=get_text(lang, "change_language"))]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an option..."
    )
    return keyboard
```

### Update cmd_start function:

**Current:**
```python
@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    
    await message.answer(
        f"👋 <b>Welcome to YouTube Premium Bot...
```

**Update to:**
```python
@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language')
    
    # First time user - show language selection
    if not lang:
        from utils.translations import get_language_keyboard
        await message.answer(
            "🌐 <b>Select Your Language</b>\n"
            "अपनी पसंदीदा भाषा चुनें\n"
            "আপনার পছন্দের ভাষা নির্বাচন করুন\n\n"
            "Please choose your preferred language:",
            parse_mode="HTML",
            reply_markup=get_language_keyboard()
        )
        return
    
    # Returning user - show main menu
    await state.clear()
    await state.update_data(language=lang)  # Restore language
    
    from utils.translations import get_text
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    
    welcome_text = get_text(lang, "welcome", message.from_user.first_name)
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang)
    )
```

---

## 🔧 STEP 4: Add Support Command

Add this function to `start.py`:

```python
@start_router.message(Command("support"))
@start_router.message(F.text.in_(["💬 Support", "💬 সাপোর্ট", "💬 सहायता"]))
async def cmd_support(message: Message, state: FSMContext):
    """Show support bot contact."""
    lang = await get_user_language(state)
    
    from config import SUPPORT_BOT
    
    if SUPPORT_BOT and SUPPORT_BOT != "":
        support_text = get_text(lang, "support_text", SUPPORT_BOT, message.from_user.id)
        await message.answer(support_text, parse_mode="HTML")
    else:
        await message.answer(
            "📞 <b>Contact Admin</b>\n\n"
            "Please contact the bot administrator for support.\n"
            f"Your User ID: <code>{message.from_user.id}</code>",
            parse_mode="HTML"
        )
```

---

## 🔧 STEP 5: Update premium.py for Multi-Language

### Add imports at top:

```python
from utils.translations import get_text
from handlers.language import get_user_language
```

### Update show_premium_plans function:

**Find this function and update:**

```python
@premium_router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium", "🎥 YouTube Premium"]))
async def show_premium_plans(message: Message, state: FSMContext, bot: Bot):
    """Show YouTube Premium plan options with animation."""
    lang = await get_user_language(state)
    
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)
    
    await state.set_state(PremiumStates.waiting_for_plan_selection)
    
    await message.answer(
        "✨ <b>Loading...</b>",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.3)
    
    plan_text = get_text(lang, "choose_plan")
    await message.answer(
        plan_text,
        parse_mode="HTML",
        reply_markup=get_plan_selection_keyboard(lang)
    )
```

### Update get_plan_selection_keyboard:

```python
def get_plan_selection_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Create inline keyboard with plan options."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 Month - ₹20", callback_data="plan_1month_20")],
            [InlineKeyboardButton(text="3 Months - ₹55", callback_data="plan_3months_55")],
            [InlineKeyboardButton(text=get_text(lang, "coming_soon") + " 6 Months - ₹100", callback_data="coming_soon")],
            [InlineKeyboardButton(text=get_text(lang, "back_menu"), callback_data="back_to_menu")]
        ]
    )
    return keyboard
```

---

## ✅ STEP 6: Test Everything

### 6.1 Test Language Selection:

```
1. Delete any existing chat with bot
2. Send /start
3. Should see language selection
4. Click English → Messages in English
5. Send /start again → Direct to main menu (no language selection)
```

### 6.2 Test Language Switching:

```
1. Click "🌐 Change Language"
2. Select Hindi
3. All messages now in Hindi
4. Buy plan → Everything in Hindi
```

### 6.3 Test Support Bot:

```
1. Click "💬 Support" button
2. Should see support bot link
3. Click link → Opens support bot
4. Send message to support bot
```

### 6.4 Test Admin Notifications:

```
1. User buys plan (in Hindi)
2. Admin receives notification
3. Admin notification should be in ENGLISH only
4. Admin approves
5. User receives approval in Hindi
```

---

## 📝 COMPLETE FILE STRUCTURE

After integration, your structure should be:

```
telegram-premium-bot/
├── bot.py (✅ Updated - added language_router)
├── config.py (✅ Updated - added SUPPORT_BOT)
├── handlers/
│   ├── __init__.py (FSM states)
│   ├── start.py (✅ Updated - language support)
│   ├── premium.py (✅ Updated - translations)
│   ├── admin.py (always English)
│   └── language.py (✅ NEW - language handler)
├── utils/
│   ├── __init__.py
│   ├── qr_generator.py
│   ├── timer.py
│   └── translations.py (✅ NEW - 800+ lines)
├── .env (Add SUPPORT_BOT)
├── USER_GUIDE.md (✅ NEW)
└── MULTILANGUAGE_SUPPORT.md (✅ NEW)
```

---

## 🎯 SUMMARY OF CHANGES

### Files to Update:

1. **bot.py**
   - Add: `from handlers.language import language_router`
   - Add: `dp.include_router(language_router)` (first router)

2. **start.py**
   - Add: Language selection on first start
   - Update: `get_main_menu_keyboard()` with translations
   - Update: `cmd_start()` to check language
   - Add: `/support` command handler
   - Add: Support and Change Language buttons

3. **premium.py**
   - Add: Import translations
   - Update: All text strings to use `get_text()`
   - Add: Language parameter to keyboards

4. **.env**
   - Add: `SUPPORT_BOT=@your_support_bot`

### Files Already Created:

✅ `utils/translations.py` - Complete translations  
✅ `handlers/language.py` - Language selection  
✅ `USER_GUIDE.md` - User documentation  
✅ `MULTILANGUAGE_SUPPORT.md` - Feature docs  

---

## 🚀 DEPLOYMENT CHECKLIST

Before deploying:

- [ ] Support bot created
- [ ] SUPPORT_BOT added to .env
- [ ] bot.py updated (language_router added)
- [ ] start.py updated (language selection)
- [ ] premium.py updated (translations)
- [ ] All handlers tested locally
- [ ] Language switching tested
- [ ] Support button tested
- [ ] Admin notifications verified (English only)
- [ ] User Guide accessible
- [ ] Ready to deploy!

---

## 💡 OPTIONAL ENHANCEMENTS

### Add /guide Command:

```python
@start_router.message(Command("guide"))
async def cmd_guide(message: Message):
    """Show user guide link."""
    await message.answer(
        "📚 <b>Complete User Guide</b>\n\n"
        "Read our step-by-step guide:\n"
        "👉 https://link-to-your-guide\n\n"
        "Or check the pinned message in this chat!",
        parse_mode="HTML"
    )
```

### Add Language Stats for Admin:

```python
# Track language usage
user_languages = {}  # Store in database

# Show in admin dashboard
"📊 Language Distribution:\n"
"🇬🇧 English: 45%\n"
"🇮🇳 Hindi: 35%\n"
"🇧🇩 Bengali: 20%"
```

---

## ✅ YOU'RE DONE!

After following this guide:

✅ Multi-language fully working  
✅ Support bot integrated  
✅ User guide available  
✅ Professional bot experience  
✅ Ready for users!  

---

**Next:** Test everything locally, then deploy to Render!

**Questions?** Check `MULTILANGUAGE_SUPPORT.md` for details.

**Need help?** All code examples are provided above.

🎉 **Your bot is now multilingual and support-ready!**
