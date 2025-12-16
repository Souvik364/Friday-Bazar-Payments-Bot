import asyncio
import logging
import re  # Import regex for email validation
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ChatAction

from handlers import PremiumStates
from utils.qr_generator import generate_payment_qr
from utils.timer import start_payment_timer
from config import ADMIN_ID
from utils.translations import get_text
from handlers.language import get_user_language

logger = logging.getLogger(__name__)
premium_router = Router()

# --- KEYBOARDS ---

def get_plan_selection_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 Month - ₹20", callback_data="plan_1month_20")],
            [InlineKeyboardButton(text="3 Months - ₹55", callback_data="plan_3months_55")],
            [InlineKeyboardButton(text=get_text(lang, "coming_soon") + " 6 Months - ₹100", callback_data="coming_soon")],
            [InlineKeyboardButton(text=get_text(lang, "back_menu"), callback_data="back_to_menu")]
        ]
    )

def get_payment_actions_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "upload_now"), callback_data="upload_now")],
            [InlineKeyboardButton(text=get_text(lang, "cancel_payment"), callback_data="cancel_payment")]
        ]
    )

def get_admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")],
            [InlineKeyboardButton(text="📞 Contact User", callback_data=f"contact_{user_id}")]
        ]
    )

def get_final_success_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard for final success message with Contact Admin button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Contact Admin for Help", url=f"tg://user?id={ADMIN_ID}")]
        ]
    )

# --- PLAN SELECTION & PAYMENT FLOW ---

@premium_router.message(F.text.in_(["🎥 YouTube Premium", "🎥 YouTube Premium", "🎥 YouTube Premium"])) 
async def show_premium_plans(message: Message, state: FSMContext, bot: Bot):
    lang = await get_user_language(state)
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)
    await state.set_state(PremiumStates.waiting_for_plan_selection)
    
    await message.answer(
        get_text(lang, "choose_plan"),
        parse_mode="HTML",
        reply_markup=get_plan_selection_keyboard(lang)
    )

@premium_router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(state)
    await state.clear()
    from handlers.start import get_main_menu_keyboard
    await callback.message.answer(
        get_text(lang, "welcome", callback.from_user.first_name),
        reply_markup=get_main_menu_keyboard(lang)
    )

@premium_router.callback_query(F.data == "coming_soon")
async def handle_coming_soon(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(state)
    await callback.answer(get_text(lang, "coming_soon"), show_alert=True)

@premium_router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(state)
    await callback.answer("Cancelled")
    await state.set_state(PremiumStates.waiting_for_plan_selection)
    await callback.message.answer(
        get_text(lang, "choose_plan"),
        reply_markup=get_plan_selection_keyboard(lang)
    )

@premium_router.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    lang = await get_user_language(state)
    await callback.answer("⏳ Processing...")
    
    plan_mapping = {
        "plan_1month_20": ("1 Month", 20),
        "plan_3months_55": ("3 Months", 55)
    }
    
    if callback.data not in plan_mapping:
        return
    
    plan_name_short, amount = plan_mapping[callback.data]
    timer_end_time = datetime.now() + timedelta(minutes=5)
    
    await state.update_data(plan_name=plan_name_short, amount=amount, timer_end=timer_end_time.isoformat())
    await state.set_state(PremiumStates.viewing_qr)
    
    qr_buffer = generate_payment_qr(plan_name_short, amount)
    qr_photo = BufferedInputFile(qr_buffer.read(), filename="payment_qr.png")
    
    caption_text = get_text(lang, "payment_details", plan_name_short, amount, timer_end_time.strftime('%I:%M %p'))
    
    await callback.message.answer_photo(
        photo=qr_photo,
        caption=caption_text,
        parse_mode="HTML",
        reply_markup=get_payment_actions_keyboard(lang)
    )
    
    await callback.message.answer(get_text(lang, "timer_started"), parse_mode="HTML")
    asyncio.create_task(start_payment_timer(bot, callback.message.chat.id, state, duration=300))

@premium_router.callback_query(F.data == "upload_now")
async def prompt_upload(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(state)
    await callback.answer()
    await callback.message.answer(get_text(lang, "upload_now") + " 📸", parse_mode="HTML")

@premium_router.message(StateFilter(PremiumStates.timer_running, PremiumStates.waiting_for_screenshot), F.photo)
async def handle_payment_screenshot(message: Message, state: FSMContext, bot: Bot):
    lang = await get_user_language(state)
    user_data = await state.get_data()
    
    photo = message.photo[-1]
    await state.set_state(PremiumStates.pending_approval)
    
    await message.answer(get_text(lang, "screenshot_received"), parse_mode="HTML")
    
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    full_name = message.from_user.full_name
    plan = user_data.get("plan_name", "Unknown")
    amount = user_data.get("amount", 0)
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            caption=f"🔔 <b>NEW PAYMENT</b>\n👤 {full_name} (@{username})\n🆔 <code>{user_id}</code>\n📦 {plan} - ₹{amount}",
            parse_mode="HTML",
            reply_markup=get_admin_approval_keyboard(user_id)
        )
    except Exception as e:
        logger.error(f"Admin notify failed: {e}")

# --- EMAIL COLLECTION & FINALIZATION LOGIC ---

@premium_router.message(StateFilter(PremiumStates.waiting_for_email))
async def handle_email_input(message: Message, state: FSMContext, bot: Bot):
    """
    Validates email and sends final confirmation details.
    """
    email = message.text.strip()
    lang = await get_user_language(state)
    
    # Basic email regex validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        error_msg = "❌ <b>Invalid Email Format</b>\nPlease enter a valid email address (e.g., yourname@gmail.com)."
        await message.answer(error_msg, parse_mode="HTML")
        return

    # Valid email logic
    await state.update_data(user_email=email)
    
    # Notify User (Final Success)
    success_msg = (
        f"🎉 <b>Thank You!</b>\n\n"
        f"📧 Email recorded: <code>{email}</code>\n\n"
        f"✅ <b>Your Premium Plan is Active!</b>\n"
        f"We have sent the login details/activation link to your email.\n\n"
        f"❓ <i>For further enquiry or issues, please contact admin below.</i>"
    )
    
    await message.answer(
        success_msg,
        parse_mode="HTML",
        reply_markup=get_final_success_keyboard(lang)
    )
    
    # Notify Admin that email was collected
    user_data = await state.get_data()
    plan_name = user_data.get("plan_name", "Unknown")
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✅ <b>USER EMAIL RECEIVED</b>\n\n"
             f"👤 User: {message.from_user.full_name}\n"
             f"🆔 ID: <code>{message.from_user.id}</code>\n"
             f"📦 Plan: {plan_name}\n"
             f"📧 Email: <code>{email}</code>\n\n"
             f"<i>Please proceed with activation for this email.</i>",
        parse_mode="HTML"
    )
    
    await state.clear()
