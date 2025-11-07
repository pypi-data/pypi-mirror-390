"""
Telegram notification system
Sends formatted notifications to multiple chat IDs
"""

import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.logger import logger
from config import settings


class TelegramNotifier:
    """Handles sending notifications via Telegram Bot API"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_ids = settings.get_chat_ids()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Send message to single chat ID
        
        Args:
            message: Message text (supports HTML formatting)
            chat_id: Target chat ID (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not chat_id and not self.chat_ids:
            logger.error("No chat IDs configured")
            return False
        
        target_id = chat_id or self.chat_ids[0]
        
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    'chat_id': target_id,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent to chat {target_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def broadcast_message(self, message: str, chat_ids: Optional[List[str]] = None) -> int:
        """
        Send message to multiple chat IDs
        
        Args:
            message: Message text
            chat_ids: List of chat IDs (uses configured if None)
            
        Returns:
            Number of successful sends
        """
        targets = chat_ids or self.chat_ids
        
        if not targets:
            logger.error("No chat IDs to broadcast to")
            return 0
        
        logger.info(f"Broadcasting to {len(targets)} chats")
        
        success_count = 0
        for chat_id in targets:
            if self.send_message(message, chat_id):
                success_count += 1
        
        logger.info(f"Broadcast complete: {success_count}/{len(targets)} successful")
        return success_count
    
    def notify_success(
        self,
        problem_title: str,
        problem_url: str,
        difficulty: str,
        runtime: Optional[str] = None,
        memory: Optional[str] = None
    ) -> int:
        """
        Send success notification
        
        Args:
            problem_title: Problem title
            problem_url: LeetCode problem URL
            difficulty: Problem difficulty
            runtime: Optional runtime stats
            memory: Optional memory stats
            
        Returns:
            Number of successful broadcasts
        """
        message = self._format_success_message(
            problem_title, problem_url, difficulty, runtime, memory
        )
        return self.broadcast_message(message)
    
    def notify_failure(
        self,
        problem_title: str,
        problem_url: str,
        error_message: str,
        step: str = "Unknown"
    ) -> int:
        """
        Send failure notification
        
        Args:
            problem_title: Problem title
            problem_url: LeetCode problem URL
            error_message: Error description
            step: Which step failed
            
        Returns:
            Number of successful broadcasts
        """
        message = self._format_failure_message(
            problem_title, problem_url, error_message, step
        )
        return self.broadcast_message(message)
    
    def notify_progress(self, message: str) -> int:
        """
        Send progress update
        
        Args:
            message: Progress message
            
        Returns:
            Number of successful broadcasts
        """
        formatted = f"🔄 <b>Progress Update</b>\n\n{message}\n\n⏰ {self._get_timestamp()}"
        return self.broadcast_message(formatted)
    
    def _format_success_message(
        self,
        title: str,
        url: str,
        difficulty: str,
        runtime: Optional[str],
        memory: Optional[str]
    ) -> str:
        """Format success notification message"""
        
        difficulty_emoji = {
            'Easy': '🟢',
            'Medium': '🟡',
            'Hard': '🔴'
        }.get(difficulty, '⚪')
        
        message_parts = [
            "✅ <b>SUBMISSION SUCCESSFUL!</b>\n",
            f"📝 <b>Problem:</b> {title}",
            f"{difficulty_emoji} <b>Difficulty:</b> {difficulty}",
            f"🔗 <b>URL:</b> {url}\n"
        ]
        
        if runtime:
            message_parts.append(f"⚡ <b>Runtime:</b> {runtime}")
        
        if memory:
            message_parts.append(f"💾 <b>Memory:</b> {memory}")
        
        message_parts.append(f"\n⏰ <b>Time:</b> {self._get_timestamp()}")
        message_parts.append(f"🤖 <b>By:</b> {settings.PROJECT_NAME}")
        
        return "\n".join(message_parts)
    
    def _format_failure_message(
        self,
        title: str,
        url: str,
        error: str,
        step: str
    ) -> str:
        """Format failure notification message"""
        
        message_parts = [
            "❌ <b>SUBMISSION FAILED</b>\n",
            f"📝 <b>Problem:</b> {title}",
            f"🔗 <b>URL:</b> {url}",
            f"⚠️ <b>Failed Step:</b> {step}",
            f"📋 <b>Error:</b> {error}\n",
            f"⏰ <b>Time:</b> {self._get_timestamp()}"
        ]
        
        return "\n".join(message_parts)
    
    def _get_timestamp(self) -> str:
        """Get formatted current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def test_connection(self) -> bool:
        """
        Test Telegram bot connection
        
        Returns:
            True if bot is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    logger.info(f"Bot connected: @{bot_info.get('username')}")
                    return True
            
            logger.error("Failed to connect to Telegram bot")
            return False
            
        except Exception as e:
            logger.error(f"Error testing bot connection: {e}")
            return False
