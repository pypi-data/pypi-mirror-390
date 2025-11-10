import hashlib
import hmac
import secrets
from datetime import datetime

def encrypt_key(data, key):
    try:
        salt = secrets.token_bytes(32)
        
        derived = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100000)
        
        encrypted = bytearray()
        for i, byte in enumerate(data.encode()):
            encrypted.append(byte ^ derived[i % len(derived)])
        
        return salt.hex() + encrypted.hex()
    except:
        return None

def decrypt_key(encrypted_data, key):
    try:
        salt = bytes.fromhex(encrypted_data[:64])
        encrypted = bytes.fromhex(encrypted_data[64:])
        
        derived = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100000)
        
        decrypted = bytearray()
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ derived[i % len(derived)])
        
        return decrypted.decode()
    except:
        return None

def generate_signature(data, key):
    try:
        timestamp = datetime.now().isoformat()
        message = f"{data}{timestamp}{key}"
        
        signature = hmac.new(
            key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    except:
        return None

def verify_signature(data, key, signature):
    try:
        expected = generate_signature(data, key)
        if expected is None:
            return False
        return hmac.compare_digest(expected, signature)
    except:
        return False

def generate_key_hash(key):
    try:
        salt = b'santaim_static_salt_v1'
        derived = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100000)
        return derived.hex()
    except:
        return None
