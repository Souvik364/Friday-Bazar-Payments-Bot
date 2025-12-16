
import asyncio
import logging
import os
import sys
import uuid
from io import BytesIO
from datetime import datetime

# Third-party imports
import qrcode
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, 
    CallbackQuery, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    BufferedInputFile
)
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load Env Vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
SUPPORT_BOT = os.getenv("SUPPORT_BOT", "@YourSupportBot")

# Validation
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is missing! Set it in environment variables.")
    sys.exit(1)

if not ADMIN_ID:
    logger.critical("ADMIN_ID is missing! Set it in environment variables.")
    sys.exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    logger.critical("ADMIN_ID must be an integer!")
    sys.exit(1)

# --- TRANSLATIONS ---
TRANSLATIONS = {
    "en": {
        "language_name": "English",
        "welcome": "👋 <b>Welcome to YouTube Premium Bot, {}!</b>\n\n"
                  "🎥 Get <b>YouTube Premium + YouTube Music</b> at affordable prices!\n\n"
                  "✨ <b>What you get:</b>\n"
                  "• 🚫 <b>Ad-Free Videos</b>\n"
                  "• 🎵 <b>YouTube Music Premium</b>\n"
                  "• 📥 <b>Download Videos</b>\n"
                  "• 📱 <b>Background Play</b>\n"
                  "• 🎬 <b>YouTube Originals</b>\n\n"
                  "💡 <i>Click the button below to view plans!</i>",
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ Help",
        "btn_status": "📊 My Status",
        "btn_support": "💬 Support",
        "btn_change_lang": "🌐 Change Language",
        "select_lang_header": "🌐 <b>Select Your Language</b>\n\nPlease choose your preferred language:",
        "choose_plan": "🎥 <b>Choose Your YouTube Premium Plan</b>\n\n🎯 <b>Includes YouTube Music Premium!</b>",
        "plan_1": "1 Month - ₹20",
        "plan_3": "3 Months - ₹55",
        "plan_6_soon": "🔜 6 Months - ₹100 (Coming Soon)",
        "coming_soon_alert": "🔜 6 Months plan coming soon! Stay tuned!",
        "payment_instr": "🎥 <b>YouTube Premium Payment</b>\n\n📦 Plan: <b>{}</b>\n💰 Amount: <b>₹{}</b>\n\n🎁 <b>Includes:</b>\n• 🚫 Ad-free videos\n• 🎵 YouTube Music Premium\n• 📥 Download videos\n\n📱 <b>Scan this QR code to pay</b>\n⏰ Timer: <b>5 minutes</b>\n\n✅ <b>Upload screenshot ANYTIME within 5 minutes!</b>",
        "upload_prompt": "📸 <b>Upload Payment Screenshot</b>\n\nPlease send your payment screenshot as a photo now.",
        "timer_ended": "⏰ <b>Time Expired!</b>\n\nThe 5-minute timer has ended. Please start again.",
        "screenshot_received": "✅ <b>Screenshot Received!</b>\n\n🎉 Admin will review your payment shortly.\nCheck /status for updates.",
        "approved": "🎉 <b>CONGRATULATIONS!</b> 🎉\n\n✅ Your payment is <b>APPROVED</b>!\n\n🎥 <b>Your YouTube Premium is Now ACTIVE!</b>\n\n🎁 <b>Features Unlocked:</b>\n• ✅ Ad-free YouTube\n• ✅ YouTube Music Premium\n• ✅ Background Play",
        "rejected": "❌ <b>Payment Verification Failed</b>\n\nUnfortunately, your payment could not be verified.\nPlease contact support.",
        "support_text": "💬 <b>Need Help?</b>\n\nContact our support team: {}\n\n📝 <b>Include:</b>\n• User ID: <code>{}</code>\n• Screenshot\n• Issue description",
        "status_free": "📍 Status: <b>Free User</b>\n🎥 Premium: <b>Not Active</b>",
        "status_pending": "📍 Status: <b>Pending Approval</b>\n💎 Plan: {}\n⏳ Admin is reviewing...",
        "status_paying": "📍 Status: <b>Payment in Progress</b>\n💎 Plan: {}\n⏰ Complete payment now!",
        "help_text": "📚 <b>Help Guide</b>\n\n1. Click 🎥 YouTube Premium\n2. Select a Plan\n3. Scan QR Code & Pay\n4. Upload Screenshot\n5. Wait for Approval"
    },
    "hi": {
        "language_name": "हिन्दी",
        "welcome": "👋 <b>YouTube Premium बॉट में आपका स्वागत है, {}!</b>\n\n🎥 किफायती कीमतों पर <b>YouTube Premium + Music</b> प्राप्त करें!\n\n✨ <b>सुविधाएं:</b>\n• 🚫 <b>विज्ञापन-मुक्त वीडियो</b>\n• 🎵 <b>YouTube Music Premium</b>\n• 📥 <b>वीडियो डाउनलोड</b>\n• 📱 <b>बैकग्राउंड प्ले</b>",
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ मदद",
        "btn_status": "📊 मेरी स्थिति",
        "btn_support": "💬 सहायता",
        "btn_change_lang": "🌐 भाषा बदलें",
        "select_lang_header": "🌐 <b>अपनी भाषा चुनें</b>\n\nकृपया अपनी पसंदीदा भाषा चुनें:",
        "choose_plan": "🎥 <b>अपना YouTube Premium प्लान चुनें</b>\n\n🎯 <b>YouTube Music Premium शामिल!</b>",
        "plan_1": "1 महीना - ₹20",
        "plan_3": "3 महीने - ₹55",
        "plan_6_soon": "🔜 6 महीने - ₹100 (जल्द आ रहा है)",
        "coming_soon_alert": "🔜 6 महीने का प्लान जल्द आ रहा है!",
        "payment_instr": "🎥 <b>भुगतान विवरण</b>\n\n📦 प्लान: <b>{}</b>\n💰 राशि: <b>₹{}</b>\n\n📱 <b>QR स्कैन करें</b>\n⏰ टाइमर: <b>5 मिनट</b>\n\n✅ <b>5 मिनट के भीतर कभी भी स्क्रीनशॉट अपलोड करें!</b>",
        "upload_prompt": "📸 <b>स्क्रीनशॉट अपलोड करें</b>\n\nकृपया भुगतान का फोटो भेजें।",
        "timer_ended": "⏰ <b>समय समाप्त!</b>\n\nकृपया प्रक्रिया पुनः आरंभ करें।",
        "screenshot_received": "✅ <b>स्क्रीनशॉट प्राप्त हुआ!</b>\n\n🎉 एडमिन जल्द ही समीक्षा करेंगे।",
        "approved": "🎉 <b>बधाई हो!</b> 🎉\n\n✅ आपका भुगतान <b>स्वीकृत</b> हो गया है!\n\n🎥 <b>YouTube Premium अब सक्रिय है!</b>",
        "rejected": "❌ <b>भुगतान विफल</b>\n\nआपका भुगतान सत्यापित नहीं हो सका। कृपया सहायता से संपर्क करें।",
        "support_text": "💬 <b>मदद चाहिए?</b>\n\nसंपर्क करें: {}\n\n📝 <b>भेजें:</b>\n• यूजर ID: <code>{}</code>\n• स्क्रीनशॉट",
        "status_free": "📍 स्थिति: <b>फ्री यूजर</b>\n🎥 प्रीमियम: <b>निष्क्रिय</b>",
        "status_pending": "📍 स्थिति: <b>स्वीकृति लंबित</b>\n💎 प्लान: {}\n⏳ समीक्षा जारी है...",
        "status_paying": "📍 स्थिति: <b>भुगतान जारी</b>\n💎 प्लान: {}\n⏰ भुगतान करें!",
        "help_text": "📚 <b>मदद</b>\n\n1. प्लान चुनें\n2. QR स्कैन करें\n3. स्क्रीनशॉट भेजें\n4. प्रतीक्षा करें"
    },
    "bn": {
        "language_name": "বাংলা",
        "welcome": "👋 <b>YouTube Premium বটে স্বাগতম, {}!</b>\n\n🎥 সাশ্রয়ী মূল্যে <b>YouTube Premium + Music</b> পান!\n\n✨ <b>আপনি যা পাবেন:</b>\n• 🚫 <b>বিজ্ঞাপন-মুক্ত ভিডিও</b>\n• 🎵 <b>YouTube Music Premium</b>\n• 📥 <b>ভিডিও ডাউনলোড</b>\n• 📱 <b>ব্যাকগ্রাউন্ড প্লে</b>",
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ সাহায্য",
        "btn_status": "📊 আমার স্ট্যাটাস",
        "btn_support": "💬 সাপোর্ট",
        "btn_change_lang": "🌐 ভাষা পরিবর্তন",
        "select_lang_header": "🌐 <b>আপনার ভাষা নির্বাচন করুন</b>\n\nঅনুগ্রহ করে আপনার ভাষা চয়ন করুন:",
        "choose_plan": "🎥 <b>আপনার YouTube Premium প্ল্যান বেছে নিন</b>",
        "plan_1": "১ মাস - ₹20",
        "plan_3": "৩ মাস - ₹55",
        "plan_6_soon": "🔜 ৬ মাস - ₹100 (শীঘ্রই আসছে)",
        "coming_soon_alert": "🔜 ৬ মাসের প্ল্যান শীঘ্রই আসছে!",
        "payment_instr": "🎥 <b>পেমেন্ট বিবরণ</b>\n\n📦 প্ল্যান: <b>{}</b>\n💰 পরিমাণ: <b>₹{}</b>\n\n📱 <b>QR স্ক্যান করুন</b>\n⏰ টাইমার: <b>৫ মিনিট</b>\n\n✅ <b>৫ মিনিটের মধ্যে যেকোনো সময় স্ক্রিনশট আপলোড করুন!</b>",
        "upload_prompt": "📸 <b>স্ক্রিনশট আপলোড করুন</b>\n\nঅনুগ্রহ করে পেমেন্টের ছবি পাঠান।",
        "timer_ended": "⏰ <b>সময় শেষ!</b>\n\nঅনুগ্রহ করে আবার শুরু করুন।",
        "screenshot_received": "✅ <b>স্ক্রিনশট প্রাপ্ত হয়েছে!</b>\n\n🎉 অ্যাডমিন শীঘ্রই এটি পর্যালোচনা করবেন।",
        "approved": "🎉 <b>অভিনন্দন!</b> 🎉\n\n✅ আপনার পেমেন্ট <b>অনুমোদিত হয়েছে</b>!\n\n🎥 <b>YouTube Premium এখন সক্রিয়!</b>",
        "rejected": "❌ <b>পেমেন্ট ব্যর্থ</b>\n\nআপনার পেমেন্ট যাচাই করা যায়নি। সাপোর্টে যোগাযোগ করুন।",
        "support_text": "💬 <b>সাহায্য দরকার?</b>\n\nযোগাযোগ: {}\n\n📝 <b>অন্তর্ভুক্ত করুন:</b>\n• ইউজার ID: <code>{}</code>\n• স্ক্রিনশট",
        "status_free": "📍 স্ট্যাটাস: <b>ফ্রি ইউজার</b>\n🎥 প্রিমিয়াম: <b>নিষ্ক্রিয়</b>",
        "status_pending": "📍 স্ট্যাটাস: <b>অপেক্ষমান</b>\n💎 প্ল্যান: {}\n⏳ পর্যালোচনা চলছে...",
        "status_paying": "📍 স্ট্যাটাস: <b>পেমেন্ট চলছে</b>\n💎 প্ল্যান: {}\n⏰ পেমেন্ট করুন!",
        "help_text": "📚 <b>সাহায্য</b>\n\n১. প্ল্যান নির্বাচন করুন\n২. QR স্ক্যান করুন\n৩. স্ক্রিনশট আপলোড করুন\n৪. অপেক্ষা করুন"
    }
}

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_plan_selection = State()
    viewing_qr = State()
    timer_running = State()
    waiting_for_screenshot = State()
    pending_approval = State()

# --- UTILS ---
def get_text(lang: str, key: str, *args) -> str:
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    if args:
        try: return text.format(*args)
        except: return text
    return text

def generate_qr(plan_name: str, amount: int) -> BytesIO:
    # Fake/Test QR Data. Replace with real UPI string for production:
    # f"upi://pay?pa=YOUR_UPI@okaxis&pn=PremiumBot&am={amount}&tn={plan_name}"
    qr_data = f"upi://pay?pa=YOUR_UPI@okaxis&pn=PremiumBot&am={amount}&tn={plan_name}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

async def start_payment_timer(bot: Bot, chat_id: int, state: FSMContext, duration: int, payment_id: str):
    """
    Non-blocking timer.
    Includes 'payment_id' check to ensure we don't expire new sessions if user restarted.
    """
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        data = await state.get_data()
        
        # Check if the session ID matches. If user started new payment, IDs won't match.
        if data.get("payment_id") != payment_id:
            return

        # Only notify if user hasn't uploaded yet (still in timer_running state)
        if current_state == BotStates.timer_running.state:
            lang = data.get("language", "en")
            
            await state.set_state(BotStates.waiting_for_screenshot)
            await bot.send_message(chat_id, get_text(lang, "timer_ended"))
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Timer error: {e}")

# --- KEYBOARDS ---
def get_main_kb(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_premium"))],
            [KeyboardButton(text=get_text(lang, "btn_help")), KeyboardButton(text=get_text(lang, "btn_status"))],
            [KeyboardButton(text=get_text(lang, "btn_support")), KeyboardButton(text=get_text(lang, "btn_change_lang"))]
        ],
        resize_keyboard=True
    )

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇧🇩 বাংলা (Bengali)", callback_data="lang_bn")]
    ])

def get_plan_kb(lang="en"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "plan_1"), callback_data="plan_1month_20")],
        [InlineKeyboardButton(text=get_text(lang, "plan_3"), callback_data="plan_3months_55")],
        [InlineKeyboardButton(text=get_text(lang, "plan_6_soon"), callback_data="coming_soon")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_payment")]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="📞 Contact User", callback_data=f"contact_{user_id}")]
    ])

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# --- HANDLERS ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language')
    
    # If language not set, show language picker first
    if not lang:
        await message.answer(
            "🌐 <b>Select Your Language</b>\n"
            "अपनी पसंदीदा भाषा चुनें\n"
            "আপনার পছন্দের ভাষা নির্বাচন করুন",
            reply_markup=get_lang_kb()
        )
        return

    # Language exists, show main menu
    await state.clear()
    await state.update_data(language=lang)
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    await message.answer(
        get_text(lang, "welcome", message.from_user.first_name),
        reply_markup=get_main_kb(lang)
    )

@router.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(language=lang_code)
    await callback.answer()
    
    msg = get_text(lang_code, "welcome", callback.from_user.first_name)
    await callback.message.answer(msg, reply_markup=get_main_kb(lang_code))

@router.message(F.text.in_(["🌐 Change Language", "🌐 भाषा बदलें", "🌐 ভাষা পরিবর্তন"]))
async def change_lang_btn(message: Message):
    await message.answer("🌐 Select Language:", reply_markup=get_lang_kb())

# --- Support Handler ---
@router.message(Command("support"))
@router.message(F.text.in_(["💬 Support", "💬 सहायता", "💬 সাপোর্ট"]))
async def support_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    msg = get_text(lang, "support_text", SUPPORT_BOT, message.from_user.id)
    await message.answer(msg)

# --- Premium Plan Handler ---
@router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium"]))
async def premium_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await state.set_state(BotStates.waiting_for_plan_selection)
    
    await message.answer("⏳ <i>Loading plans...</i>")
    await asyncio.sleep(0.5)
    
    await message.answer(get_text(lang, "choose_plan"), reply_markup=get_plan_kb(lang))

@router.callback_query(F.data == "coming_soon")
async def coming_soon_alert(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer(get_text(lang, "coming_soon_alert"), show_alert=True)

@router.callback_query(F.data == "cancel_payment")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await state.clear()
    await state.update_data(language=lang)
    await callback.message.edit_text("❌ Operation Cancelled")

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer("⏳ Generating QR...")
    data = await state.get_data()
    lang = data.get("language", "en")
    
    plans = {
        "plan_1month_20": ("1 Month YouTube Premium", 20),
        "plan_3months_55": ("3 Months YouTube Premium", 55)
    }
    
    if callback.data not in plans: return
    plan_name, amount = plans[callback.data]
    
    # Generate Unique Payment ID for this session
    payment_id = str(uuid.uuid4())
    
    # Generate QR
    qr_buffer = generate_qr(plan_name, amount)
    qr_file = BufferedInputFile(qr_buffer.read(), filename="qr.png")
    
    await state.update_data(plan_name=plan_name, amount=amount, payment_id=payment_id)
    await state.set_state(BotStates.timer_running)
    
    caption = get_text(lang, "payment_instr", plan_name, amount)
    
    await callback.message.answer_photo(
        photo=qr_file,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📤 Upload Screenshot Now", callback_data="upload_now")
        ]])
    )
    
    # Start Timer with Payment ID check
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state, 300, payment_id))

@router.callback_query(F.data == "upload_now")
async def ask_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_prompt"))

# Accept photo in both states (Flexible Upload Feature)
@router.message(StateFilter(BotStates.timer_running, BotStates.waiting_for_screenshot), F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    plan = data.get("plan_name", "Unknown")
    amount = data.get("amount", 0)
    
    await message.answer(get_text(lang, "screenshot_received"))
    await state.set_state(BotStates.pending_approval)
    
    # Admin Notification
    admin_text = (
        f"🔔 <b>NEW PAYMENT</b>\n\n"
        f"👤 User: {message.from_user.full_name} (ID: <code>{message.from_user.id}</code>)\n"
        f"📦 Plan: {plan}\n"
        f"💰 Amount: ₹{amount}\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=get_admin_kb(message.from_user.id)
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
        await message.answer("⚠️ Technical Error: Could not notify admin. Please contact support manually.")

# --- Status Handler ---
@router.message(F.text.in_(["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]))
async def status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    current_state = await state.get_state()
    plan = data.get("plan_name", "N/A")
    
    if current_state == BotStates.pending_approval.state:
        status_msg = get_text(lang, "status_pending", plan)
    elif current_state in [BotStates.timer_running.state, BotStates.waiting_for_screenshot.state]:
        status_msg = get_text(lang, "status_paying", plan)
    else:
        status_msg = get_text(lang, "status_free")
        
    await message.answer(f"👤 <b>User:</b> {message.from_user.full_name}\n{status_msg}")

@router.message(F.text.in_(["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]))
async def help_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await message.answer(get_text(lang, "help_text"))

# --- ADMIN HANDLERS ---
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    
    action, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)
    
    # Notification to User
    try:
        if action == "approve":
            await bot.send_message(user_id, TRANSLATIONS["en"]["approved"])
            status = "✅ APPROVED"
        else:
            await bot.send_message(user_id, TRANSLATIONS["en"]["rejected"])
            status = "❌ REJECTED"
            
             "timer_ended": "⏰ <b>समय समाप्त!</b>\n\nकृपया प्रक्रिया पुनः आरंभ करें।",
        "screenshot_received": "✅ <b>स्क्रीनशॉट प्राप्त हुआ!</b>\n\n🎉 एडमिन जल्द ही समीक्षा करेंगे।",
        "approved": "🎉 <b>बधाई हो!</b> 🎉\n\n✅ आपका भुगतान <b>स्वीकृत</b> हो गया है!\n\n🎥 <b>YouTube Premium अब सक्रिय है!</b>",
        "rejected": "❌ <b>भुगतान विफल</b>\n\nआपका भुगतान सत्यापित नहीं हो सका। कृपया सहायता से संपर्क करें।",
        "support_text": "💬 <b>मदद चाहिए?</b>\n\nसंपर्क करें: {}\n\n📝 <b>भेजें:</b>\n• यूजर ID: <code>{}</code>\n• स्क्रीनशॉट",
        "status_free": "📍 स्थिति: <b>फ्री यूजर</b>\n🎥 प्रीमियम: <b>निष्क्रिय</b>",
        "status_pending": "📍 स्थिति: <b>स्वीकृति लंबित</b>\n💎 प्लान: {}\n⏳ समीक्षा जारी है...",
        "status_paying": "📍 स्थिति: <b>भुगतान जारी</b>\n💎 प्लान: {}\n⏰ भुगतान करें!",
        "help_text": "📚 <b>मदद</b>\n\n1. प्लान चुनें\n2. QR स्कैन करें\n3. स्क्रीनशॉट भेजें\n4. प्रतीक्षा करें"
    },
    "bn": {
        "language_name": "বাংলা",
        "welcome": "👋 <b>YouTube Premium বটে স্বাগতম, {}!</b>\n\n🎥 সাশ্রয়ী মূল্যে <b>YouTube Premium + Music</b> পান!\n\n✨ <b>আপনি যা পাবেন:</b>\n• 🚫 <b>বিজ্ঞাপন-মুক্ত ভিডিও</b>\n• 🎵 <b>YouTube Music Premium</b>\n• 📥 <b>ভিডিও ডাউনলোড</b>\n• 📱 <b>ব্যাকগ্রাউন্ড প্লে</b>",
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ সাহায্য",
        "btn_status": "📊 আমার স্ট্যাটাস",
        "btn_support": "💬 সাপোর্ট",
        "btn_change_lang": "🌐 ভাষা পরিবর্তন",
        "select_lang_header": "🌐 <b>আপনার ভাষা নির্বাচন করুন</b>\n\nঅনুগ্রহ করে আপনার ভাষা চয়ন করুন:",
        "choose_plan": "🎥 <b>আপনার YouTube Premium প্ল্যান বেছে নিন</b>",
        "plan_1": "১ মাস - ₹20",
        "plan_3": "৩ মাস - ₹55",
        "plan_6_soon": "🔜 ৬ মাস - ₹100 (শীঘ্রই আসছে)",
        "coming_soon_alert": "🔜 ৬ মাসের প্ল্যান শীঘ্রই আসছে!",
        "payment_instr": "🎥 <b>পেমেন্ট বিবরণ</b>\n\n📦 প্ল্যান: <b>{}</b>\n💰 পরিমাণ: <b>₹{}</b>\n\n📱 <b>QR স্ক্যান করুন</b>\n⏰ টাইমার: <b>৫ মিনিট</b>\n\n✅ <b>৫ মিনিটের মধ্যে যেকোনো সময় স্ক্রিনশট আপলোড করুন!</b>",
        "upload_prompt": "📸 <b>স্ক্রিনশট আপলোড করুন</b>\n\nঅনুগ্রহ করে পেমেন্টের ছবি পাঠান।",
        "timer_ended": "⏰ <b>সময় শেষ!</b>\n\nঅনুগ্রহ করে আবার শুরু করুন।",
        "screenshot_received": "✅ <b>স্ক্রিনশট প্রাপ্ত হয়েছে!</b>\n\n🎉 অ্যাডমিন শীঘ্রই এটি পর্যালোচনা করবেন।",
        "approved": "🎉 <b>অভিনন্দন!</b> 🎉\n\n✅ আপনার পেমেন্ট <b>অনুমোদিত হয়েছে</b>!\n\n🎥 <b>YouTube Premium এখন সক্রিয়!</b>",
        "rejected": "❌ <b>পেমেন্ট ব্যর্থ</b>\n\nআপনার পেমেন্ট যাচাই করা যায়নি। সাপোর্টে যোগাযোগ করুন।",
        "support_text": "💬 <b>সাহায্য দরকার?</b>\n\nযোগাযোগ: {}\n\n📝 <b>অন্তর্ভুক্ত করুন:</b>\n• ইউজার ID: <code>{}</code>\n• স্ক্রিনশট",
        "status_free": "📍 স্ট্যাটাস: <b>ফ্রি ইউজার</b>\n🎥 প্রিমিয়াম: <b>নিষ্ক্রিয়</b>",
        "status_pending": "📍 স্ট্যাটাস: <b>অপেক্ষমান</b>\n💎 প্ল্যান: {}\n⏳ পর্যালোচনা চলছে...",
        "status_paying": "📍 স্ট্যাটাস: <b>পেমেন্ট চলছে</b>\n💎 প্ল্যান: {}\n⏰ পেমেন্ট করুন!",
        "help_text": "📚 <b>সাহায্য</b>\n\n১. প্ল্যান নির্বাচন করুন\n২. QR স্ক্যান করুন\n৩. স্ক্রিনশট আপলোড করুন\n৪. অপেক্ষা করুন"
    }
}

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_plan_selection = State()
    viewing_qr = State()
    timer_running = State()
    waiting_for_screenshot = State()
    pending_approval = State()

# --- UTILS ---
def get_text(lang: str, key: str, *args) -> str:
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    if args:
        try: return text.format(*args)
        except: return text
    return text

def generate_qr(plan_name: str, amount: int) -> BytesIO:
    # Fake/Test QR Data. Replace with real UPI string for production:
    # f"upi://pay?pa=YOUR_UPI@okaxis&pn=PremiumBot&am={amount}&tn={plan_name}"
    qr_data = f"upi://pay?pa=YOUR_UPI@okaxis&pn=PremiumBot&am={amount}&tn={plan_name}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

async def start_payment_timer(bot: Bot, chat_id: int, state: FSMContext, duration: int, payment_id: str):
    """
    Non-blocking timer.
    Includes 'payment_id' check to ensure we don't expire new sessions if user restarted.
    """
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        data = await state.get_data()
        
        # Check if the session ID matches. If user started new payment, IDs won't match.
        if data.get("payment_id") != payment_id:
            return

        # Only notify if user hasn't uploaded yet (still in timer_running state)
        if current_state == BotStates.timer_running.state:
            lang = data.get("language", "en")
            
            await state.set_state(BotStates.waiting_for_screenshot)
            await bot.send_message(chat_id, get_text(lang, "timer_ended"))
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Timer error: {e}")

# --- KEYBOARDS ---
def get_main_kb(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_premium"))],
            [KeyboardButton(text=get_text(lang, "btn_help")), KeyboardButton(text=get_text(lang, "btn_status"))],
            [KeyboardButton(text=get_text(lang, "btn_support")), KeyboardButton(text=get_text(lang, "btn_change_lang"))]
        ],
        resize_keyboard=True
    )

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇧🇩 বাংলা (Bengali)", callback_data="lang_bn")]
    ])

def get_plan_kb(lang="en"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "plan_1"), callback_data="plan_1month_20")],
        [InlineKeyboardButton(text=get_text(lang, "plan_3"), callback_data="plan_3months_55")],
        [InlineKeyboardButton(text=get_text(lang, "plan_6_soon"), callback_data="coming_soon")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_payment")]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="📞 Contact User", callback_data=f"contact_{user_id}")]
    ])

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# --- HANDLERS ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language')
    
    # If language not set, show language picker first
    if not lang:
        await message.answer(
            "🌐 <b>Select Your Language</b>\n"
            "अपनी पसंदीदा भाषा चुनें\n"
            "আপনার পছন্দের ভাষা নির্বাচন করুন",
            reply_markup=get_lang_kb()
        )
        return

    # Language exists, show main menu
    await state.clear()
    await state.update_data(language=lang)
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    await message.answer(
        get_text(lang, "welcome", message.from_user.first_name),
        reply_markup=get_main_kb(lang)
    )

@router.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(language=lang_code)
    await callback.answer()
    
    msg = get_text(lang_code, "welcome", callback.from_user.first_name)
    await callback.message.answer(msg, reply_markup=get_main_kb(lang_code))

@router.message(F.text.in_(["🌐 Change Language", "🌐 भाषा बदलें", "🌐 ভাষা পরিবর্তন"]))
async def change_lang_btn(message: Message):
    await message.answer("🌐 Select Language:", reply_markup=get_lang_kb())

# --- Support Handler ---
@router.message(Command("support"))
@router.message(F.text.in_(["💬 Support", "💬 सहायता", "💬 সাপোর্ট"]))
async def support_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    msg = get_text(lang, "support_text", SUPPORT_BOT, message.from_user.id)
    await message.answer(msg)

# --- Premium Plan Handler ---
@router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium"]))
async def premium_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await state.set_state(BotStates.waiting_for_plan_selection)
    
    await message.answer("⏳ <i>Loading plans...</i>")
    await asyncio.sleep(0.5)
    
    await message.answer(get_text(lang, "choose_plan"), reply_markup=get_plan_kb(lang))

@router.callback_query(F.data == "coming_soon")
async def coming_soon_alert(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer(get_text(lang, "coming_soon_alert"), show_alert=True)

@router.callback_query(F.data == "cancel_payment")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await state.clear()
    await state.update_data(language=lang)
    await callback.message.edit_text("❌ Operation Cancelled")

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer("⏳ Generating QR...")
    data = await state.get_data()
    lang = data.get("language", "en")
    
    plans = {
        "plan_1month_20": ("1 Month YouTube Premium", 20),
        "plan_3months_55": ("3 Months YouTube Premium", 55)
    }
    
    if callback.data not in plans: return
    plan_name, amount = plans[callback.data]
    
    # Generate Unique Payment ID for this session
    payment_id = str(uuid.uuid4())
    
    # Generate QR
    qr_buffer = generate_qr(plan_name, amount)
    qr_file = BufferedInputFile(qr_buffer.read(), filename="qr.png")
    
    await state.update_data(plan_name=plan_name, amount=amount, payment_id=payment_id)
    await state.set_state(BotStates.timer_running)
    
    caption = get_text(lang, "payment_instr", plan_name, amount)
    
    await callback.message.answer_photo(
        photo=qr_file,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📤 Upload Screenshot Now", callback_data="upload_now")
        ]])
    )
    
    # Start Timer with Payment ID check
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state, 300, payment_id))

@router.callback_query(F.data == "upload_now")
async def ask_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_prompt"))

# Accept photo in both states (Flexible Upload Feature)
@router.message(StateFilter(BotStates.timer_running, BotStates.waiting_for_screenshot), F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    plan = data.get("plan_name", "Unknown")
    amount = data.get("amount", 0)
    
    await message.answer(get_text(lang, "screenshot_received"))
    await state.set_state(BotStates.pending_approval)
    
    # Admin Notification
    admin_text = (
        f"🔔 <b>NEW PAYMENT</b>\n\n"
        f"👤 User: {message.from_user.full_name} (ID: <code>{message.from_user.id}</code>)\n"
        f"📦 Plan: {plan}\n"
        f"💰 Amount: ₹{amount}\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=get_admin_kb(message.from_user.id)
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
        await message.answer("⚠️ Technical Error: Could not notify admin. Please contact support manually.")

# --- Status Handler ---
@router.message(F.text.in_(["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]))
async def status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    current_state = await state.get_state()
    plan = data.get("plan_name", "N/A")
    
    if current_state == BotStates.pending_approval.state:
        status_msg = get_text(lang, "status_pending", plan)
    elif current_state in [BotStates.timer_running.state, BotStates.waiting_for_screenshot.state]:
        status_msg = get_text(lang, "status_paying", plan)
    else:
        status_msg = get_text(lang, "status_free")
        
    await message.answer(f"👤 <b>User:</b> {message.from_user.full_name}\n{status_msg}")

@router.message(F.text.in_(["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]))
async def help_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await message.answer(get_text(lang, "help_text"))

# --- ADMIN HANDLERS ---
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    
    action, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)
    
    # Notification to User
    try:
        if action == "approve":
            await bot.send_message(user_id, TRANSLATIONS["en"]["approved"])
            status = "✅ APPROVED"
        else:
            await bot.send_message(user_id, TRANSLATIONS["en"]["rejected"])
            status = "❌ REJECTED"
            
             "screenshot_received": "✅ <b>स्क्रीनशॉट प्राप्त हुआ!</b>\n\n🎉 एडमिन जल्द ही समीक्षा करेंगे।",
        "approved": "🎉 <b>बधाई हो!</b> 🎉\n\n✅ आपका भुगतान <b>स्वीकृत</b> हो गया है!\n\n🎥 <b>YouTube Premium अब सक्रिय है!</b>",
        "rejected": "❌ <b>भुगतान विफल</b>\n\nआपका भुगतान सत्यापित नहीं हो सका। कृपया सहायता से संपर्क करें।",
        "support_text": "💬 <b>मदद चाहिए?</b>\n\nसंपर्क करें: {}\n\n📝 <b>भेजें:</b>\n• यूजर ID: <code>{}</code>\n• स्क्रीनशॉट",
        "status_free": "📍 स्थिति: <b>फ्री यूजर</b>\n🎥 प्रीमियम: <b>निष्क्रिय</b>",
        "status_pending": "📍 स्थिति: <b>स्वीकृति लंबित</b>\n💎 प्लान: {}\n⏳ समीक्षा जारी है...",
        "status_paying": "📍 स्थिति: <b>भुगतान जारी</b>\n💎 प्लान: {}\n⏰ भुगतान करें!",
        "help_text": "📚 <b>मदद</b>\n\n1. प्लान चुनें\n2. QR स्कैन करें\n3. स्क्रीनशॉट भेजें\n4. प्रतीक्षा करें"
    },
    "bn": {
        "language_name": "বাংলা",
        "welcome": "👋 <b>YouTube Premium বটে স্বাগতম, {}!</b>\n\n🎥 সাশ্রয়ী মূল্যে <b>YouTube Premium + Music</b> পান!\n\n✨ <b>আপনি যা পাবেন:</b>\n• 🚫 <b>বিজ্ঞাপন-মুক্ত ভিডিও</b>\n• 🎵 <b>YouTube Music Premium</b>\n• 📥 <b>ভিডিও ডাউনলোড</b>\n• 📱 <b>ব্যাকগ্রাউন্ড প্লে</b>",
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ সাহায্য",
        "btn_status": "📊 আমার স্ট্যাটাস",
        "btn_support": "💬 সাপোর্ট",
        "btn_change_lang": "🌐 ভাষা পরিবর্তন",
        "select_lang_header": "🌐 <b>আপনার ভাষা নির্বাচন করুন</b>\n\nঅনুগ্রহ করে আপনার ভাষা চয়ন করুন:",
        "choose_plan": "🎥 <b>আপনার YouTube Premium প্ল্যান বেছে নিন</b>",
        "plan_1": "১ মাস - ₹20",
        "plan_3": "৩ মাস - ₹55",
        "plan_6_soon": "🔜 ৬ মাস - ₹100 (শীঘ্রই আসছে)",
        "coming_soon_alert": "🔜 ৬ মাসের প্ল্যান শীঘ্রই আসছে!",
        "payment_instr": "🎥 <b>পেমেন্ট বিবরণ</b>\n\n📦 প্ল্যান: <b>{}</b>\n💰 পরিমাণ: <b>₹{}</b>\n\n📱 <b>QR স্ক্যান করুন</b>\n⏰ টাইমার: <b>৫ মিনিট</b>\n\n✅ <b>৫ মিনিটের মধ্যে যেকোনো সময় স্ক্রিনশট আপলোড করুন!</b>",
        "upload_prompt": "📸 <b>স্ক্রিনশট আপলোড করুন</b>\n\nঅনুগ্রহ করে পেমেন্টের ছবি পাঠান।",
        "timer_ended": "⏰ <b>সময় শেষ!</b>\n\nঅনুগ্রহ করে আবার শুরু করুন।",
        "screenshot_received": "✅ <b>স্ক্রিনশট প্রাপ্ত হয়েছে!</b>\n\n🎉 অ্যাডমিন শীঘ্রই এটি পর্যালোচনা করবেন।",
        "approved": "🎉 <b>অভিনন্দন!</b> 🎉\n\n✅ আপনার পেমেন্ট <b>অনুমোদিত হয়েছে</b>!\n\n🎥 <b>YouTube Premium এখন সক্রিয়!</b>",
        "rejected": "❌ <b>পেমেন্ট ব্যর্থ</b>\n\nআপনার পেমেন্ট যাচাই করা যায়নি। সাপোর্টে যোগাযোগ করুন।",
        "support_text": "💬 <b>সাহায্য দরকার?</b>\n\nযোগাযোগ: {}\n\n📝 <b>অন্তর্ভুক্ত করুন:</b>\n• ইউজার ID: <code>{}</code>\n• স্ক্রিনশট",
        "status_free": "📍 স্ট্যাটাস: <b>ফ্রি ইউজার</b>\n🎥 প্রিমিয়াম: <b>নিষ্ক্রিয়</b>",
        "status_pending": "📍 স্ট্যাটাস: <b>অপেক্ষমান</b>\n💎 প্ল্যান: {}\n⏳ পর্যালোচনা চলছে...",
        "status_paying": "📍 স্ট্যাটাস: <b>পেমেন্ট চলছে</b>\n💎 প্ল্যান: {}\n⏰ পেমেন্ট করুন!",
        "help_text": "📚 <b>সাহায্য</b>\n\n১. প্ল্যান নির্বাচন করুন\n২. QR স্ক্যান করুন\n৩. স্ক্রিনশট আপলোড করুন\n৪. অপেক্ষা করুন"
    }
}

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_plan_selection = State()
    viewing_qr = State()
    timer_running = State()
    waiting_for_screenshot = State()
    pending_approval = State()

# --- UTILS ---
def get_text(lang: str, key: str, *args) -> str:
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    if args:
        try: return text.format(*args)
        except: return text
    return text

def generate_qr(plan_name: str, amount: int) -> BytesIO:
    # Fake/Test QR Data. Replace with real UPI string for production:
    # f"upi://pay?pa=YOUR_UPI@okaxis&pn=PremiumBot&am={amount}&tn={plan_name}"
    qr_data = f"TEST_PAYMENT|Plan:{plan_name}|Amount:{amount}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

async def start_payment_timer(bot: Bot, chat_id: int, state: FSMContext, duration: int = 300):
    """5 Minute non-blocking timer"""
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        
        # Only notify if user hasn't uploaded yet
        if current_state == BotStates.timer_running.state:
            user_data = await state.get_data()
            lang = user_data.get("language", "en")
            
            await state.set_state(BotStates.waiting_for_screenshot)
            await bot.send_message(chat_id, get_text(lang, "timer_ended"))
            # We don't clear state here to allow late uploads if you want, 
            # but usually timer end means strict cutoff. 
            # Uncomment next line to force restart:
            # await state.clear()
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Timer error: {e}")

# --- KEYBOARDS ---
def get_main_kb(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_premium"))],
            [KeyboardButton(text=get_text(lang, "btn_help")), KeyboardButton(text=get_text(lang, "btn_status"))],
            [KeyboardButton(text=get_text(lang, "btn_support")), KeyboardButton(text=get_text(lang, "btn_change_lang"))]
        ],
        resize_keyboard=True
    )

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇧🇩 বাংলা (Bengali)", callback_data="lang_bn")]
    ])

def get_plan_kb(lang="en"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "plan_1"), callback_data="plan_1month_20")],
        [InlineKeyboardButton(text=get_text(lang, "plan_3"), callback_data="plan_3months_55")],
        [InlineKeyboardButton(text=get_text(lang, "plan_6_soon"), callback_data="coming_soon")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_payment")]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="📞 Contact User", callback_data=f"contact_{user_id}")]
    ])

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# --- HANDLERS ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('language')
    
    # If language not set, show language picker first
    if not lang:
        await message.answer(
            "🌐 <b>Select Your Language</b>\n"
            "अपनी पसंदीदा भाषा चुनें\n"
            "আপনার পছন্দের ভাষা নির্বাচন করুন",
            reply_markup=get_lang_kb()
        )
        return

    # Language exists, show main menu
    await state.clear()
    await state.update_data(language=lang)
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    await message.answer(
        get_text(lang, "welcome", message.from_user.first_name),
        reply_markup=get_main_kb(lang)
    )

@router.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(language=lang_code)
    await callback.answer()
    
    msg = get_text(lang_code, "welcome", callback.from_user.first_name)
    await callback.message.answer(msg, reply_markup=get_main_kb(lang_code))

@router.message(F.text.in_(["🌐 Change Language", "🌐 भाषा बदलें", "🌐 ভাষা পরিবর্তন"]))
async def change_lang_btn(message: Message):
    await message.answer("🌐 Select Language:", reply_markup=get_lang_kb())

# --- Support Handler ---
@router.message(Command("support"))
@router.message(F.text.in_(["💬 Support", "💬 सहायता", "💬 সাপোর্ট"]))
async def support_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    msg = get_text(lang, "support_text", SUPPORT_BOT, message.from_user.id)
    await message.answer(msg)

# --- Premium Plan Handler ---
@router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium"])) # Matches all langs if keys match
async def premium_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    
    await state.set_state(BotStates.waiting_for_plan_selection)
    
    await message.answer("⏳ <i>Loading plans...</i>")
    await asyncio.sleep(0.5)
    
    await message.answer(get_text(lang, "choose_plan"), reply_markup=get_plan_kb(lang))

@router.callback_query(F.data == "coming_soon")
async def coming_soon_alert(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer(get_text(lang, "coming_soon_alert"), show_alert=True)

@router.callback_query(F.data == "cancel_payment")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await state.clear()
    await state.update_data(language=lang)
    await callback.message.edit_text("❌ Operation Cancelled")

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer("⏳ Generating QR...")
    data = await state.get_data()
    lang = data.get("language", "en")
    
    plans = {
        "plan_1month_20": ("1 Month YouTube Premium", 20),
        "plan_3months_55": ("3 Months YouTube Premium", 55)
    }
    
    if callback.data not in plans: return
    plan_name, amount = plans[callback.data]
    
    # Generate QR
    qr_buffer = generate_qr(plan_name, amount)
    qr_file = BufferedInputFile(qr_buffer.read(), filename="qr.png")
    
    await state.update_data(plan_name=plan_name, amount=amount)
    await state.set_state(BotStates.timer_running)
    
    caption = get_text(lang, "payment_instr", plan_name, amount)
    
    await callback.message.answer_photo(
        photo=qr_file,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📤 Upload Screenshot Now", callback_data="upload_now")
        ]])
    )
    
    # Start Timer
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state))

@router.callback_query(F.data == "upload_now")
async def ask_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_prompt"))

# Accept photo in both states (Flexible Upload Feature)
@router.message(StateFilter(BotStates.timer_running, BotStates.waiting_for_screenshot), F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    plan = data.get("plan_name", "Unknown")
    amount = data.get("amount", 0)
    
    await message.answer(get_text(lang, "screenshot_received"))
    await state.set_state(BotStates.pending_approval)
    
    # Admin Notification
    admin_text = (
        f"🔔 <b>NEW PAYMENT</b>\n\n"
        f"👤 User: {message.from_user.full_name} (ID: <code>{message.from_user.id}</code>)\n"
        f"📦 Plan: {plan}\n"
        f"💰 Amount: ₹{amount}\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=get_admin_kb(message.from_user.id)
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# --- Status Handler ---
@router.message(F.text.in_(["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]))
async def status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    current_state = await state.get_state()
    plan = data.get("plan_name", "N/A")
    
    if current_state == BotStates.pending_approval.state:
        status_msg = get_text(lang, "status_pending", plan)
    elif current_state in [BotStates.timer_running.state, BotStates.waiting_for_screenshot.state]:
        status_msg = get_text(lang, "status_paying", plan)
    else:
        status_msg = get_text(lang, "status_free")
        
    await message.answer(f"👤 <b>User:</b> {message.from_user.full_name}\n{status_msg}")

@router.message(F.text.in_(["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]))
async def help_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await message.answer(get_text(lang, "help_text"))

# --- ADMIN HANDLERS ---
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    
    action, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)
    
    # Send notification to user
    # Note: In a stateless admin handler, we assume English/Default or check DB.
    # Here we send bilingual or standard English to ensure delivery.
    if action == "approve":
        await bot.send_message(user_id, TRANSLATIONS["en"]["approved"])
        status = "✅ APPROVED"
    else:
        await bot.send_message(user_id, TRANSLATIONS["en"]["rejected"])
        status = "❌ REJECTED"
        
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n{status}\nBy Admin: {callback.from_user.first_name}"
    )
        "screenshot_received": "✅ <b>স্ক্রিনশট প্রাপ্ত হয়েছে!</b>\n\nঅ্যাডমিন শীঘ্রই এটি পর্যালোচনা করবেন।",
        "approved": "🎉 <b>অনুমোদিত!</b>\n\nআপনার YouTube Premium এখন সক্রিয়!",
        "rejected": "❌ <b>প্রত্যাখ্যাত</b>\n\nআপনার পেমেন্ট যাচাই করা যায়নি।",
        "cancelled": "❌ প্রক্রিয়া বাতিল করা হয়েছে।",
        "help_text": "📚 <b>সাহায্য</b>\n\n১. প্ল্যান নির্বাচন করুন\n২. QR কোড স্ক্যান করুন\n৩. স্ক্রিনশট আপলোড করুন\n৪. অনুমোদনের জন্য অপেক্ষা করুন",
        "status_free": "📍 স্ট্যাটাস: <b>ফ্রি ইউজার</b>\n❌ প্রিমিয়াম: নিষ্ক্রিয়",
        "status_pending": "📍 স্ট্যাটাস: <b>অনুমোদনের অপেক্ষায়</b>\n⏳ অনুগ্রহ করে অপেক্ষা করুন।",
        "status_paying": "📍 স্ট্যাটাস: <b>পেমেন্ট চলছে</b>\n⏳ এখনই পেমেন্ট সম্পন্ন করুন!",
    }
}

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_plan_selection = State()
    viewing_qr = State()
    timer_running = State()
    waiting_for_screenshot = State()
    pending_approval = State()

# --- UTILS ---
def get_text(lang: str, key: str, *args) -> str:
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    if args:
        try: return text.format(*args)
        except: return text
    return text

def generate_qr(plan_name: str, amount: int) -> BytesIO:
    # Generates a dummy/test QR. Replace `qr_data` with actual UPI string if needed.
    qr_data = f"upi://pay?pa=YOUR_UPI_ID&pn=PremiumBot&am={amount}&tn={plan_name}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

async def start_payment_timer(bot: Bot, chat_id: int, state: FSMContext, duration: int = 300):
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        if current_state == BotStates.timer_running.state:
            user_data = await state.get_data()
            lang = user_data.get("language", "en")
            await state.set_state(BotStates.waiting_for_screenshot)
            await bot.send_message(chat_id, get_text(lang, "timer_ended"))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Timer error: {e}")

# --- KEYBOARDS ---
def get_main_kb(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "btn_premium"))],
            [KeyboardButton(text=get_text(lang, "btn_help")), KeyboardButton(text=get_text(lang, "btn_status"))],
            [KeyboardButton(text=get_text(lang, "btn_change_lang"))]
        ],
        resize_keyboard=True
    )

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang_bn")]
    ])

def get_plan_kb(lang="en"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "plan_1"), callback_data="plan_1month_20")],
        [InlineKeyboardButton(text=get_text(lang, "plan_3"), callback_data="plan_3months_55")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_payment")]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="📞 Contact", callback_data=f"contact_{user_id}")]
    ])

# --- BOT SETUP ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# --- HANDLERS ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(language="en")
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    await message.answer("👋 Welcome! Please select your language:", reply_markup=get_lang_kb())

@router.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(language=lang_code)
    await callback.answer()
    msg = get_text(lang_code, "welcome", callback.from_user.first_name)
    await callback.message.answer(msg, reply_markup=get_main_kb(lang_code))

@router.message(F.text.in_(["🌐 Change Language", "🌐 भाषा बदलें", "🌐 ভাষা পরিবর্তন"]))
async def change_lang_btn(message: Message):
    await message.answer("Select Language:", reply_markup=get_lang_kb())

# --- Help Handler ---
@router.message(F.text.in_(["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]))
async def help_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await message.answer(get_text(lang, "help_text"))

# --- Status Handler ---
@router.message(F.text.in_(["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]))
async def status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    current_state = await state.get_state()
    
    if current_state == BotStates.pending_approval.state:
        status_msg = get_text(lang, "status_pending")
    elif current_state in [BotStates.timer_running.state, BotStates.waiting_for_screenshot.state]:
        status_msg = get_text(lang, "status_paying")
    else:
        status_msg = get_text(lang, "status_free")
        
    await message.answer(f"👤 <b>User:</b> {message.from_user.full_name}\n🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n\n{status_msg}")

@router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium"]))
async def premium_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await state.set_state(BotStates.waiting_for_plan_selection)
    await message.answer(get_text(lang, "select_plan"), reply_markup=get_plan_kb(lang))

@router.callback_query(F.data == "cancel_payment")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await state.clear()
    await state.update_data(language=lang)
    await callback.message.edit_text(get_text(lang, "cancelled"))

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer("⏳ Generating QR...")
    data = await state.get_data()
    lang = data.get("language", "en")
    
    plans = {
        "plan_1month_20": ("1 Month", 20),
        "plan_3months_55": ("3 Months", 55)
    }
    
    if callback.data not in plans: return
    plan_name, amount = plans[callback.data]
    
    qr_buffer = generate_qr(plan_name, amount)
    qr_file = BufferedInputFile(qr_buffer.read(), filename="qr.png")
    
    await state.update_data(plan_name=plan_name, amount=amount)
    await state.set_state(BotStates.timer_running)
    
    caption = get_text(lang, "payment_instr", plan_name, amount)
    await callback.message.answer_photo(
        photo=qr_file,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📤 Upload Screenshot", callback_data="upload_now")
        ]])
    )
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state))

@router.callback_query(F.data == "upload_now")
async def ask_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_prompt"))

@router.message(StateFilter(BotStates.timer_running, BotStates.waiting_for_screenshot), F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    plan = data.get("plan_name", "Unknown")
    amount = data.get("amount", 0)
    
    await message.answer(get_text(lang, "screenshot_received"))
    await state.set_state(BotStates.pending_approval)
    
    admin_text = (
        f"🔔 <b>NEW PAYMENT</b>\n\n"
        f"👤 User: {message.from_user.full_name} (ID: {message.from_user.id})\n"
        f"📦 Plan: {plan}\n💰 Amount: ₹{amount}"
    )
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=get_admin_kb(message.from_user.id)
        )
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")

# --- ADMIN HANDLERS ---
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
        
    action, user_id = callback.data.split("_")
    user_id = int(user_id)
    
    # Simple Bilingual Notification
    if action == "approve":
        await bot.send_message(user_id, TRANSLATIONS["en"]["approved"])
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ APPROVED")
    else:
        await bot.send_message(user_id, TRANSLATIONS["en"]["rejected"])
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ REJECTED")
    await callback.answer("Done!")

@router.callback_query(F.data.startswith("contact_"))
async def admin_contact(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.answer(f"Click to chat: tg://user?id={user_id}")
    await callback.answer()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👨‍💼 Admin Panel Active. Wait for incoming payments.")

# --- WEB SERVER ---
async def health_check(request):
    return web.Response(text="Bot is running! 🚀")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server started on port {port}")

# --- MAIN ---
async def main():
    logger.info("Starting bot...")
    await start_web_server()
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")


