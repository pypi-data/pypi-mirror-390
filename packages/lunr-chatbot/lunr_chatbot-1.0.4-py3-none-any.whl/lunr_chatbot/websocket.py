"""
Gestion de la connexion WebSocket pour les bots
"""
import asyncio
import json
import logging
from typing import Optional, Callable, Any
import websockets
from websockets.exceptions import ConnectionClosed

from .exceptions import WebSocketError

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    Client WebSocket pour la communication en temps réel avec Ondes Chat.
    """
    
    def __init__(self, ws_url: str, token: str):
        """
        Args:
            ws_url: URL du serveur WebSocket (ws://... ou wss://...)
            token: Token JWT pour l'authentification
        """
        self.ws_url = ws_url
        self.token = token
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.message_handler: Optional[Callable] = None
        self.reaction_handler: Optional[Callable] = None
        self.typing_handler: Optional[Callable] = None
        self._listen_task: Optional[asyncio.Task] = None
    
    async def connect(self, group_id: str):
        """
        Établit la connexion WebSocket au groupe.
        
        Args:
            group_id: ID du groupe à rejoindre
        """
        try:
            # Construire l'URL avec le token
            url = f"{self.ws_url}/ws/chat/{group_id}/?token={self.token}"
            
            logger.info(f"Connexion WebSocket à {url}")
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            
            logger.info(f"✅ Connecté au groupe {group_id}")
            
            # Démarrer l'écoute des messages
            self._listen_task = asyncio.create_task(self._listen())
            
        except Exception as e:
            raise WebSocketError(f"Erreur de connexion WebSocket: {e}")
    
    async def disconnect(self):
        """Ferme la connexion WebSocket"""
        self.is_connected = False
        
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket déconnecté")
    
    async def _listen(self):
        """Écoute les messages entrants du WebSocket"""
        try:
            while self.is_connected and self.websocket:
                message = await self.websocket.recv()
                await self._handle_message(message)
                
        except ConnectionClosed:
            logger.warning("Connexion WebSocket fermée")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Erreur dans l'écoute WebSocket: {e}")
            self.is_connected = False
    
    async def _handle_message(self, raw_message: str):
        """
        Traite un message reçu du WebSocket.
        
        Args:
            raw_message: Message brut JSON
        """
        try:
            logger.debug(f"📩 Message WebSocket brut reçu")
            data = json.loads(raw_message)
            message_type = data.get('type')
            logger.debug(f"📋 Type de message: {message_type}")
            
            if message_type == 'message':  # Backend envoie 'message', pas 'chat_message'
                # Nouveau message - les données sont dans 'data'
                message_data = data.get('data')
                if self.message_handler and message_data:
                    await self.message_handler(message_data)
            
            elif message_type == 'reaction_added' or message_type == 'reaction_removed':
                # Réaction ajoutée/retirée
                if self.reaction_handler:
                    await self.reaction_handler(data)
            
            elif message_type == 'typing' or message_type == 'stop_typing':  # Noms corrects
                # Indicateur de frappe
                if self.typing_handler:
                    await self.typing_handler(data)
            
            else:
                logger.debug(f"Type de message inconnu: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
        except Exception as e:
            logger.error(f"Erreur de traitement du message: {e}")
    
    async def send_message(self, content_encrypted: str, message_type: str = 'text'):
        """
        Envoie un message via WebSocket.
        
        Args:
            content_encrypted: Contenu chiffré du message
            message_type: Type de message (text, image, file, voice)
        """
        if not self.is_connected or not self.websocket:
            raise WebSocketError("WebSocket non connecté")
        
        try:
            payload = {
                'action': 'send_message',
                'content': content_encrypted,
                'message_type': message_type
            }
            
            await self.websocket.send(json.dumps(payload))
            logger.debug(f"Message envoyé: {message_type}")
            
        except Exception as e:
            raise WebSocketError(f"Erreur lors de l'envoi du message: {e}")
    
    async def send_typing(self, is_typing: bool = True):
        """
        Envoie un indicateur de frappe.
        
        Args:
            is_typing: True pour "en train d'écrire", False pour arrêter
        """
        if not self.is_connected or not self.websocket:
            return
        
        try:
            action = 'typing' if is_typing else 'stop_typing'
            payload = {'action': action}
            await self.websocket.send(json.dumps(payload))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'indicateur de frappe: {e}")
    
    async def add_reaction(self, message_id: str, reaction: str):
        """
        Ajoute une réaction à un message.
        
        Args:
            message_id: ID du message
            reaction: Emoji de la réaction
        """
        if not self.is_connected or not self.websocket:
            raise WebSocketError("WebSocket non connecté")
        
        try:
            payload = {
                'action': 'add_reaction',
                'message_id': message_id,
                'reaction': reaction
            }
            await self.websocket.send(json.dumps(payload))
            
        except Exception as e:
            raise WebSocketError(f"Erreur lors de l'ajout de réaction: {e}")
    
    async def remove_reaction(self, message_id: str, reaction: str):
        """
        Retire une réaction d'un message.
        
        Args:
            message_id: ID du message
            reaction: Emoji de la réaction
        """
        if not self.is_connected or not self.websocket:
            raise WebSocketError("WebSocket non connecté")
        
        try:
            payload = {
                'action': 'remove_reaction',
                'message_id': message_id,
                'reaction': reaction
            }
            await self.websocket.send(json.dumps(payload))
            
        except Exception as e:
            raise WebSocketError(f"Erreur lors du retrait de réaction: {e}")
    
    def on_message(self, handler: Callable):
        """
        Enregistre un handler pour les nouveaux messages.
        
        Args:
            handler: Fonction async à appeler pour chaque nouveau message
        """
        self.message_handler = handler
    
    def on_reaction(self, handler: Callable):
        """
        Enregistre un handler pour les réactions.
        
        Args:
            handler: Fonction async à appeler pour chaque réaction
        """
        self.reaction_handler = handler
    
    def on_typing(self, handler: Callable):
        """
        Enregistre un handler pour les indicateurs de frappe.
        
        Args:
            handler: Fonction async à appeler pour chaque indicateur
        """
        self.typing_handler = handler
