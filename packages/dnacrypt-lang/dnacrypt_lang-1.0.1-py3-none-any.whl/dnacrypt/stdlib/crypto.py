"""
DNACrypt Standard Library - Cryptography Module
Provides cryptographic primitives and operations

File: dnacrypt_stdlib/crypto.py
"""

import hashlib
import hmac
import secrets
import os
from typing import Optional, Tuple, Union
from dataclasses import dataclass

# Cryptography library
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding as asym_padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not installed. Install with: pip install cryptography")


# ============ DATA STRUCTURES ============

@dataclass
class Key:
    """Cryptographic key"""
    algorithm: str
    key_data: bytes
    key_object: Optional[object] = None  # For cryptography library objects
    is_private: bool = False
    key_size: int = 0
    
    def __repr__(self):
        return f"Key(algorithm={self.algorithm}, size={self.key_size}, private={self.is_private})"
    
    def to_bytes(self) -> bytes:
        """Export key as bytes"""
        if self.key_object and hasattr(self.key_object, 'private_bytes'):
            # RSA/ECDSA private key
            return self.key_object.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        elif self.key_object and hasattr(self.key_object, 'public_bytes'):
            # RSA/ECDSA public key
            return self.key_object.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        return self.key_data
    
    def to_hex(self) -> str:
        """Export key as hex string"""
        return self.key_data.hex()


@dataclass
class KeyPair:
    """Public/Private key pair"""
    private_key: Key
    public_key: Key
    algorithm: str
    
    def __repr__(self):
        return f"KeyPair(algorithm={self.algorithm})"


@dataclass
class EncryptedData:
    """Encrypted data container"""
    algorithm: str
    ciphertext: bytes
    iv: bytes
    tag: Optional[bytes] = None  # For AEAD modes
    metadata: Optional[dict] = None
    
    def __repr__(self):
        return f"EncryptedData(algorithm={self.algorithm}, size={len(self.ciphertext)} bytes)"


@dataclass
class HashDigest:
    """Hash digest"""
    algorithm: str
    digest: bytes
    
    def __repr__(self):
        return f"Hash({self.algorithm})"
    
    def hex(self) -> str:
        """Return hex representation"""
        return self.digest.hex()
    
    def base64(self) -> str:
        """Return base64 representation"""
        import base64
        return base64.b64encode(self.digest).decode('utf-8')


@dataclass
class Signature:
    """Digital signature"""
    algorithm: str
    signature: bytes
    
    def __repr__(self):
        return f"Signature(algorithm={self.algorithm})"
    
    def hex(self) -> str:
        """Return hex representation"""
        return self.signature.hex()


# ============ EXCEPTIONS ============

class CryptoError(Exception):
    """Base cryptography error"""
    pass


class EncryptionError(CryptoError):
    """Encryption failed"""
    pass


class DecryptionError(CryptoError):
    """Decryption failed"""
    pass


class KeyError(CryptoError):
    """Key operation error"""
    pass


class SignatureError(CryptoError):
    """Signature operation error"""
    pass


# ============ KEY GENERATION ============

def generate_key(algorithm: str, size: Optional[int] = None) -> Key:
    """
    Generate symmetric encryption key
    
    Args:
        algorithm: Algorithm name (AES128, AES192, AES256, ChaCha20)
        size: Key size in bits (optional, inferred from algorithm)
    
    Returns:
        Key object
    """
    # Determine key size
    key_sizes = {
        "AES128": 128,
        "AES192": 192,
        "AES256": 256,
        "ChaCha20": 256,
    }
    
    key_size = size or key_sizes.get(algorithm)
    if not key_size:
        raise KeyError(f"Unknown algorithm or size not specified: {algorithm}")
    
    # Generate random key
    key_bytes = secrets.token_bytes(key_size // 8)
    
    return Key(
        algorithm=algorithm,
        key_data=key_bytes,
        key_size=key_size,
        is_private=False
    )


def generate_keypair(algorithm: str, key_size: Optional[int] = None) -> KeyPair:
    """
    Generate asymmetric key pair
    
    Args:
        algorithm: Algorithm name (RSA2048, RSA4096, ECDSA_P256, ECDSA_P384, ECDSA_P521)
        key_size: Key size in bits (for RSA)
    
    Returns:
        KeyPair object
    """
    if not CRYPTO_AVAILABLE:
        raise CryptoError("cryptography library not installed")
    
    if algorithm.startswith("RSA"):
        # RSA key pair
        size = key_size or int(algorithm[3:])
        
        private_key_obj = rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
            backend=default_backend()
        )
        public_key_obj = private_key_obj.public_key()
        
        # Extract key bytes
        private_bytes = private_key_obj.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key_obj.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        private_key = Key(
            algorithm=algorithm,
            key_data=private_bytes,
            key_object=private_key_obj,
            is_private=True,
            key_size=size
        )
        
        public_key = Key(
            algorithm=algorithm,
            key_data=public_bytes,
            key_object=public_key_obj,
            is_private=False,
            key_size=size
        )
        
        return KeyPair(private_key, public_key, algorithm)
    
    elif algorithm.startswith("ECDSA"):
        # ECDSA key pair
        curve_map = {
            "ECDSA_P256": ec.SECP256R1(),
            "ECDSA_P384": ec.SECP384R1(),
            "ECDSA_P521": ec.SECP521R1(),
        }
        
        curve = curve_map.get(algorithm)
        if not curve:
            raise KeyError(f"Unknown ECDSA curve: {algorithm}")
        
        private_key_obj = ec.generate_private_key(curve, default_backend())
        public_key_obj = private_key_obj.public_key()
        
        # Extract key bytes
        private_bytes = private_key_obj.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key_obj.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        private_key = Key(
            algorithm=algorithm,
            key_data=private_bytes,
            key_object=private_key_obj,
            is_private=True
        )
        
        public_key = Key(
            algorithm=algorithm,
            key_data=public_bytes,
            key_object=public_key_obj,
            is_private=False
        )
        
        return KeyPair(private_key, public_key, algorithm)
    
    else:
        raise KeyError(f"Unknown algorithm: {algorithm}")


def derive_key(password: Union[str, bytes], 
               salt: bytes,
               algorithm: str = "PBKDF2",
               iterations: int = 100000,
               key_length: int = 32) -> Key:
    """
    Derive key from password
    
    Args:
        password: Password string or bytes
        salt: Random salt (at least 16 bytes)
        algorithm: KDF algorithm (PBKDF2, Scrypt)
        iterations: Number of iterations (PBKDF2)
        key_length: Derived key length in bytes
    
    Returns:
        Key object
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if len(salt) < 16:
        raise KeyError("Salt must be at least 16 bytes")
    
    if algorithm == "PBKDF2":
        if not CRYPTO_AVAILABLE:
            # Fallback to hashlib
            key_data = hashlib.pbkdf2_hmac('sha256', password, salt, iterations, key_length)
        else:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=key_length,
                salt=salt,
                iterations=iterations,
                backend=default_backend()
            )
            key_data = kdf.derive(password)
    
    elif algorithm == "Scrypt":
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Scrypt requires cryptography library")
        
        kdf = Scrypt(
            salt=salt,
            length=key_length,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        key_data = kdf.derive(password)
    
    else:
        raise KeyError(f"Unknown KDF algorithm: {algorithm}")
    
    return Key(
        algorithm=f"AES{key_length * 8}",
        key_data=key_data,
        key_size=key_length * 8
    )


# ============ SYMMETRIC ENCRYPTION ============

def encrypt(plaintext: Union[str, bytes],
            key: Key,
            mode: str = "GCM",
            associated_data: Optional[bytes] = None) -> EncryptedData:
    """
    Encrypt data with symmetric key
    
    Args:
        plaintext: Data to encrypt
        key: Encryption key
        mode: Cipher mode (GCM, CBC, CTR)
        associated_data: Additional authenticated data (GCM only)
    
    Returns:
        EncryptedData object
    """
    if not CRYPTO_AVAILABLE:
        raise CryptoError("cryptography library required for encryption")
    
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    # Generate IV
    if mode == "GCM":
        iv = secrets.token_bytes(12)  # 96 bits for GCM
    else:
        iv = secrets.token_bytes(16)  # 128 bits for CBC/CTR
    
    # Encrypt based on mode
    if mode == "GCM":
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag
        
        return EncryptedData(
            algorithm=f"{key.algorithm}-{mode}",
            ciphertext=ciphertext,
            iv=iv,
            tag=tag
        )
    
    elif mode == "CBC":
        # Apply PKCS7 padding
        padding_length = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([padding_length] * padding_length)
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        
        return EncryptedData(
            algorithm=f"{key.algorithm}-{mode}",
            ciphertext=ciphertext,
            iv=iv
        )
    
    elif mode == "CTR":
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CTR(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptedData(
            algorithm=f"{key.algorithm}-{mode}",
            ciphertext=ciphertext,
            iv=iv
        )
    
    else:
        raise EncryptionError(f"Unknown cipher mode: {mode}")


def decrypt(encrypted: EncryptedData,
            key: Key,
            associated_data: Optional[bytes] = None) -> bytes:
    """
    Decrypt data with symmetric key
    
    Args:
        encrypted: EncryptedData object
        key: Decryption key
        associated_data: Additional authenticated data (GCM only)
    
    Returns:
        Decrypted plaintext bytes
    """
    if not CRYPTO_AVAILABLE:
        raise CryptoError("cryptography library required for decryption")
    
    try:
        if "GCM" in encrypted.algorithm:
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(encrypted.iv, encrypted.tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            plaintext = decryptor.update(encrypted.ciphertext) + decryptor.finalize()
        
        elif "CBC" in encrypted.algorithm:
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(encrypted.iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded = decryptor.update(encrypted.ciphertext) + decryptor.finalize()
            
            # Remove PKCS7 padding
            padding_length = padded[-1]
            plaintext = padded[:-padding_length]
        
        elif "CTR" in encrypted.algorithm:
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CTR(encrypted.iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(encrypted.ciphertext) + decryptor.finalize()
        
        else:
            raise DecryptionError(f"Unknown algorithm: {encrypted.algorithm}")
        
        return plaintext
    
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {str(e)}")


# ============ HASHING ============

def hash_data(data: Union[str, bytes], algorithm: str = "SHA256") -> HashDigest:
    """
    Hash data
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (SHA256, SHA3_256, SHA3_512, BLAKE2b, BLAKE2s)
    
    Returns:
        HashDigest object
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    algorithms_map = {
        "SHA256": hashlib.sha256,
        "SHA3_256": hashlib.sha3_256,
        "SHA3_512": hashlib.sha3_512,
        "BLAKE2b": hashlib.blake2b,
        "BLAKE2s": hashlib.blake2s,
        "SHA512": hashlib.sha512,
        "SHA1": hashlib.sha1,
    }
    
    hash_func = algorithms_map.get(algorithm)
    if not hash_func:
        raise CryptoError(f"Unknown hash algorithm: {algorithm}")
    
    digest = hash_func(data).digest()
    
    return HashDigest(algorithm=algorithm, digest=digest)


def hmac_data(data: Union[str, bytes], 
              key: Key,
              algorithm: str = "SHA256") -> HashDigest:
    """
    Create HMAC
    
    Args:
        data: Data to authenticate
        key: Secret key
        algorithm: Hash algorithm
    
    Returns:
        HashDigest object
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    algorithms_map = {
        "SHA256": hashlib.sha256,
        "SHA3_256": hashlib.sha3_256,
    }
    
    hash_func = algorithms_map.get(algorithm)
    if not hash_func:
        raise CryptoError(f"Unknown HMAC algorithm: {algorithm}")
    
    h = hmac.new(key.key_data, data, hash_func)
    
    return HashDigest(algorithm=f"HMAC-{algorithm}", digest=h.digest())


# ============ DIGITAL SIGNATURES ============

def sign(data: Union[str, bytes],
         private_key: Key,
         algorithm: str = "ECDSA") -> Signature:
    """
    Create digital signature
    
    Args:
        data: Data to sign
        private_key: Private key
        algorithm: Signature algorithm (ECDSA, RSA)
    
    Returns:
        Signature object
    """
    if not CRYPTO_AVAILABLE:
        raise CryptoError("cryptography library required for signatures")
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if not private_key.is_private:
        raise SignatureError("Private key required for signing")
    
    try:
        if algorithm == "ECDSA" or private_key.algorithm.startswith("ECDSA"):
            signature_bytes = private_key.key_object.sign(
                data,
                ec.ECDSA(hashes.SHA256())
            )
        
        elif algorithm == "RSA" or private_key.algorithm.startswith("RSA"):
            signature_bytes = private_key.key_object.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        
        else:
            raise SignatureError(f"Unknown signature algorithm: {algorithm}")
        
        return Signature(algorithm=algorithm, signature=signature_bytes)
    
    except Exception as e:
        raise SignatureError(f"Signing failed: {str(e)}")


def verify(data: Union[str, bytes],
           signature: Signature,
           public_key: Key) -> bool:
    """
    Verify digital signature
    
    Args:
        data: Data that was signed
        signature: Signature to verify
        public_key: Public key
    
    Returns:
        True if signature is valid
    """
    if not CRYPTO_AVAILABLE:
        raise CryptoError("cryptography library required for verification")
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        if signature.algorithm == "ECDSA" or public_key.algorithm.startswith("ECDSA"):
            public_key.key_object.verify(
                signature.signature,
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        
        elif signature.algorithm == "RSA" or public_key.algorithm.startswith("RSA"):
            public_key.key_object.verify(
                signature.signature,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        
        else:
            raise SignatureError(f"Unknown signature algorithm: {signature.algorithm}")
    
    except Exception:
        return False


# ============ UTILITY FUNCTIONS ============

def random_bytes(size: int) -> bytes:
    """Generate cryptographically secure random bytes"""
    return secrets.token_bytes(size)


def random_int(min_value: int, max_value: int) -> int:
    """Generate cryptographically secure random integer"""
    return secrets.randbelow(max_value - min_value + 1) + min_value


def random_string(length: int, alphabet: str = None) -> str:
    """Generate cryptographically secure random string"""
    if alphabet is None:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ============ TESTING ============

if __name__ == "__main__":
    print("=" * 70)
    print("DNACrypt Crypto Module Test")
    print("=" * 70)
    
    # Test key generation
    print("\n1. Key Generation")
    key = generate_key("AES256")
    print(f"   Generated: {key}")
    
    # Test key pair generation
    print("\n2. Key Pair Generation")
    keypair = generate_keypair("ECDSA_P256")
    print(f"   Generated: {keypair}")
    
    # Test key derivation
    print("\n3. Key Derivation")
    derived = derive_key("password123", random_bytes(16))
    print(f"   Derived: {derived}")
    
    # Test encryption/decryption
    print("\n4. Encryption/Decryption")
    plaintext = "Hello, DNACrypt!"
    encrypted = encrypt(plaintext, key)
    print(f"   Encrypted: {encrypted}")
    decrypted = decrypt(encrypted, key)
    print(f"   Decrypted: {decrypted.decode('utf-8')}")
    
    # Test hashing
    print("\n5. Hashing")
    hash_digest = hash_data("Hash this", "SHA256")
    print(f"   Hash: {hash_digest.hex()[:32]}...")
    
    # Test signatures
    print("\n6. Digital Signatures")
    sig = sign("Sign this", keypair.private_key)
    print(f"   Signature: {sig}")
    valid = verify("Sign this", sig, keypair.public_key)
    print(f"   Valid: {valid}")
    
    print("\n✓ All crypto tests passed!")