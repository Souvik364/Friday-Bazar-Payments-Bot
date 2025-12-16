import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ChatAction

from config import ADMIN_ID

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
        await callback.answer("📞 Opening chat with user...")
        
        await callback.message.answer(
            f"📞 <b>Contact User</b>\n\n"
            f"User ID: <code>{user_id}</code>\n\n"
            f"Click to message: tg://user?id={user_id}\n\n"
            f"Or use /msg {user_id} your_message_here",
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
    
    await bot.send_chat_action(callback.message.chat.id, ChatAction.TYPING)
    await callback.answer("⏳ Processing...")
    await asyncio.sleep(0.3)
    
    try:
        if action == "approve":
            await bot.send_message(
                chat_id=user_id,
                text="🎉 <b>CONGRATULATIONS!</b> 🎉\n\n"
                     "✅ Your payment has been <b>APPROVED</b>!\n\n"
                     "🎥 <b>Your YouTube Premium is Now ACTIVE!</b>\n\n"
                     "🎁 <b>Features Unlocked:</b>\n"
                     "• ✅ Ad-free YouTube videos\n"
                     "• ✅ YouTube Music Premium\n"
                     "• ✅ Download videos & music\n"
                     "• ✅ Background playback\n"
                     "• ✅ YouTube Originals access\n\n"
                     "💡 Type /status to view your subscription details\n\n"
                     "🙏 <i>Thank you for choosing YouTube Premium!</i>",
                parse_mode="HTML"
            )
            
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n"
                        f"✅ <b>APPROVED</b> ✅\n"
                        f"By: Admin\n"
                        f"Time: {asyncio.get_event_loop().time()}",
                parse_mode="HTML",
                reply_markup=None
            )
            
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"✅ <b>Payment Approved Successfully</b>\n\n"
                     f"User ID: <code>{user_id}</code>\n"
                     f"User has been notified.",
                parse_mode="HTML"
            )
            
            await callback.answer("✅ Approved successfully!", show_alert=False)
            logger.info(f"Admin {ADMIN_ID} approved payment for user {user_id}")
            
        elif action == "reject":
            await bot.send_message(
                chat_id=user_id,
                text="❌ <b>Payment Verification Failed</b>\n\n"
                     "Unfortunately, your payment could not be verified.\n\n"
                     "📝 <b>Possible Reasons:</b>\n"
                     "• Incorrect payment amount\n"
                     "• Incomplete transaction details\n"
                     "• Payment not received\n\n"
                     "💡 <b>What to do next:</b>\n"
                     "• Double-check your payment\n"
                     "• Try again with correct details\n"
                     "• Contact support for help\n\n"
                     "📞 Need assistance? Use /help to contact support.",
                parse_mode="HTML"
            )
            
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n"
                        f"❌ <b>REJECTED</b> ❌\n"
                        f"By: Admin\n"
                        f"Time: {asyncio.get_event_loop().time()}",
                parse_mode="HTML",
                reply_markup=None
            )
            
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"❌ <b>Payment Rejected</b>\n\n"
                     f"User ID: <code>{user_id}</code>\n"
                     f"User has been notified.",
                parse_mode="HTML"
            )
            
            await callback.answer("❌ Rejected!", show_alert=False)
            logger.info(f"Admin {ADMIN_ID} rejected payment for user {user_id}")
        
        user_state = FSMContext(
            bot=bot,
            storage=state.storage,
            key=state.key.with_user_id(user_id)
        )
        await user_state.clear()
        
    except Exception as e:
        logger.error(f"Error processing admin decision: {e}", exc_info=True)
        
        error_msg = str(e).lower()
        if "bot was blocked" in error_msg:
            await callback.answer("⚠️ User has blocked the bot", show_alert=True)
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"⚠️ <b>Cannot notify user</b>\n\n"
                     f"User ID: <code>{user_id}</code>\n"
                     f"Reason: User blocked the bot",
                parse_mode="HTML"
            )
        elif "chat not found" in error_msg:
            await callback.answer("⚠️ User chat not found", show_alert=True)
        else:
            await callback.answer("❌ Error sending notification", show_alert=True)
        
        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n"
                    f"⚠️ <b>ACTION FAILED</b>\n"
                    f"Could not notify user: {e}",
            parse_mode="HTML",
            reply_markup=None
        )


@admin_router.message(Command("stats"))
async def admin_stats(message: Message):
    """Show bot statistics (admin only)."""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "📊 <b>BOT STATISTICS</b>\n\n"
        "👥 Total Users: <code>-</code>\n"
        "💎 Premium Users: <code>-</code>\n"
        "💰 Total Revenue: <code>₹-</code>\n"
        "⏳ Pending Payments: <code>-</code>\n\n"
        "📈 <i>Statistics tracking coming soon!</i>\n"
        "💡 <i>Add database integration for detailed stats.</i>",
        parse_mode="HTML"
    )
