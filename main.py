
import asyncio
import logging
import os
import sys
import functools
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
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
)
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
# Set logging to stdout to see real-time logs in Render console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load Env Vars with fallbacks to prevent immediate crashing
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
SUPPORT_BOT = os.getenv("SUPPORT_BOT", "@YourSupportBot").strip()
UPI_ID = os.getenv("UPI_ID", "").strip()

# --- VALIDATION ---
if not BOT_TOKEN:
    logger.critical("❌ BOT_TOKEN is missing! Add it to Render Environment Variables.")
    sys.exit(1)

# Convert ADMIN_ID to int safely
try:
    if ADMIN_ID:
        ADMIN_ID = int(ADMIN_ID)
    else:
        logger.critical("❌ ADMIN_ID is missing!")
        sys.exit(1)
except ValueError:
    logger.critical("❌ ADMIN_ID must be a number!")
    sys.exit(1)

# --- TRANSLATIONS (COMPACT) ---
TRANSLATIONS = {
    "en": {
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ Help",
        "btn_status": "📊 Status",
        "btn_support": "💬 Support",
        "btn_change_lang": "🌐 Language",
        "welcome": "👋 <b>Hi, {}!</b>\n\n🎥 Get <b>YouTube Premium</b> cheap!\n❌ No Ads\n🎵 Music Included",
        "choose_plan": "🎥 <b>Choose Plan</b>\n🎯 Includes Music Premium!",
        "plan_1": "1 Month - ₹20",
        "plan_3": "3 Months - ₹55",
        "payment_instr": "🎥 <b>Payment</b>\n📦 Plan: <b>{}</b>\n💰 Pay: <b>₹{}</b>\n\n📱 <b>Scan QR to Pay</b>\n⏰ Time: <b>5 mins</b>\n✅ <b>Upload screenshot NOW!</b>",
        "upload_prompt": "📸 <b>Send Screenshot</b>\n\nPlease upload payment photo.",
        "timer_ended": "⏰ <b>Expired!</b>\nPlease start again.",
        "screenshot_received": "✅ <b>Received!</b>\nWait for approval.",
        "approved": "🎉 <b>APPROVED!</b>\nYour Premium is ACTIVE!",
        "rejected": "❌ <b>Rejected</b>\nContact support.",
        "support_text": "💬 <b>Support</b>\nContact: {}\nID: <code>{}</code>",
        "status_msg": "📍 Status: <b>{}</b>\n💎 Plan: {}\n💰 Amount: ₹{}",
        "status_free": "Free User",
        "status_pending": "Pending",
        "status_paying": "Paying",
        "help_text": "📚 <b>How to buy:</b>\n1. Tap YouTube Premium\n2. Select Plan\n3. Scan QR\n4. Send Screenshot",
        "session_expired": "⚠️ <b>Session Expired</b>\nStart again."
    },
    "hi": {
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ मदद",
        "btn_status": "📊 स्थिति",
        "btn_support": "💬 सहायता",
        "btn_change_lang": "🌐 भाषा",
        "welcome": "👋 <b>नमस्ते, {}!</b>\n\n🎥 <b>YouTube Premium</b> सस्ते में पाएं!",
        "choose_plan": "🎥 <b>प्लान चुनें</b>",
        "plan_1": "1 महीना - ₹20",
        "plan_3": "3 महीने - ₹55",
        "payment_instr": "🎥 <b>भुगतान</b>\n📦 प्लान: <b>{}</b>\n💰 राशि: <b>₹{}</b>\n\n📱 <b>QR स्कैन करें</b>\n⏰ समय: <b>5 मिनट</b>\n✅ <b>स्क्रीनशॉट भेजें!</b>",
        "upload_prompt": "📸 <b>फोटो भेजें</b>\n\nभुगतान का स्क्रीनशॉट भेजें।",
        "timer_ended": "⏰ <b>समय समाप्त!</b>\nफिर से शुरू करें।",
        "screenshot_received": "✅ <b>प्राप्त हुआ!</b>\nइंतज़ार करें।",
        "approved": "🎉 <b>स्वीकृत!</b>\nPremium चालू है!",
        "rejected": "❌ <b>अस्वीकृत</b>\nसंपर्क करें।",
        "support_text": "💬 <b>सहायता</b>\nसंपर्क: {}\nID: <code>{}</code>",
        "status_msg": "📍 स्थिति: <b>{}</b>\n💎 प्लान: {}\n💰 राशि: ₹{}",
        "status_free": "फ्री यूजर",
        "status_pending": "लंबित",
        "status_paying": "भुगतान जारी",
        "help_text": "📚 <b>कैसे खरीदें:</b>\n1. प्रीमियम चुनें\n2. प्लान चुनें\n3. QR स्कैन करें\n4. फोटो भेजें",
        "session_expired": "⚠️ <b>सत्र समाप्त</b>\nफिर से शुरू करें।"
    },
    "bn": {
        "btn_premium": "🎥 YouTube Premium",
        "btn_help": "ℹ️ সাহায্য",
        "btn_status": "📊 স্ট্যাটাস",
        "btn_support": "💬 সাপোর্ট",
        "btn_change_lang": "🌐 ভাষা",
        "welcome": "👋 <b>স্বাগতম, {}!</b>\n\n🎥 সুলভ মূল্যে <b>YouTube Premium</b> পান!\n❌ বিজ্ঞাপন নেই\n🎵 মিউজিক অন্তর্ভুক্ত",
        "choose_plan": "🎥 <b>প্ল্যান বাছুন</b>\n🎯 মিউজিক প্রিমিয়াম অন্তর্ভুক্ত!",
        "plan_1": "১ মাস - ₹20",
        "plan_3": "৩ মাস - ₹55",
        "payment_instr": "🎥 <b>পেমেন্ট</b>\n📦 প্ল্যান: <b>{}</b>\n💰 পেমেন্ট: <b>₹{}</b>\n\n📱 <b>QR স্ক্যান করুন</b>\n⏰ সময়: <b>৫ মিনিট</b>\n✅ <b>এখনই স্ক্রিনশট আপলোড করুন!</b>",
        "upload_prompt": "📸 <b>স্ক্রিনশট পাঠান</b>\n\nঅনুগ্রহ করে পেমেন্টের ছবি আপলোড করুন।",
        "timer_ended": "⏰ <b>সময় শেষ!</b>\nঅনুগ্রহ করে আবার শুরু করুন।",
        "screenshot_received": "✅ <b>প্রাপ্ত হয়েছে!</b>\nঅনুমোদনের জন্য অপেক্ষা করুন।",
        "approved": "🎉 <b>অনুমোদিত!</b>\nআপনার প্রিমিয়াম এখন সক্রিয়!",
        "rejected": "❌ <b>প্রত্যাখ্যাত</b>\nসাপোর্টে যোগাযোগ করুন।",
        "support_text": "💬 <b>সাপোর্ট</b>\nযোগাযোগ: {}\nID: <code>{}</code>",
        "status_msg": "📍 স্ট্যাটাস: <b>{}</b>\n💎 প্ল্যান: {}\n💰 পরিমাণ: ₹{}",
        "status_free": "ফ্রি ইউজার",
        "status_pending": "অপেক্ষমান",
        "status_paying": "পেমেন্ট চলছে",
        "help_text": "📚 <b>কিভাবে কিনবেন:</b>\n১. YouTube Premium এ ট্যাপ করুন\n২. প্ল্যান নির্বাচন করুন\n৩. QR স্ক্যান করুন\n৪. স্ক্রিনশট পাঠান",
        "session_expired": "⚠️ <b>সেশন শেষ</b>\nআবার শুরু করুন।"
    }
}

# --- STATES ---
class BotStates(StatesGroup):
    waiting_for_plan_selection = State()
    timer_running = State()
    waiting_for_screenshot = State()
    pending_approval = State()

# --- UTILS & HELPERS ---
def get_text(lang, key, *args):
    lang = lang if lang in TRANSLATIONS else "en"
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    if args:
        try: return text.format(*args)
        except: return text
    return text

# CPU-Bound Task: Moved to function to be run in executor
def generate_qr_sync(plan_name, amount, upi_id):
    upi = upi_id if upi_id else "example@upi"
    safe_plan = plan_name.replace(" ", "%20")
    qr_data = f"upi://pay?pa={upi}&pn=PremiumBot&am={amount}&tn={safe_plan}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

async def generate_qr_async(plan_name, amount):
    """Generates QR code in a separate thread to keep bot responsive."""
    loop = asyncio.get_running_loop()
    # Run the synchronous image generation in a thread pool
    result = await loop.run_in_executor(
        None, functools.partial(generate_qr_sync, plan_name, amount, UPI_ID)
    )
    return result

async def start_payment_timer(bot, chat_id, state, duration=300):
    """Background timer task."""
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        # Only act if user is still in the payment process
        if current_state in [BotStates.timer_running.state, BotStates.waiting_for_screenshot.state]:
            data = await state.get_data()
            lang = data.get("language", "en")
            # Clear state to reset user
            await state.clear()
            await state.update_data(language=lang)
            try: 
                await bot.send_message(chat_id, get_text(lang, "timer_ended"))
            except: 
                pass 
    except asyncio.CancelledError: 
        pass

# --- KEYBOARDS ---
def get_main_kb(lang="en"):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=get_text(lang, "btn_premium"))],
        [KeyboardButton(text=get_text(lang, "btn_help")), KeyboardButton(text=get_text(lang, "btn_status"))],
        [KeyboardButton(text=get_text(lang, "btn_support")), KeyboardButton(text=get_text(lang, "btn_change_lang"))]
    ], resize_keyboard=True)

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
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="cancel_payment")]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")]
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
    if not lang:
        await message.answer("🌐 <b>Select Language / भाषा चुनें / ভাষা নির্বাচন করুন</b>", reply_markup=get_lang_kb())
        return
    await state.clear()
    await state.update_data(language=lang)
    await message.answer(get_text(lang, "welcome", message.from_user.first_name), reply_markup=get_main_kb(lang))

@router.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(language=lang_code)
    await callback.answer()
    await callback.message.answer(get_text(lang_code, "welcome", callback.from_user.first_name), reply_markup=get_main_kb(lang_code))

@router.message(F.text.in_([t["btn_change_lang"] for t in TRANSLATIONS.values()]))
async def change_lang_btn(message: Message):
    await message.answer("🌐 Select Language:", reply_markup=get_lang_kb())

@router.message(F.text.in_([t["btn_support"] for t in TRANSLATIONS.values()]) | Command("support"))
async def support_handler(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language", "en")
    await message.answer(get_text(lang, "support_text", SUPPORT_BOT, message.from_user.id))

@router.message(F.text.in_([t["btn_premium"] for t in TRANSLATIONS.values()]))
async def premium_flow(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language", "en")
    await state.set_state(BotStates.waiting_for_plan_selection)
    await message.answer(get_text(lang, "choose_plan"), reply_markup=get_plan_kb(lang))

@router.callback_query(F.data == "cancel_payment")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("language", "en")
    await state.clear()
    await state.update_data(language=lang)
    await callback.message.edit_text("❌ Cancelled")

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Generating QR...")
    lang = (await state.get_data()).get("language", "en")
    plans = {
        "plan_1month_20": ("1 Month Premium", 20),
        "plan_3months_55": ("3 Months Premium", 55)
    }
    if callback.data not in plans: return
    plan_name, amount = plans[callback.data]
    
    # Run QR generation in executor to prevent lag
    qr_buffer = await generate_qr_async(plan_name, amount)
    qr_file = BufferedInputFile(qr_buffer.getvalue(), filename="qr.png")
    
    await state.update_data(plan_name=plan_name, amount=amount)
    await state.set_state(BotStates.timer_running)
    
    await callback.message.answer_photo(
        photo=qr_file,
        caption=get_text(lang, "payment_instr", plan_name, amount),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📤 Upload Screenshot", callback_data="upload_now")]])
    )
    # Start timer as a background task
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state))

@router.callback_query(F.data == "upload_now")
async def ask_upload(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("language", "en")
    await state.set_state(BotStates.waiting_for_screenshot)
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_prompt"))

@router.message(StateFilter(BotStates.timer_running, BotStates.waiting_for_screenshot), F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    lang, plan, amount = data.get("language", "en"), data.get("plan_name"), data.get("amount")
    
    # Restart protection
    if not plan:
        await message.answer(get_text(lang, "session_expired"))
        await state.clear()
        await state.update_data(language=lang)
        return

    await message.answer(get_text(lang, "screenshot_received"))
    await state.set_state(BotStates.pending_approval)
    
    admin_msg = f"🔔 <b>NEW PAYMENT</b>\n👤 User: {message.from_user.full_name}\nID: <code>{message.from_user.id}</code>\n📦 {plan}\n💰 ₹{amount}"
    try: await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_msg, reply_markup=get_admin_kb(message.from_user.id))
    except: logger.error("Failed to msg admin")

@router.message(F.text.in_([t["btn_status"] for t in TRANSLATIONS.values()]) | Command("status"))
async def status_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "en")
    st = await state.get_state()
    status = get_text(lang, "status_pending") if st == BotStates.pending_approval.state else get_text(lang, "status_free")
    await message.answer(get_text(lang, "status_msg", status, data.get("plan_name", "None"), data.get("amount", 0)))

@router.message(F.text.in_([t["btn_help"] for t in TRANSLATIONS.values()]) | Command("help"))
async def help_handler(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language", "en")
    await message.answer(get_text(lang, "help_text"))

# --- ADMIN ---
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    action, uid = callback.data.split("_")
    
    msg = TRANSLATIONS["en"]["approved"] if action == "approve" else TRANSLATIONS["en"]["rejected"]
    tag = "✅ APPROVED" if action == "approve" else "❌ REJECTED"
    
    try: await bot.send_message(int(uid), msg)
    except: pass
    
    try: await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n{tag}", reply_markup=None)
    except: pass
    await callback.answer()

# --- WEB SERVER (REQUIRED FOR RENDER) ---
async def health_check(request):
    """Simple health check to keep Render happy."""
    return web.Response(text="Bot is running! 🚀")

async def main():
    logger.info("🤖 Starting bot...")

    # 1. Start Web Server (Keep-alive for Render)
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    # Render provides PORT, default to 10000 locally
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    # 0.0.0.0 is CRITICAL for Render
    await web.TCPSite(runner, "0.0.0.0", port).start()
    logger.info(f"✅ Web server started on port {port}")

    # 2. Start Bot Polling
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user.")
