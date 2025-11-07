"""
Exceptions personnalisées pour la bibliothèque Ondes Bot
"""


class OndesBotException(Exception):
    """Classe de base pour toutes les exceptions de la bibliothèque"""
    pass


class AuthenticationError(OndesBotException):
    """Erreur d'authentification"""
    pass


class EncryptionError(OndesBotException):
    """Erreur de chiffrement/déchiffrement"""
    pass


class WebSocketError(OndesBotException):
    """Erreur de connexion WebSocket"""
    pass


class APIError(OndesBotException):
    """Erreur lors d'un appel API"""
    pass


class MessageSendError(OndesBotException):
    """Erreur lors de l'envoi d'un message"""
    pass
