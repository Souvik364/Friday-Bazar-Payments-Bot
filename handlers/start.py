import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

# Imports for Language System
# Assuming these exist in your project structure
from utils.translations import get_text, get_language_keyboard
from handlers.language import get_user_language

# Safe import for config
try:
    from config import SUPPORT_BOT
except ImportError:
    SUPPORT_BOT = "SupportAdmin"  # Fallback if config is missing

start_router = Router()

# --- CONSTANTS FOR FILTERS ---
# These should match the translations in your utils/translations.py
# It is better to define them here so filters don't get messy
HELP_TEXTS = ["ℹ️ Help", "ℹ️ मदद", "ℹ️ সাহায্য"]
STATUS_TEXTS = ["📊 My Status", "📊 मेरी स्थिति", "📊 আমার স্ট্যাটাস"]
SUPPORT_TEXTS = ["💬 Support", "💬 सहायता", "💬 সাপোর্ট"]

def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Create main menu keyboard with translated options."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "youtube_premium"))],
            [KeyboardButton(text=get_text(lang, "help")), KeyboardButton(text=get_text(lang, "my_status"))],
            [KeyboardButton(text=get_text(lang, "support")), KeyboardButton(text=get_text(lang, "change_language"))]
        ],
        resize_keyboard=True,
        input_field_placeholder=get_text(lang, "menu_placeholder", default="Choose an option...")
    )

@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command. 
    1. If new user (no language in state): Show Language Selection.
    2. If existing user: Show Main Menu.
    """
    # 1. Get current language and state data
    lang = await get_user_language(state)
    data = await state.get_data()
    
    # 2. Check if language is actually set in the FSM data
    # Note: get_user_language might return a default 'en' even if not in state
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

    # 3. Existing user logic
    # CRITICAL FIX: Use set_state(None) instead of clear(). 
    # clear() wipes the language data; set_state(None) only stops active forms/dialogs.
    await state.set_state(None) 
    
    # Aesthetic delay for "loading" feel
    msg = await message.answer("⚡")
    await asyncio.sleep(0.3)
    await msg.delete() # Clean up the loading emoji
    
    welcome_text = get_text(lang, "welcome", message.from_user.first_name)
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(lang)
    )

@start_router.message(Command("help"))
@start_router.message(F.text.in_(HELP_TEXTS))
async def cmd_help(message: Message, state: FSMContext):
    """Show help information."""
    lang = await get_user_language(state)
    help_text = get_text(lang, "help_message") # Changed key to 'help_message' to distinguish from button text
    
    # Fallback if specific help message key is missing, try generic 'help'
    if not help_text:
        help_text = get_text(lang, "help")
        
    await message.answer(help_text, parse_mode="HTML")

@start_router.message(Command("status"))
@start_router.message(F.text.in_(STATUS_TEXTS))
async def cmd_status(message: Message, state: FSMContext):
    """Show status."""
    lang = await get_user_language(state)
    status_header = get_text(lang, "my_status")
    
    await message.answer(f"<b>{status_header}</b>\n\nChecking database...", parse_mode="HTML")
    # Add your actual status checking logic here
    # ...

@start_router.message(Command("support"))
@start_router.message(F.text.in_(SUPPORT_TEXTS))
async def cmd_support(message: Message, state: FSMContext):
    """Show support contact."""
    lang = await get_user_language(state)
    
    # Pass defaults to get_text to prevent errors if arguments are missing in translation string
    support_msg = get_text(
        lang, 
        "support_text", 
        admin_user=SUPPORT_BOT, 
        user_id=message.from_user.id
    )
    await message.answer(support_msg, parse_mode="HTML")

@start_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancels current action but keeps language settings."""
    lang = await get_user_language(state)
    
    # CRITICAL FIX: Do not use state.clear() here, or the user loses their language setting.
    await state.set_state(None)
    
    cancel_text = get_text(lang, "cancelled", default="❌ Cancelled / रद्द किया गया")
    await message.answer(cancel_text, reply_markup=get_main_menu_keyboard(lang))
    
