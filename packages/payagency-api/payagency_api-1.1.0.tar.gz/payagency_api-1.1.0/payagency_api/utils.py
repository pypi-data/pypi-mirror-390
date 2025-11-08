"""
Utility functions for encryption and other operations
"""

import json
import os
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt_data(data: str, key: str) -> str:
    """
    Encrypts data using AES-256-CBC.
    
    Args:
        data: The data to encrypt
        key: The encryption key (32 characters)
        
    Returns:
        The encrypted data as hex string with IV prepended
    """
    # Generate a random 16-byte IV
    iv = os.urandom(16)
    
    # Convert key to bytes
    key_bytes = key.encode('utf-8')
    
    # Create cipher
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad data to be multiple of 16 bytes
    data_bytes = data.encode('utf-8')
    padding_length = 16 - (len(data_bytes) % 16)
    padded_data = data_bytes + bytes([padding_length] * padding_length)
    
    # Encrypt
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return IV + encrypted data as hex
    return iv.hex() + ":" + encrypted.hex()


def prepare_request_data(data: Dict[str, Any], encryption_key: str, skip_encryption: bool = False) -> Dict[str, Any]:
    """
    Prepares request data for API call, optionally encrypting it.
    
    Args:
        data: The data to prepare
        encryption_key: The encryption key
        skip_encryption: Whether to skip encryption
        
    Returns:
        The prepared data
    """
    if skip_encryption:
        return data
    
    json_data = json.dumps(data, separators=(',', ':'))
    encrypted_payload = encrypt_data(json_data, encryption_key)
    
    return {"payload": encrypted_payload}


def validate_config(encryption_key: str, secret_key: str) -> None:
    """
    Validates the configuration parameters.
    
    Args:
        encryption_key: The encryption key to validate
        secret_key: The secret key to validate
        
    Raises:
        ValueError: If validation fails
    """
    if not encryption_key or len(encryption_key) != 32:
        raise ValueError("Encryption key must be exactly 32 characters long")
    
    if not secret_key or not (secret_key.startswith("PA_TEST_") or secret_key.startswith("PA_LIVE_")):
        raise ValueError("Secret key must start with 'PA_TEST_' or 'PA_LIVE_'")


def get_environment(secret_key: str) -> str:
    """
    Determines the environment based on secret key.
    
    Args:
        secret_key: The secret key
        
    Returns:
        'live' or 'test'
    """
    return "live" if secret_key.startswith("PA_LIVE_") else "test"


def normalize_base_url(base_url: str) -> str:
    """
    Normalizes the base URL by ensuring it starts with https and has no trailing slash.
    
    Args:
        base_url: The base URL to normalize
        
    Returns:
        The normalized base URL
    """
    # Remove trailing slashes
    base_url = base_url.rstrip('/')
    
    # Ensure it starts with https://
    if not base_url.startswith('https://'):
        if base_url.startswith('http://'):
            base_url = base_url.replace('http://', 'https://', 1)
        else:
            base_url = f'https://{base_url}'
    
    return base_url
