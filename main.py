import asyncio
import logging
import os
import sys
from io import BytesIO

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
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ Help",
        "btn_status": "📊 My Status",
        "btn_change_lang": "🌐 Change Language",
        "welcome": "👋 <b>Welcome, {}!</b>\n\n🎥 Get <b>YouTube Premium</b> at affordable prices!",
        "select_plan": "🎥 <b>Choose Your Plan</b>\n\n👇 Select a plan to generate payment QR:",
        "plan_1": "1 Month - ₹20",
        "plan_3": "3 Months - ₹55",
        "payment_instr": "🎥 <b>Payment Details</b>\n\n📦 Plan: <b>{}</b>\n💰 Amount: <b>₹{}</b>\n\n📱 <b>Scan QR to Pay</b>\n⏰ You have <b>5 minutes</b> to upload a screenshot.",
        "upload_prompt": "📸 <b>Upload Screenshot Now</b>\n\nPlease send the payment screenshot photo.",
        "timer_ended": "⏰ <b>Time Expired!</b>\n\nPlease start the process again.",
        "screenshot_received": "✅ <b>Screenshot Received!</b>\n\nAdmin will review it shortly.",
        "approved": "🎉 <b>APPROVED!</b>\n\nYour YouTube Premium is now active!",
        "rejected": "❌ <b>REJECTED</b>\n\nYour payment could not be verified.",
        "cancelled": "❌ Operation cancelled.",
        "help_text": "📚 <b>Help</b>\n\n1. Select a Plan\n2. Scan QR Code\n3. Upload Screenshot\n4. Wait for Approval\n\nNeed support? Contact admin.",
        "status_free": "📍 Status: <b>Free User</b>\n❌ Premium: Inactive",
        "status_pending": "📍 Status: <b>Pending Approval</b>\n⏳ Please wait for admin.",
        "status_paying": "📍 Status: <b>Payment in Progress</b>\n⏳ Complete payment now!",
    },
    "hi": {
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ मदद",
        "btn_status": "📊 मेरी स्थिति",
        "btn_change_lang": "🌐 भाषा बदलें",
        "welcome": "👋 <b>स्वागत है, {}!</b>\n\n🎥 <b>YouTube Premium</b> किफायती दामों पर प्राप्त करें!",
        "select_plan": "🎥 <b>अपना प्लान चुनें</b>\n\n👇 भुगतान QR प्राप्त करने के लिए प्लान चुनें:",
        "plan_1": "1 महीना - ₹20",
        "plan_3": "3 महीने - ₹55",
        "payment_instr": "🎥 <b>भुगतान विवरण</b>\n\n📦 प्लान: <b>{}</b>\n💰 राशि: <b>₹{}</b>\n\n📱 <b>QR स्कैन करें</b>\n⏰ आपके पास स्क्रीनशॉट अपलोड करने के लिए <b>5 मिनट</b> हैं।",
        "upload_prompt": "📸 <b>अभी स्क्रीनशॉट अपलोड करें</b>\n\nकृपया भुगतान का फोटो भेजें।",
        "timer_ended": "⏰ <b>समय समाप्त!</b>\n\nकृपया प्रक्रिया पुनः आरंभ करें।",
        "screenshot_received": "✅ <b>स्क्रीनशॉट प्राप्त हुआ!</b>\n\nएडमिन जल्द ही इसकी समीक्षा करेंगे।",
        "approved": "🎉 <b>स्वीकृत!</b>\n\nआपका YouTube Premium अब सक्रिय है!",
        "rejected": "❌ <b>अस्वीकृत</b>\n\nआपके भुगतान का सत्यापन नहीं हो सका।",
        "cancelled": "❌ प्रक्रिया रद्द कर दी गई।",
        "help_text": "📚 <b>मदद</b>\n\n1. प्लान चुनें\n2. QR कोड स्कैन करें\n3. स्क्रीनशॉट अपलोड करें\n4. स्वीकृति की प्रतीक्षा करें",
        "status_free": "📍 स्थिति: <b>फ्री यूजर</b>\n❌ प्रीमियम: निष्क्रिय",
        "status_pending": "📍 स्थिति: <b>स्वीकृति लंबित</b>\n⏳ कृपया प्रतीक्षा करें।",
        "status_paying": "📍 स्थिति: <b>भुगतान जारी है</b>\n⏳ अभी भुगतान पूरा करें!",
    },
    "bn": {
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ সাহায্য",
        "btn_status": "📊 আমার স্ট্যাটাস",
        "btn_change_lang": "🌐 ভাষা পরিবর্তন",
        "welcome": "👋 <b>স্বাগতম, {}!</b>\n\n🎥 সাশ্রয়ী মূল্যে <b>YouTube Premium</b> পান!",
        "select_plan": "🎥 <b>আপনার প্ল্যান বেছে নিন</b>\n\n👇 পেমেন্ট QR পেতে একটি প্ল্যান সিলেক্ট করুন:",
        "plan_1": "১ মাস - ₹20",
        "plan_3": "৩ মাস - ₹55",
        "payment_instr": "🎥 <b>পেমেন্ট বিবরণ</b>\n\n📦 প্ল্যান: <b>{}</b>\n💰 পরিমাণ: <b>₹{}</b>\n\n📱 <b>QR স্ক্যান করুন</b>\n⏰ স্ক্রিনশট আপলোড করার জন্য আপনার কাছে <b>৫ মিনিট</b> সময় আছে।",
        "upload_prompt": "📸 <b>এখনই স্ক্রিনশট আপলোড করুন</b>\n\nঅনুগ্রহ করে পেমেন্টের ছবি পাঠান।",
        "timer_ended": "⏰ <b>সময় শেষ!</b>\n\nঅনুগ্রহ করে আবার শুরু করুন।",
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


