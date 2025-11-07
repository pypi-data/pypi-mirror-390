"""
Client principal pour créer des bots Ondes Chat
"""
import asyncio
import logging
import os
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import aiohttp

from .encryption import EncryptionManager
from .websocket import WebSocketClient
from .models import Message, User, Group
from .exceptions import AuthenticationError, APIError, EncryptionError, WebSocketError

logger = logging.getLogger(__name__)


class OndesBotClient:
    """
    Client principal pour créer des bots Ondes Chat.
    
    Exemple:
        bot = OndesBotClient(
            api_url="http://localhost:8000",
            bot_token="your_bot_token"
        )
        
        @bot.on_message
        async def handle_message(message):
            if message.content == "/hello":
                await bot.send_message(message.group_id, "Hello! 👋")
        
        bot.run()
    """
    
    def __init__(self, api_url: str, bot_token: str, auto_decrypt: bool = True, keys_dir: str = ".bot_keys"):
        """
        Args:
            api_url: URL de l'API (ex: http://localhost:8000)
            bot_token: Token JWT du bot
            auto_decrypt: Déchiffrer automatiquement les messages entrants
            keys_dir: Répertoire où stocker les clés (par défaut: .bot_keys/)
        """
        self.api_url = api_url.rstrip('/')
        self.bot_token = bot_token
        self.auto_decrypt = auto_decrypt
        self.keys_dir = Path(keys_dir)
        
        # Créer le répertoire des clés s'il n'existe pas
        self.keys_dir.mkdir(exist_ok=True)
        
        # Déterminer l'URL WebSocket
        ws_protocol = 'wss' if api_url.startswith('https') else 'ws'
        ws_host = api_url.replace('https://', '').replace('http://', '')
        self.ws_url = f"{ws_protocol}://{ws_host}"
        
        # Composants
        self.encryption = EncryptionManager()
        self.websocket: Optional[WebSocketClient] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # État
        self.bot_user: Optional[User] = None
        self.current_group: Optional[Group] = None
        self.groups: Dict[str, Group] = {}
        
        # Handlers
        self._message_handlers: List[Callable] = []
        self._reaction_handlers: List[Callable] = []
        self._typing_handlers: List[Callable] = []
    
    async def _init_session(self):
        """Initialise la session HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.bot_token}',
                    'Content-Type': 'application/json'
                }
            )
    
    async def _close_session(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def initialize(self):
        """
        Initialise le bot (authentification, récupération du profil, etc.)
        """
        try:
            logger.info("Initialisation du bot...")
            
            await self._init_session()
            
            # Récupérer le profil du bot
            async with self.session.get(f"{self.api_url}/api/auth/profile/") as resp:
                if resp.status == 401:
                    raise AuthenticationError("Token invalide ou expiré")
                elif resp.status != 200:
                    raise APIError(f"Erreur API: {resp.status}")
                
                data = await resp.json()
                self.bot_user = User.from_dict(data)
                logger.info(f"✅ Bot authentifié: {self.bot_user.username}")
            
            # Chemin du fichier de clés pour ce bot
            keys_file = self.keys_dir / f"{self.bot_user.username}_keys.pem"
            
            # Générer ou charger les clés de chiffrement
            if not data.get('public_key'):
                logger.info("🔐 Génération des clés de chiffrement RSA...")
                public_key, private_key = self.encryption.generate_keypair()
                
                # Sauvegarder localement
                with open(keys_file, 'w') as f:
                    f.write(private_key)
                logger.info(f"💾 Clés sauvegardées dans {keys_file}")
                
                # Enregistrer les clés sur le serveur
                async with self.session.patch(
                    f"{self.api_url}/api/auth/profile/",
                    json={
                        'public_key': public_key,
                        'private_key_encrypted': private_key
                    }
                ) as resp:
                    if resp.status == 200:
                        logger.info("✅ Clés enregistrées sur le serveur")
                    else:
                        logger.warning("⚠️ Échec de l'enregistrement des clés")
                        
                # Charger la clé privée en mémoire
                self.encryption.load_private_key(private_key)
                
            else:
                # Essayer de charger depuis le fichier local
                if keys_file.exists():
                    logger.info(f"📂 Chargement des clés depuis {keys_file}")
                    with open(keys_file, 'r') as f:
                        private_key = f.read()
                    self.encryption.load_private_key(private_key)
                else:
                    # Récupérer depuis le serveur
                    logger.info("📥 Récupération de la clé privée depuis le serveur")
                    private_key = data.get('private_key_encrypted')
                    if private_key:
                        # Sauvegarder localement pour la prochaine fois
                        with open(keys_file, 'w') as f:
                            f.write(private_key)
                        self.encryption.load_private_key(private_key)
                    else:
                        raise EncryptionError("Clé privée introuvable")
                
                logger.info("✅ Clés de chiffrement chargées")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation: {e}")
            raise

    async def join_group(self, group_id: str):
        """
        Rejoint un groupe et établit la connexion WebSocket.
        
        Args:
            group_id: ID du groupe à rejoindre
        """
        try:
            logger.info(f"📡 Connexion au groupe {group_id}...")
            
            # Récupérer les infos du groupe
            async with self.session.get(f"{self.api_url}/api/groups/{group_id}/") as resp:
                if resp.status != 200:
                    raise APIError(f"Groupe non trouvé: {resp.status}")
                
                data = await resp.json()
                self.current_group = Group.from_dict(data)
                self.groups[group_id] = self.current_group
                logger.info(f"✅ Groupe trouvé: {self.current_group.name or group_id}")
            
            # Récupérer les clés de groupe (toutes les sessions)
            keys_url = f"{self.api_url}/api/groups/{group_id}/keys/"
            async with self.session.get(keys_url) as resp:
                if resp.status == 200:
                    keys_data = await resp.json()
                    sessions = keys_data.get('sessions', [])
                    
                    # Récupérer la session active (dernière version)
                    if sessions:
                        active_session = next((s for s in sessions if s.get('is_active')), sessions[0])
                        encrypted_key = active_session.get('encrypted_key')
                        if encrypted_key:
                            self.encryption.decrypt_group_key(encrypted_key, group_id)
                            logger.info(f"✅ Clé de groupe déchiffrée (session v{active_session.get('version')})")
                        else:
                            logger.warning(f"⚠️ Aucune clé chiffrée dans la session")
                    else:
                        logger.warning(f"⚠️ Aucune session de clé disponible pour ce groupe")
                else:
                    logger.warning(f"⚠️ Impossible de récupérer les clés du groupe (status: {resp.status})")
            
            # Connecter le WebSocket
            logger.info("🔌 Connexion au WebSocket...")
            self.websocket = WebSocketClient(self.ws_url, self.bot_token)
            self.websocket.on_message(self._handle_incoming_message)
            self.websocket.on_reaction(self._handle_reaction)
            self.websocket.on_typing(self._handle_typing)
            
            await self.websocket.connect(group_id)
            logger.info(f"✅ Connecté au groupe {self.current_group.name or group_id}")
            logger.info(f"👂 En écoute des messages...")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion au groupe: {e}")
            raise

    async def leave_group(self):
        """Quitte le groupe actuel"""
        if self.websocket:
            await self.websocket.disconnect()
            self.websocket = None
        self.current_group = None
        logger.info("Groupe quitté")
    
    async def send_message(self, group_id: str = None, content: str = None, message_type: str = 'text'):
        """
        Envoie un message dans un groupe.
        
        Args:
            group_id: ID du groupe (optionnel, utilise le groupe actuel si non spécifié)
            content: Contenu du message (sera chiffré automatiquement)
            message_type: Type de message (text, image, file, voice)
        """
        if not self.websocket or not self.websocket.is_connected:
            raise WebSocketError("WebSocket non connecté. Appelez join_group() d'abord.")
        
        # Utiliser le groupe actuel si group_id n'est pas fourni
        if not group_id:
            if not self.current_group:
                raise ValueError("Aucun groupe spécifié et pas de groupe actuel")
            group_id = self.current_group.id
        
        try:
            # Chiffrer le message
            encrypted_content = self.encryption.encrypt_message(content, group_id)
            
            # Envoyer via WebSocket
            await self.websocket.send_message(encrypted_content, message_type)
            logger.debug(f"Message envoyé dans {group_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi du message: {e}")
            raise

    async def send_typing(self, is_typing: bool = True):
        """
        Envoie un indicateur "en train d'écrire".
        
        Args:
            is_typing: True pour commencer, False pour arrêter
        """
        if self.websocket and self.websocket.is_connected:
            await self.websocket.send_typing(is_typing)

    async def add_reaction(self, message_id: str, reaction: str):
        """
        Ajoute une réaction à un message.
        
        Args:
            message_id: ID du message
            reaction: Emoji (ex: '👍', '❤️')
        """
        if self.websocket and self.websocket.is_connected:
            await self.websocket.add_reaction(message_id, reaction)

    async def _handle_incoming_message(self, message_data: Dict[str, Any]):
        """
        Traite un message entrant.

        Args:
            message_data: Données du message
        """
        try:
            logger.debug(f"📨 Message reçu: {message_data.get('id', 'unknown')}")
            
            # Déchiffrer le contenu si auto_decrypt est activé
            decrypted_content = None
            if self.auto_decrypt and self.current_group:
                try:
                    encrypted = message_data.get('content_encrypted')
                    logger.debug(f"🔐 Tentative de déchiffrement: {encrypted[:50]}...")
                    decrypted_content = self.encryption.decrypt_message(
                        encrypted,
                        self.current_group.id
                    )
                    logger.debug(f"✅ Message déchiffré: {decrypted_content}")
                except EncryptionError as e:
                    logger.error(f"❌ Impossible de déchiffrer le message: {e}")
                except Exception as e:
                    logger.error(f"❌ Erreur inattendue lors du déchiffrement: {e}", exc_info=True)
            
            # Créer l'objet Message
            message = Message.from_dict(message_data, decrypted_content)
            
            # Ne pas traiter les messages envoyés par le bot lui-même
            if self.bot_user and message.sender.id == self.bot_user.id:
                return
            
            # Appeler tous les handlers
            for handler in self._message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Erreur dans le handler de message: {e}")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message entrant: {e}")
    
    async def _handle_reaction(self, reaction_data: Dict[str, Any]):
        """Traite une réaction"""
        for handler in self._reaction_handlers:
            try:
                await handler(reaction_data)
            except Exception as e:
                logger.error(f"Erreur dans le handler de réaction: {e}")
    
    async def _handle_typing(self, typing_data: Dict[str, Any]):
        """Traite un indicateur de frappe"""
        for handler in self._typing_handlers:
            try:
                await handler(typing_data)
            except Exception as e:
                logger.error(f"Erreur dans le handler de frappe: {e}")
    
    def on_message(self, func: Callable):
        """
        Décorateur pour enregistrer un handler de messages.
        
        Exemple:
            @bot.on_message
            async def handle(message):
                print(f"Message reçu: {message.content}")
        """
        self._message_handlers.append(func)
        return func
    
    def on_reaction(self, func: Callable):
        """Décorateur pour enregistrer un handler de réactions"""
        self._reaction_handlers.append(func)
        return func
    
    def on_typing(self, func: Callable):
        """Décorateur pour enregistrer un handler d'indicateurs de frappe"""
        self._typing_handlers.append(func)
        return func
    
    def run(self, group_id: str):
        """
        Lance le bot de manière synchrone (bloquante).
        
        Args:
            group_id: ID du groupe à rejoindre
        """
        try:
            asyncio.run(self.run_async(group_id))
        except KeyboardInterrupt:
            logger.info("Bot arrêté par l'utilisateur")
    
    async def run_async(self, group_id: str):
        """
        Lance le bot de manière asynchrone.
        
        Args:
            group_id: ID du groupe à rejoindre
        """
        try:
            await self.initialize()
            await self.join_group(group_id)
            
            logger.info(f"✅ Bot {self.bot_user.username} en cours d'exécution...")
            logger.info("Appuyez sur Ctrl+C pour arrêter")
            
            # Garder le bot en vie
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Arrêt du bot...")
        finally:
            await self.leave_group()
            await self._close_session()
            logger.info("Bot arrêté")
