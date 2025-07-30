"""Telegram message handlers for processing user interactions."""

from typing import Dict, Any, List, Optional
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
import logging
from datetime import datetime
import asyncio

from src.utils.config import settings
from src.database.models import User, Conversation, Message
from src.translations.i18n import TranslationManager
from .keyboards import KeyboardBuilder

logger = logging.getLogger(__name__)


class TelegramMessageHandler:
    """
    Main handler for processing Telegram messages and interactions.
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize the message handler.
        
        Args:
            agents: Dictionary of initialized agents
        """
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.agents = agents
        self.translator = TranslationManager()
        self.keyboard_builder = KeyboardBuilder()
        
    async def handle_message(self, message_data: Dict[str, Any]) -> None:
        """
        Main entry point for handling messages.
        
        Args:
            message_data: Extracted message data from webhook
        """
        try:
            # Determine message type and route accordingly
            if message_data["message_type"] == "callback":
                await self._handle_callback_query(message_data)
            else:
                await self._handle_text_message(message_data)
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self._send_error_message(message_data["chat_id"], message_data.get("language_code", "en"))
    
    async def _handle_text_message(self, message_data: Dict[str, Any]) -> None:
        """
        Handle regular text messages.
        
        Args:
            message_data: Message data dictionary
        """
        chat_id = message_data["chat_id"]
        text = message_data["text"]
        user_id = message_data["user_id"]
        language_code = self._detect_user_language(message_data)
        
        # Handle commands
        if text.startswith("/"):
            await self._handle_command(message_data)
            return
        
        # Show typing indicator
        await self.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Get or create user
        user = await self._get_or_create_user(message_data)
        
        # Create or get conversation
        conversation = await self._get_or_create_conversation(user_id, chat_id)
        
        # Store user message
        await self._store_message(conversation.id, text, "user", message_data)
        
        # Process with orchestrator agent
        # Get response from orchestrator (which will coordinate all agents)
        response = await self.agents["orchestrator"].process(text)
        
        # Format and send response
        formatted_response = await self._format_agent_response(response, language_code)
        
        # Send response with appropriate keyboard
        keyboard = self._get_context_keyboard(response.get("metadata", {}), language_code)
        
        sent_message = await self.bot.send_message(
            chat_id=chat_id,
            text=formatted_response,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
        # Store bot response
        await self._store_message(
            conversation.id, 
            formatted_response, 
            "assistant", 
            {"message_id": sent_message.message_id}
        )
    
    async def _handle_command(self, message_data: Dict[str, Any]) -> None:
        """
        Handle bot commands (e.g., /start, /help, etc.).
        
        Args:
            message_data: Message data dictionary
        """
        command = message_data["text"].split()[0].lower()
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        if command == "/start":
            await self._handle_start_command(message_data)
        elif command == "/help":
            await self._handle_help_command(message_data)
        elif command == "/language":
            await self._handle_language_command(message_data)
        elif command == "/procedures":
            await self._handle_procedures_command(message_data)
        elif command == "/clinics":
            await self._handle_clinics_command(message_data)
        elif command == "/about":
            await self._handle_about_command(message_data)
        else:
            # Unknown command
            text = self.translator.translate("unknown_command", language_code)
            await self.bot.send_message(chat_id=chat_id, text=text)
    
    async def _handle_start_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /start command."""
        chat_id = message_data["chat_id"]
        user_name = message_data.get("first_name", "")
        language_code = self._detect_user_language(message_data)
        
        # Create or update user
        user = await self._get_or_create_user(message_data)
        
        # Prepare welcome message
        welcome_text = self.translator.translate(
            "welcome_message",
            language_code,
            name=user_name
        )
        
        # Create main menu keyboard
        keyboard = self.keyboard_builder.create_main_menu(language_code)
        
        # Send welcome message
        await self.bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
        # Send follow-up with quick actions
        follow_up_text = self.translator.translate("start_follow_up", language_code)
        quick_actions = self.keyboard_builder.create_quick_actions(language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=follow_up_text,
            reply_markup=quick_actions
        )
    
    async def _handle_help_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /help command."""
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        help_text = self.translator.translate("help_message", language_code)
        help_keyboard = self.keyboard_builder.create_help_menu(language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=help_keyboard
        )
    
    async def _handle_language_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /language command."""
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        text = self.translator.translate("choose_language", language_code)
        keyboard = self.keyboard_builder.create_language_selection()
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_procedures_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /procedures command."""
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        text = self.translator.translate("procedures_menu", language_code)
        keyboard = self.keyboard_builder.create_procedures_menu(language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def _handle_clinics_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /clinics command."""
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        # Use medical expert agent to get clinic recommendations
        response = await self.agents["medical_expert"].find_suitable_clinics({})
        
        # Format clinic information
        text = self._format_clinic_list(response, language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_about_command(self, message_data: Dict[str, Any]) -> None:
        """Handle /about command."""
        chat_id = message_data["chat_id"]
        language_code = self._detect_user_language(message_data)
        
        about_text = self.translator.translate("about_message", language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=about_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_callback_query(self, message_data: Dict[str, Any]) -> None:
        """
        Handle callback queries from inline keyboards.
        
        Args:
            message_data: Callback query data
        """
        callback_query_id = message_data["callback_query_id"]
        callback_data = message_data["callback_data"]
        chat_id = message_data["chat_id"]
        message_id = message_data["message_id"]
        language_code = self._detect_user_language(message_data)
        
        try:
            # Answer callback query to remove loading state
            await self.bot.answer_callback_query(callback_query_id)
            
            # Process callback data
            if callback_data.startswith("lang_"):
                # Language selection
                new_language = callback_data.split("_")[1]
                await self._update_user_language(message_data["user_id"], new_language)
                
                text = self.translator.translate("language_updated", new_language)
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text
                )
                
            elif callback_data.startswith("procedure_"):
                # Procedure information request
                procedure = callback_data.split("_", 1)[1]
                await self._show_procedure_info(chat_id, message_id, procedure, language_code)
                
            elif callback_data.startswith("clinic_"):
                # Clinic information request
                clinic_id = callback_data.split("_", 1)[1]
                await self._show_clinic_info(chat_id, message_id, clinic_id, language_code)
                
            elif callback_data == "main_menu":
                # Return to main menu
                text = self.translator.translate("main_menu", language_code)
                keyboard = self.keyboard_builder.create_main_menu(language_code)
                
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=keyboard
                )
                
        except TelegramError as e:
            logger.error(f"Error handling callback query: {str(e)}")
    
    async def _show_procedure_info(self, chat_id: int, message_id: int, 
                                  procedure: str, language_code: str) -> None:
        """Show detailed procedure information."""
        # Get procedure info from medical expert
        response = await self.agents["medical_expert"].get_procedure_info(procedure)
        
        # Format response
        text = self._format_procedure_info(response, language_code)
        
        # Create back button
        keyboard = self.keyboard_builder.create_back_button("procedures", language_code)
        
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def _show_clinic_info(self, chat_id: int, message_id: int,
                               clinic_id: str, language_code: str) -> None:
        """Show detailed clinic information."""
        # This would fetch specific clinic details
        # For now, showing mock data
        text = self.translator.translate(
            "clinic_details",
            language_code,
            clinic_name=clinic_id
        )
        
        keyboard = self.keyboard_builder.create_back_button("clinics", language_code)
        
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    def _detect_user_language(self, message_data: Dict[str, Any]) -> str:
        """
        Detect user's preferred language.
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            Language code (ar, en, ko)
        """
        # Check if user has set preference (would check database)
        # For now, use Telegram language code
        tg_lang = message_data.get("language_code", "en")
        
        if tg_lang.startswith("ar"):
            return "ar"
        elif tg_lang.startswith("ko"):
            return "ko"
        else:
            return "en"
    
    def _get_context_keyboard(self, metadata: Dict[str, Any], 
                            language_code: str) -> Optional[Any]:
        """
        Get appropriate keyboard based on response context.
        
        Args:
            metadata: Response metadata
            language_code: User's language
            
        Returns:
            Inline keyboard or None
        """
        response_type = metadata.get("response_type", "")
        
        if response_type == "medical_consultation":
            return self.keyboard_builder.create_medical_actions(language_code)
        elif response_type == "review_analysis":
            return self.keyboard_builder.create_review_actions(language_code)
        elif response_type == "cultural_etiquette":
            return self.keyboard_builder.create_cultural_actions(language_code)
        else:
            return None
    
    async def _format_agent_response(self, response: Dict[str, Any], 
                                   language_code: str) -> str:
        """
        Format agent response for Telegram display.
        
        Args:
            response: Agent response dictionary
            language_code: User's language
            
        Returns:
            Formatted text for Telegram
        """
        # This would implement proper formatting based on response structure
        # For now, return the content as is
        return str(response.get("content", ""))
    
    def _format_procedure_info(self, info: Dict[str, Any], 
                             language_code: str) -> str:
        """Format procedure information for display."""
        # Implement proper formatting
        return str(info)
    
    def _format_clinic_list(self, clinics: List[Dict[str, Any]], 
                          language_code: str) -> str:
        """Format clinic list for display."""
        # Implement proper formatting
        return str(clinics)
    
    async def _send_error_message(self, chat_id: int, language_code: str) -> None:
        """Send error message to user."""
        error_text = self.translator.translate("error_message", language_code)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _get_or_create_user(self, message_data: Dict[str, Any]) -> User:
        """Get or create user in database."""
        # This would interact with actual database
        # Mock implementation for now
        return User(
            telegram_id=message_data["user_id"],
            username=message_data.get("username"),
            first_name=message_data.get("first_name"),
            last_name=message_data.get("last_name"),
            language_code=message_data.get("language_code", "en")
        )
    
    async def _get_or_create_conversation(self, user_id: int, 
                                        chat_id: int) -> Conversation:
        """Get or create conversation in database."""
        # Mock implementation
        return Conversation(
            id=1,
            user_id=user_id,
            chat_id=chat_id,
            created_at=datetime.now()
        )
    
    async def _store_message(self, conversation_id: int, content: str,
                           role: str, message_metadata: Dict[str, Any]) -> None:
        """Store message in database."""
        # This would store in actual database
        pass
    
    async def _update_user_language(self, user_id: int, language_code: str) -> None:
        """Update user's language preference."""
        # This would update in actual database
        pass