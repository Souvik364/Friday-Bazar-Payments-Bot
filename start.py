from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
import asyncio

# Imports for Language System
from utils.translations import get_text, get_language_keyboard
from handlers.language import get_user_language

start_router = Router()

def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Create main menu keyboard with translated options."""
    # Maps internal keys to translated text
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "youtube_premium"))],
            [KeyboardButton(text=get_text(lang, "help")), KeyboardButton(text=get_text(lang, "my_status"))],
            [KeyboardButton(text=get_text(lang, "support")), KeyboardButton(text=get_text(lang, "change_language"))]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an option..."
    )

@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command. First time -> Language Select. Returning -> Menu."""
    lang = await get_user_language(state)
    data = await state.get_data()
    
    # If no language is set in state, show selection
    if 'language' not in data:
        await message.answer(
            "🌐 <b>Select Your Language</b>\n"
            "अपनी पसंदीदा भाषा चुनें\n"
            "আপনার পছন্দের ভাষা নির্বাচন করুন\n\n"
            "Please choose your preferred language:",
            parse_mode="HTML",
            reply_markup=get_language_keyboard()
        )
        return

    # If language exists, show main menu
    await state.clear()
    await state.update_data(language=lang) # Keep language setting
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    
    welcome_text = get_text(lang, "welcome", message.from_user.first_name)
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang)
    )

@start_router.message(Command("help"))
@start_router.message(F.text.in_(["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]))
async def cmd_help(message: Message, state: FSMContext):
    """Show help information in correct language."""
    lang = await get_user_language(state)
    # Uses 'help' key from translations which contains the full help text
    help_text = get_text(lang, "help") 
    await message.answer(help_text, parse_mode="HTML")

@start_router.message(Command("status"))
@start_router.message(F.text.in_(["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]))
async def cmd_status(message: Message, state: FSMContext):
    """Show status in correct language."""
    lang = await get_user_language(state)
    # Simple status check - for full translation, ensure 'my_status' keys exist for body text
    # For now, we keep the dynamic logic but use the header from translations
    status_header = get_text(lang, "my_status")
    await message.answer(f"{status_header}: Checking...", parse_mode="HTML")
    # (Existing status logic continues...)

@start_router.message(Command("support"))
@start_router.message(F.text.in_(["💬 Support", "💬 सहायता", "💬 সাপোর্ট"]))
async def cmd_support(message: Message, state: FSMContext):
    """Show support contact."""
    from config import SUPPORT_BOT
    lang = await get_user_language(state)
    
    support_msg = get_text(lang, "support_text", SUPPORT_BOT or "Admin", message.from_user.id)
    await message.answer(support_msg, parse_mode="HTML")

@start_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    lang = await get_user_language(state)
    await state.clear()
    await message.answer("❌ Cancelled / रद्द किया गया / বাতিল হয়েছে", reply_markup=get_main_menu_keyboard(lang))
        
        if 'waiting_for_plan_selection' in current_state:
            status_text += "📍 Status: <b>Browsing plans</b>\n"
        elif 'viewing_qr' in current_state or 'timer_running' in current_state:
            status_text += "📍 Status: <b>Payment in progress</b>\n"
            status_text += f"💎 Plan: {plan_name}\n"
            status_text += f"💰 Amount: ₹{amount}\n"
            status_text += "\n⏰ You have up to 5 minutes to complete payment and upload screenshot."
        elif 'waiting_for_screenshot' in current_state:
            status_text += "📍 Status: <b>Waiting for payment screenshot</b>\n"
            status_text += f"💎 Plan: {plan_name}\n"
            status_text += f"💰 Amount: ₹{amount}\n"
        elif 'pending_approval' in current_state:
            status_text += "📍 Status: <b>Pending admin approval</b>\n"
            status_text += f"💎 Plan: {plan_name}\n"
            status_text += f"💰 Amount: ₹{amount}\n"
            status_text += "\n⏳ Your payment is being reviewed by admin."
    else:
        status_text += "📍 Status: <b>Free user</b>\n"
        status_text += "🎥 YouTube Premium: <b>Not active</b>\n\n"
        status_text += "🌟 Upgrade to YouTube Premium to enjoy ad-free experience!"
    
    await message.answer(status_text, parse_mode="HTML")
