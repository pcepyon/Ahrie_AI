"""Telegram webhook handler for receiving and processing messages."""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import hmac
import hashlib
from datetime import datetime

from src.bot.handlers import TelegramMessageHandler
from src.utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_telegram_webhook(request_data: bytes, signature: str) -> bool:
    """
    Verify Telegram webhook signature for security.
    
    Args:
        request_data: Raw request body
        signature: Telegram signature from headers
        
    Returns:
        True if signature is valid
    """
    secret = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    expected_signature = hmac.new(
        secret,
        request_data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Handle incoming Telegram webhook requests.
    
    Args:
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        
    Returns:
        JSON response acknowledging receipt
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature if in production
        if not settings.DEBUG:
            signature = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if not verify_telegram_webhook(body, signature):
                logger.warning("Invalid webhook signature received")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse update
        update = await request.json()
        
        # Log incoming update
        logger.info(f"Received Telegram update: {update.get('update_id', 'unknown')}")
        
        # Extract message data
        message_data = extract_message_data(update)
        
        if not message_data:
            logger.warning("No valid message data in update")
            return JSONResponse({"ok": True, "description": "No message to process"})
        
        # Process message in background
        background_tasks.add_task(
            process_telegram_message,
            message_data,
            request.app.state.agents
        )
        
        # Return immediate response to Telegram
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Don't expose internal errors to Telegram
        return JSONResponse({"ok": True, "description": "Error processed"})


def extract_message_data(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract relevant message data from Telegram update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Extracted message data or None
    """
    # Handle regular messages
    if "message" in update:
        message = update["message"]
        return {
            "update_id": update.get("update_id"),
            "message_id": message.get("message_id"),
            "chat_id": message["chat"]["id"],
            "user_id": message["from"]["id"],
            "username": message["from"].get("username", ""),
            "first_name": message["from"].get("first_name", ""),
            "last_name": message["from"].get("last_name", ""),
            "text": message.get("text", ""),
            "date": message.get("date"),
            "language_code": message["from"].get("language_code", "en"),
            "message_type": "text" if "text" in message else "other"
        }
    
    # Handle callback queries (button presses)
    elif "callback_query" in update:
        callback = update["callback_query"]
        return {
            "update_id": update.get("update_id"),
            "callback_query_id": callback.get("id"),
            "chat_id": callback["message"]["chat"]["id"],
            "user_id": callback["from"]["id"],
            "username": callback["from"].get("username", ""),
            "first_name": callback["from"].get("first_name", ""),
            "last_name": callback["from"].get("last_name", ""),
            "callback_data": callback.get("data", ""),
            "message_id": callback["message"].get("message_id"),
            "language_code": callback["from"].get("language_code", "en"),
            "message_type": "callback"
        }
    
    return None


async def process_telegram_message(
    message_data: Dict[str, Any],
    agents: Dict[str, Any]
) -> None:
    """
    Process Telegram message using the bot handler and agents.
    
    Args:
        message_data: Extracted message data
        agents: Dictionary of initialized agents
    """
    try:
        # Initialize message handler
        handler = TelegramMessageHandler(agents)
        
        # Process the message
        await handler.handle_message(message_data)
        
        logger.info(f"Successfully processed message from user {message_data['user_id']}")
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Could implement retry logic or error notification here


@router.post("/set")
async def set_webhook() -> Dict[str, Any]:
    """
    Endpoint to set Telegram webhook URL.
    
    This is typically called once during deployment or when changing webhook URL.
    """
    try:
        from telegram import Bot
        
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Construct webhook URL
        webhook_url = f"{settings.WEBHOOK_BASE_URL}/api/v1/webhook/telegram"
        
        # Set webhook with secret token
        result = await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        if result:
            logger.info(f"Webhook set successfully: {webhook_url}")
            return {
                "status": "success",
                "webhook_url": webhook_url,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise Exception("Failed to set webhook")
            
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set webhook: {str(e)}")


@router.delete("/delete")
async def delete_webhook() -> Dict[str, str]:
    """
    Delete the current Telegram webhook.
    
    Useful for development when switching between webhook and polling.
    """
    try:
        from telegram import Bot
        
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        result = await bot.delete_webhook(drop_pending_updates=True)
        
        if result:
            logger.info("Webhook deleted successfully")
            return {"status": "success", "message": "Webhook deleted"}
        else:
            raise Exception("Failed to delete webhook")
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")


@router.get("/info")
async def webhook_info() -> Dict[str, Any]:
    """
    Get current webhook information from Telegram.
    """
    try:
        from telegram import Bot
        
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        webhook_info = await bot.get_webhook_info()
        
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get webhook info: {str(e)}")