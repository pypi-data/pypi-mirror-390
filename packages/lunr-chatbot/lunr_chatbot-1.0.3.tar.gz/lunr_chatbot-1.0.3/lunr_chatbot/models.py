"""
Modèles de données pour les messages, utilisateurs et groupes
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class User:
    """Représente un utilisateur"""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    is_online: bool = False
    is_bot: bool = False
    
    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage de l'utilisateur"""
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name
        return self.username
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Créer un User depuis un dictionnaire"""
        return cls(
            id=data['id'],
            username=data['username'],
            email=data.get('email', ''),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            avatar=data.get('avatar'),
            is_online=data.get('is_online', False),
            is_bot=data.get('is_bot', False)
        )


@dataclass
class Group:
    """Représente un groupe"""
    id: str
    name: Optional[str]
    group_type: str  # 'private' ou 'group'
    members: List[User]
    description: Optional[str] = None
    avatar: Optional[str] = None
    
    @property
    def is_private(self) -> bool:
        """Retourne True si c'est une discussion privée"""
        return self.group_type == 'private'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        """Créer un Group depuis un dictionnaire"""
        members = [User.from_dict(m) for m in data.get('members', [])]
        return cls(
            id=data['id'],
            name=data.get('name'),
            group_type=data['group_type'],
            members=members,
            description=data.get('description'),
            avatar=data.get('avatar')
        )


@dataclass
class Message:
    """Représente un message"""
    id: str
    content: str  # Contenu déchiffré
    content_encrypted: str  # Contenu chiffré
    sender: User
    group_id: str
    message_type: str  # 'text', 'image', 'file', 'voice', 'poll'
    created_at: datetime
    is_edited: bool = False
    reply_to: Optional['Message'] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    reactions: Dict[str, List[User]] = None
    
    def __post_init__(self):
        if self.reactions is None:
            self.reactions = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], decrypted_content: str = None) -> 'Message':
        """Créer un Message depuis un dictionnaire"""
        sender = User.from_dict(data['sender'])
        
        # Parser la date
        created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        # Parser reply_to si présent
        reply_to = None
        if data.get('reply_to'):
            reply_to_data = data['reply_to']
            reply_sender = User.from_dict(reply_to_data['sender'])
            reply_to = Message(
                id=reply_to_data['id'],
                content=reply_to_data.get('content', ''),
                content_encrypted=reply_to_data.get('content', ''),
                sender=reply_sender,
                group_id=data.get('group', {}).get('id', ''),
                message_type=reply_to_data.get('message_type', 'text'),
                created_at=created_at
            )
        
        # Parser les réactions
        reactions = {}
        for emoji, reaction_data in data.get('reactions', {}).items():
            reactions[emoji] = [User.from_dict(u) for u in reaction_data.get('users', [])]
        
        return cls(
            id=data['id'],
            content=decrypted_content or data.get('content_encrypted', ''),
            content_encrypted=data['content_encrypted'],
            sender=sender,
            group_id=data.get('group', {}).get('id', ''),
            message_type=data.get('message_type', 'text'),
            created_at=created_at,
            is_edited=data.get('is_edited', False),
            reply_to=reply_to,
            file_url=data.get('file'),
            file_name=data.get('file_name'),
            reactions=reactions
        )
