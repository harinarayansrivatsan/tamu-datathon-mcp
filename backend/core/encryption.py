"""
Simple encryption utilities for sensitive data.
Uses Fernet (symmetric encryption) from cryptography library.
"""

from cryptography.fernet import Fernet
from backend.core import get_settings

settings = get_settings()


def get_cipher():
    """Get Fernet cipher instance using SECRET_KEY."""
    # Use first 32 bytes of SECRET_KEY as Fernet key
    # In production, use a dedicated encryption key
    key = settings.secret_key.encode()[:32]
    # Fernet requires base64-encoded 32-byte key
    import base64
    key_b64 = base64.urlsafe_b64encode(key.ljust(32)[:32])
    return Fernet(key_b64)


def encrypt_token(token: str) -> str:
    """Encrypt a token string."""
    if not token:
        return ""

    cipher = get_cipher()
    encrypted = cipher.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token string."""
    if not encrypted_token:
        return ""

    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting token: {e}")
        return ""
