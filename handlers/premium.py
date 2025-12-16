import asyncio
import logging
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

logger = logging.getLogger(__name__)
premium_router = Router()


def get_plan_selection_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with plan options."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 Month - ₹20", callback_data="plan_1month_20")],
            [InlineKeyboardButton(text="3 Months - ₹55", callback_data="plan_3months_55")],
            [InlineKeyboardButton(text="🔜 6 Months - ₹100 (Coming Soon)", callback_data="coming_soon")],
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
        ]
    )
    return keyboard


def get_payment_actions_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for actions during payment."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Upload Screenshot Now", callback_data="upload_now")],
            [InlineKeyboardButton(text="🔙 Cancel & Go Back", callback_data="cancel_payment")]
        ]
    )
    return keyboard


def get_admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create admin approval keyboard with user ID embedded."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}")
            ],
            [InlineKeyboardButton(text="📞 Contact User", callback_data=f"contact_{user_id}")]
        ]
    )
    return keyboard


@premium_router.message(F.text == "🎥 YouTube Premium")
async def show_premium_plans(message: Message, state: FSMContext, bot: Bot):
    """Show YouTube Premium plan options with animation."""
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)
    
    await state.set_state(PremiumStates.waiting_for_plan_selection)
    
    await message.answer(
        "✨ <b>Loading YouTube Premium Plans...</b>",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.3)
    
    await message.answer(
        "🎥 <b>Choose Your YouTube Premium Plan</b>\n\n"
        "🎯 <b>Includes YouTube Music Premium!</b>\n\n"
        "🔹 <b>1 Month</b> - ₹20\n"
        "   • Ad-free videos\n"
        "   • Background play\n"
        "   • Download videos\n"
        "   • YouTube Music included\n\n"
        "🔹 <b>3 Months</b> - ₹55 🔥\n"
        "   • <i>Save ₹5! Most Popular!</i>\n"
        "   • All features for 3 months\n"
        "   • Best value for money\n\n"
        "🔜 <b>6 Months</b> - ₹100 (Coming Soon)\n"
        "   • <i>Save ₹20! Available soon!</i>\n\n"
        "💡 Click a button below to proceed:",
        parse_mode="HTML",
        reply_markup=get_plan_selection_keyboard()
    )


@premium_router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu."""
    await callback.answer("🔙 Returning to main menu...")
    await state.clear()
    
    from handlers.start import get_main_menu_keyboard
    
    await callback.message.answer(
        "🏠 <b>Main Menu</b>\n\n"
        "What would you like to do?",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@premium_router.callback_query(F.data == "coming_soon")
async def handle_coming_soon(callback: CallbackQuery):
    """Handle coming soon plan click."""
    await callback.answer(
        "🔜 6 Months plan coming soon! Stay tuned!",
        show_alert=True
    )
    
    await callback.message.answer(
        "🔜 <b>6 Months Plan - Coming Soon!</b>\n\n"
        "We're working on bringing you the 6-month plan at ₹100.\n\n"
        "📢 <b>You'll be notified when it's available!</b>\n\n"
        "Meanwhile, check out our other plans:\n"
        "• 1 Month - ₹20\n"
        "• 3 Months - ₹55 🔥\n\n"
        "💡 Choose from available plans below:",
        parse_mode="HTML",
        reply_markup=get_plan_selection_keyboard()
    )


@premium_router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment and return to plans."""
    await callback.answer("❌ Payment cancelled")
    await state.set_state(PremiumStates.waiting_for_plan_selection)
    
    await callback.message.answer(
        "❌ <b>Payment Cancelled</b>\n\n"
        "You can select a plan again anytime.\n"
        "No charges have been made.",
        parse_mode="HTML",
        reply_markup=get_plan_selection_keyboard()
    )


@premium_router.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle plan selection and show QR code with flexible upload."""
    await callback.answer("⏳ Processing...")
    
    await bot.send_chat_action(callback.message.chat.id, ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(0.5)
    
    callback_data = callback.data
    
    plan_mapping = {
        "plan_1month_20": ("1 Month YouTube Premium", 20),
        "plan_3months_55": ("3 Months YouTube Premium", 55)
    }
    
    if callback_data not in plan_mapping:
        await callback.message.answer("❌ Invalid plan selected.")
        return
    
    plan_name, amount = plan_mapping[callback_data]
    
    timer_end_time = datetime.now() + timedelta(minutes=5)
    
    await state.update_data(
        plan_name=plan_name,
        amount=amount,
        timer_end=timer_end_time.isoformat()
    )
    await state.set_state(PremiumStates.viewing_qr)
    
    qr_buffer = generate_payment_qr(plan_name, amount)
    qr_photo = BufferedInputFile(qr_buffer.read(), filename="payment_qr.png")
    
    await callback.message.answer_photo(
        photo=qr_photo,
        caption=f"🎥 <b>YouTube Premium Payment</b>\n\n"
                f"📦 Plan: <b>{plan_name}</b>\n"
                f"💰 Amount: <b>₹{amount}</b>\n\n"
                f"🎁 <b>Includes:</b>\n"
                f"• 🚫 Ad-free videos\n"
                f"• 🎵 YouTube Music Premium\n"
                f"• 📥 Download videos\n"
                f"• 📱 Background play\n\n"
                f"📱 <b>Scan this QR code to pay</b>\n\n"
                f"⏰ Timer: <b>5 minutes</b>\n"
                f"⏱️ Ends at: {timer_end_time.strftime('%I:%M %p')}\n\n"
                f"✅ <b>Upload screenshot anytime within 5 minutes!</b>\n"
                f"No need to wait - upload as soon as you complete payment.",
        parse_mode="HTML",
        reply_markup=get_payment_actions_keyboard()
    )
    
    await state.set_state(PremiumStates.timer_running)
    
    await callback.message.answer(
        "⏱️ <b>Timer Started!</b>\n\n"
        "🎯 You can upload your payment screenshot <b>anytime</b> within the next 5 minutes.\n\n"
        "📸 <b>Just send the photo directly</b> or click 'Upload Screenshot Now' button.\n\n"
        "💡 <i>Tip: Upload immediately after payment to get YouTube Premium faster!</i>",
        parse_mode="HTML"
    )
    
    asyncio.create_task(
        start_payment_timer(bot, callback.message.chat.id, state, duration=300)
    )
    
    logger.info(f"User {callback.from_user.id} selected plan: {plan_name} (₹{amount})")


@premium_router.callback_query(F.data == "upload_now")
async def prompt_upload(callback: CallbackQuery):
    """Prompt user to upload screenshot."""
    await callback.answer("📸 Send your payment screenshot now!")
    
    await callback.message.answer(
        "📸 <b>Upload Payment Screenshot</b>\n\n"
        "Please send your payment screenshot as a photo.\n\n"
        "✅ Make sure the screenshot shows:\n"
        "• Payment amount\n"
        "• Transaction ID\n"
        "• Payment date & time\n\n"
        "📤 <i>Send the photo now...</i>",
        parse_mode="HTML"
    )


@premium_router.message(
    StateFilter(PremiumStates.timer_running, PremiumStates.waiting_for_screenshot),
    F.photo
)
async def handle_payment_screenshot(message: Message, state: FSMContext, bot: Bot):
    """Handle payment screenshot submission (anytime within timer)."""
    user_data = await state.get_data()
    timer_end = user_data.get('timer_end')
    
    if timer_end:
        timer_end_dt = datetime.fromisoformat(timer_end)
        if datetime.now() > timer_end_dt:
            await message.answer(
                "⏰ <b>Time Expired!</b>\n\n"
                "The 5-minute timer has ended.\n"
                "Please start a new payment process.",
                parse_mode="HTML"
            )
            await state.clear()
            return
    
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.3)
    
    await message.answer("⏳ <i>Processing your screenshot...</i>", parse_mode="HTML")
    await asyncio.sleep(0.5)
    
    photo = message.photo[-1]
    photo_file_id = photo.file_id
    
    await state.update_data(screenshot_file_id=photo_file_id)
    await state.set_state(PremiumStates.pending_approval)
    
    await message.answer(
        "✅ <b>Screenshot Received!</b>\n\n"
        "🎉 Your payment screenshot has been submitted successfully!\n\n"
        "⏳ <b>Next Steps:</b>\n"
        "• Admin will review your payment\n"
        "• You'll be notified within a few minutes\n"
        "• Check /status anytime for updates\n\n"
        "💡 <i>Thank you for your patience!</i>",
        parse_mode="HTML"
    )
    
    plan_name = user_data.get("plan_name", "Unknown")
    amount = user_data.get("amount", 0)
    
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    first_name = message.from_user.first_name or "User"
    full_name = message.from_user.full_name or first_name
    
    admin_message = (
        f"🔔 <b>NEW PAYMENT SUBMISSION</b> 🔔\n\n"
        f"{'='*30}\n"
        f"👤 <b>USER INFO</b>\n"
        f"{'='*30}\n"
        f"📛 Name: <b>{full_name}</b>\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"👤 Username: @{username}\n\n"
        f"{'='*30}\n"
        f"💎 <b>PLAN DETAILS</b>\n"
        f"{'='*30}\n"
        f"📦 Plan: <b>{plan_name}</b>\n"
        f"💰 Amount: <b>₹{amount}</b>\n"
        f"📅 Submitted: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        f"👇 <i>Please review the payment screenshot below</i>"
    )
    
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="HTML"
        )
        
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption="📸 <b>Payment Screenshot</b>\n\n"
                    "Review and take action below ⬇️",
            parse_mode="HTML",
            reply_markup=get_admin_approval_keyboard(user_id)
        )
        
        logger.info(f"Payment screenshot from user {user_id} forwarded to admin {ADMIN_ID}")
        
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}", exc_info=True)
        await message.answer(
            "⚠️ <b>Error notifying admin</b>\n\n"
            "Please contact support directly or try again.",
            parse_mode="HTML"
        )


@premium_router.message(StateFilter(PremiumStates.timer_running, PremiumStates.waiting_for_screenshot))
async def handle_non_photo_during_payment(message: Message):
    """Handle non-photo messages during payment process."""
    await message.answer(
        "⚠️ <b>Please send a PHOTO</b>\n\n"
        "📸 Send your payment screenshot as an image.\n\n"
        "💡 <i>Make sure to send it as a photo, not a file.</i>",
        parse_mode="HTML"
    )


@premium_router.message(F.photo)
async def handle_unexpected_photo(message: Message, state: FSMContext):
    """Handle photos sent in unexpected states."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "⚠️ <b>No active payment process</b>\n\n"
            "Please select a premium plan first:\n"
            "Click the 💎 Premium Plan button to get started!",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "⚠️ <b>Unexpected photo</b>\n\n"
            "Please follow the payment process:\n\n"
            "1️⃣ Click 💎 Premium Plan\n"
            "2️⃣ Select a plan\n"
            "3️⃣ Make payment\n"
            "4️⃣ Upload screenshot within 5 mins\n\n"
            "Use /cancel to start over.",
            parse_mode="HTML"
    )
    
