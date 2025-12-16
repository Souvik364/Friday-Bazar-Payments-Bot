from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
import asyncio

start_router = Router()


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard with options."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 YouTube Premium")],
            [KeyboardButton(text="ℹ️ Help"), KeyboardButton(text="📊 My Status")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an option..."
    )
    return keyboard


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command and show main menu with animation."""
    await state.clear()
    
    await message.answer("⚡")
    await asyncio.sleep(0.3)
    
    await message.answer(
        f"👋 <b>Welcome to YouTube Premium Bot, {message.from_user.first_name}!</b>\n\n"
        "🎥 Get <b>YouTube Premium + YouTube Music</b> at affordable prices!\n\n"
        "✨ <b>What you get:</b>\n"
        "• 🚫 <b>Ad-Free Videos</b> - No interruptions\n"
        "• 🎵 <b>YouTube Music Premium</b> - Unlimited music\n"
        "• 📥 <b>Download Videos</b> - Watch offline anytime\n"
        "• 📱 <b>Background Play</b> - Listen with screen off\n"
        "• 🎬 <b>YouTube Originals</b> - Exclusive content\n"
        "• 🎶 <b>High Quality Audio</b> - Premium sound\n\n"
        "💡 <i>Click the button below to view our premium plans!</i>",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@start_router.message(Command("help"))
@start_router.message(F.text == "ℹ️ Help")
async def cmd_help(message: Message):
    """Show help information."""
    await message.answer(
        "📚 <b>YouTube Premium Bot - Help</b>\n\n"
        "🔹 <b>/start</b> - Return to main menu\n"
        "🔹 <b>/help</b> - Show this help message\n"
        "🔹 <b>/cancel</b> - Cancel current operation\n"
        "🔹 <b>/status</b> - Check your subscription status\n\n"
        "🎥 <b>YouTube Premium Features:</b>\n"
        "• No ads across YouTube\n"
        "• YouTube Music Premium included\n"
        "• Download videos & music\n"
        "• Background playback\n"
        "• YouTube Originals\n\n"
        "💳 <b>Payment Process:</b>\n"
        "1. Select a plan\n"
        "2. View QR code\n"
        "3. Make payment\n"
        "4. Upload screenshot (anytime within 5 mins)\n"
        "5. Wait for admin approval\n"
        "6. Get your YouTube Premium access!\n\n"
        "❓ <b>Need help?</b> Contact admin for support!",
        parse_mode="HTML"
    )


@start_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation."""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "✅ No active operation to cancel.\n\n"
            "Use /start to return to main menu.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await state.clear()
        await message.answer(
            "❌ <b>Operation Cancelled</b>\n\n"
            "Your current process has been cancelled.\n"
            "Use /start to begin again.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )


@start_router.message(Command("status"))
@start_router.message(F.text == "📊 My Status")
async def cmd_status(message: Message, state: FSMContext):
    """Show user status."""
    current_state = await state.get_state()
    user_data = await state.get_data()
    
    await message.answer("⏳ <i>Checking your status...</i>", parse_mode="HTML")
    await asyncio.sleep(0.5)
    
    status_text = "📊 <b>Your Status</b>\n\n"
    status_text += f"👤 Name: {message.from_user.first_name}\n"
    status_text += f"🆔 User ID: <code>{message.from_user.id}</code>\n\n"
    
    if current_state:
        plan_name = user_data.get('plan_name', 'N/A')
        amount = user_data.get('amount', 'N/A')
        
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
