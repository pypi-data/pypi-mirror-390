"""
Gestion du chiffrement E2E pour les bots
"""
import base64
import json
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os

from .exceptions import EncryptionError


class EncryptionManager:
    """
    Gère le chiffrement et déchiffrement des messages pour les bots.
    Utilise RSA pour l'échange de clés et AES-256-GCM pour les messages.
    """
    
    def __init__(self):
        self.private_key: Optional[rsa.RSAPrivateKey] = None
        self.public_key: Optional[rsa.RSAPublicKey] = None
        self.group_keys: dict = {}  # {group_id: group_key_bytes}
    
    def generate_keypair(self) -> tuple[str, str]:
        """
        Génère une paire de clés RSA pour le bot.
        
        Returns:
            tuple[str, str]: (public_key_pem, private_key_pem)
        """
        try:
            # Générer la clé privée
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Extraire la clé publique
            self.public_key = self.private_key.public_key()
            
            # Sérialiser en PEM
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Encoder en base64 pour le transport
            private_key_b64 = base64.b64encode(private_pem).decode('utf-8')
            public_key_b64 = base64.b64encode(public_pem).decode('utf-8')
            
            return public_key_b64, private_key_b64
            
        except Exception as e:
            raise EncryptionError(f"Erreur lors de la génération des clés: {e}")
    
    def load_private_key(self, private_key_b64: str):
        """
        Charge une clé privée depuis une chaîne base64.
        
        Args:
            private_key_b64: Clé privée en base64
        """
        try:
            private_pem = base64.b64decode(private_key_b64.encode('utf-8'))
            self.private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
        except Exception as e:
            raise EncryptionError(f"Erreur lors du chargement de la clé privée: {e}")
    
    def decrypt_group_key(self, encrypted_group_key_b64: str, group_id: str):
        """
        Déchiffre la clé de groupe avec la clé privée RSA du bot.
        
        Args:
            encrypted_group_key_b64: Clé de groupe chiffrée en base64
            group_id: ID du groupe
        """
        if not self.private_key:
            raise EncryptionError("Clé privée non chargée")
        
        try:
            # Décoder le base64
            encrypted_key = base64.b64decode(encrypted_group_key_b64.encode('utf-8'))
            
            # Déchiffrer avec RSA
            group_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Stocker la clé du groupe
            self.group_keys[group_id] = group_key
            
        except Exception as e:
            raise EncryptionError(f"Erreur lors du déchiffrement de la clé de groupe: {e}")
    
    def encrypt_message(self, plain_text: str, group_id: str) -> str:
        """
        Chiffre un message avec AES-256-GCM (compatible Flutter).
        
        Args:
            plain_text: Texte en clair
            group_id: ID du groupe
            
        Returns:
            str: Message chiffré en base64(utf8(JSON)) - format Flutter
        """
        if group_id not in self.group_keys:
            raise EncryptionError(f"Clé de groupe non disponible pour {group_id}")
        
        try:
            group_key = self.group_keys[group_id]
            
            # Générer un nonce aléatoire (12 bytes pour GCM)
            nonce = os.urandom(12)
            
            # Créer le cipher AES-GCM
            cipher = Cipher(
                algorithms.AES(group_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Chiffrer
            ciphertext = encryptor.update(plain_text.encode('utf-8')) + encryptor.finalize()
            
            # Obtenir le tag d'authentification
            tag = encryptor.tag
            
            # Format Flutter : {"iv": "...", "tag": "...", "ciphertext": "..."}
            result = {
                'iv': base64.b64encode(nonce).decode('utf-8'),  # 'iv' au lieu de 'nonce'
                'tag': base64.b64encode(tag).decode('utf-8'),
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
            }
            
            # Encoder en base64(utf8(JSON)) comme Flutter
            json_str = json.dumps(result)
            return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            raise EncryptionError(f"Erreur lors du chiffrement: {e}")
    
    def decrypt_message(self, encrypted_message: str, group_id: str) -> str:
        """
        Déchiffre un message avec AES-256-GCM.
        
        Args:
            encrypted_message: Message chiffré (format JSON avec iv/nonce, tag, ciphertext)
            group_id: ID du groupe
            
        Returns:
            str: Texte déchiffré
        """
        if group_id not in self.group_keys:
            raise EncryptionError(f"Clé de groupe non disponible pour {group_id}")
        
        try:
            group_key = self.group_keys[group_id]
            
            # Parser le JSON (peut être encodé en base64 comme dans Flutter)
            try:
                # Essayer de décoder depuis base64 (format Flutter)
                decoded = base64.b64decode(encrypted_message.encode('utf-8')).decode('utf-8')
                data = json.loads(decoded)
            except:
                # Sinon parser directement comme JSON
                data = json.loads(encrypted_message)
            
            # Supporter les deux formats : 'iv' (Flutter) et 'nonce' (Python)
            nonce_b64 = data.get('iv') or data.get('nonce')
            if not nonce_b64:
                raise EncryptionError("Nonce/IV manquant dans le message chiffré")
            
            nonce = base64.b64decode(nonce_b64.encode('utf-8'))
            tag = base64.b64decode(data['tag'].encode('utf-8'))
            ciphertext = base64.b64decode(data['ciphertext'].encode('utf-8'))
            
            # Créer le cipher AES-GCM
            cipher = Cipher(
                algorithms.AES(group_key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Déchiffrer
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            raise EncryptionError(f"Erreur lors du déchiffrement: {e}")
