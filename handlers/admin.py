
import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ChatAction

from config import ADMIN_ID
from utils.translations import get_text
from handlers.language import get_user_language

logger = logging.getLogger(__name__)
admin_router = Router()


@admin_router.message(Command("admin"))
async def admin_dashboard(message: Message):
    """Show admin dashboard (admin only)."""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "👨‍💼 <b>ADMIN DASHBOARD</b>\n\n"
        "🎛️ <b>Available Commands:</b>\n\n"
        "📊 /stats - View statistics\n"
        "👥 /users - User management\n"
        "💳 /pending - View pending payments\n"
        "📢 /broadcast - Send message to all users\n\n"
        "💡 <i>Manage your bot efficiently!</i>",
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data.startswith("contact_"))
async def contact_user(callback: CallbackQuery, bot: Bot):
    """Allow admin to contact user directly."""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Unauthorized!", show_alert=True)
        return
    
    user_id_str = callback.data.split("_", 1)[1]
    
    try:
        user_id = int(user_id_str)
        await callback.answer("📞 Opening chat...")
        
        await callback.message.answer(
            f"📞 <b>Contact User</b>\n\n"
            f"User ID: <code>{user_id}</code>\n\n"
            f"Click to message: <a href='tg://user?id={user_id}'>Message User</a>",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer("❌ Error", show_alert=True)
        logger.error(f"Error in contact_user: {e}")


@admin_router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def handle_admin_decision(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Handle admin approval or rejection with enhanced UX."""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Unauthorized access!", show_alert=True)
        return
    
    action, user_id_str = callback.data.split("_", 1)
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        await callback.answer("❌ Invalid user ID", show_alert=True)
        return
    
    # Get user state to determine language
    user_state = FSMContext(
        bot=bot,
        storage=state.storage,
        key=state.key.with_user_id(user_id)
    )
    lang = await get_user_language(user_state)
    
    await bot.send_chat_action(callback.message.chat.id, ChatAction.TYPING)
    await callback.answer("⏳ Processing...")
    
    try:
        if action == "approve":
            # Send Approved Message to User
            await bot.send_message(
                chat_id=user_id,
                text=get_text(lang, "approved"),
                parse_mode="HTML"
            )
            
            # Update Admin Message
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n"
                        f"✅ <b>APPROVED</b>\n"
                        f"By: Admin\n"
                        f"Time: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode="HTML",
                reply_markup=None
            )
            
            await bot.send_message(ADMIN_ID, f"✅ Approved User {user_id}")
            
        elif action == "reject":
            # Send Rejected Message to User
            await bot.send_message(
                chat_id=user_id,
                text=get_text(lang, "rejected"),
                parse_mode="HTML"
            )
            
            # Update Admin Message
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n"
                        f"❌ <b>REJECTED</b>\n"
                        f"By: Admin\n"
                        f"Time: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode="HTML",
                reply_markup=None
            )
            
            await bot.send_message(ADMIN_ID, f"❌ Rejected User {user_id}")
        
        # Clear User State
        await user_state.clear()
        # Restore language preference
        await user_state.update_data(language=lang)
        
    except Exception as e:
        logger.error(f"Error processing admin decision: {e}", exc_info=True)
        await callback.answer("❌ Error occurred (User might have blocked bot)", show_alert=True)
        
