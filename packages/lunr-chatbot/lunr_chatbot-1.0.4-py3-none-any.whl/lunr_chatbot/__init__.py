"""
Ondes Chat Bot Library
======================

Bibliothèque Python pour créer des bots pour l'application Ondes Chat.

Exemple d'utilisation:
    from chatbot import OndesBotClient
    
    bot = OndesBotClient(
        api_url="http://localhost:8000",
        bot_token="your_bot_token_here"
    )
    
    @bot.on_message
    async def handle_message(message):
        if message.content == "/hello":
            await bot.send_message(
                group_id=message.group_id,
                content="Hello! 👋"
            )
    
    bot.run()
"""

__version__ = "1.0.0"
__author__ = "Ondes Chat"

from .client import OndesBotClient
from .models import Message, User, Group
from .exceptions import (
    OndesBotException,
    AuthenticationError,
    EncryptionError,
    WebSocketError
)

__all__ = [
    'OndesBotClient',
    'Message',
    'User',
    'Group',
    'OndesBotException',
    'AuthenticationError',
    'EncryptionError',
    'WebSocketError'
]
