"""
DNACrypt Language Interpreter (Execution Engine)
Executes the Abstract Syntax Tree
"""

import hashlib
import hmac
import secrets
import base64
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Cryptography imports
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not installed. Crypto functions will be simulated.")

# ============ RUNTIME VALUES ============

class ValueType(Enum):
    """Types of runtime values"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    NULL = "null"
    DNA = "DNA"
    RNA = "RNA"
    KEY = "Key"
    CIPHER = "Cipher"
    HASH = "Hash"
    SIGNATURE = "Signature"
    CODON = "Codon"
    GENE = "Gene"
    ARRAY = "array"
    DICT = "dict"
    FUNCTION = "function"

@dataclass
class RuntimeValue:
    """Runtime value wrapper"""
    type: ValueType
    value: Any
    
    def __repr__(self):
        return f"RuntimeValue({self.type.value}, {self.value})"

@dataclass
class DNAValue:
    """DNA sequence value"""
    sequence: str
    
    def __repr__(self):
        return f"DNA({self.sequence})"

@dataclass
class CipherValue:
    """Encrypted data"""
    algorithm: str
    data: bytes
    iv: bytes
    tag: Optional[bytes] = None
    
    def __repr__(self):
        return f"Cipher({self.algorithm})"

@dataclass
class KeyValue:
    """Cryptographic key"""
    algorithm: str
    key_data: Any  # Can be bytes or cryptography key object
    is_private: bool = False
    
    def __repr__(self):
        return f"Key({self.algorithm}, private={self.is_private})"

@dataclass
class KeyPair:
    """Public/Private key pair"""
    private: KeyValue
    public: KeyValue
    
    def __repr__(self):
        return f"KeyPair({self.private.algorithm})"

@dataclass
class HashValue:
    """Hash digest"""
    algorithm: str
    digest: bytes
    
    def __repr__(self):
        return f"Hash({self.algorithm})"

@dataclass
class SignatureValue:
    """Digital signature"""
    algorithm: str
    signature: bytes
    
    def __repr__(self):
        return f"Signature({self.algorithm})"

@dataclass
class GeneValue:
    """Gene structure"""
    sequence: str
    metadata: dict
    
    def __repr__(self):
        return f"Gene({self.metadata.get('name', 'unnamed')})"

# ============ EXCEPTIONS ============

class RuntimeError(Exception):
    """Runtime error"""
    pass

class DecryptionError(RuntimeError):
    """Decryption failed"""
    pass

class SignatureError(RuntimeError):
    """Signature verification failed"""
    pass

class InvalidDNAError(RuntimeError):
    """Invalid DNA sequence"""
    pass

class KeyError(RuntimeError):
    """Key operation error"""
    pass

# ============ ENVIRONMENT (SYMBOL TABLE) ============

class Environment:
    """Symbol table for variable storage"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, RuntimeValue] = {}
        self.parent = parent
    
    def define(self, name: str, value: RuntimeValue):
        """Define a variable"""
        self.variables[name] = value
    
    def get(self, name: str) -> RuntimeValue:
        """Get variable value"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: RuntimeValue):
        """Set variable value"""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise RuntimeError(f"Undefined variable: {name}")
    
    def exists(self, name: str) -> bool:
        """Check if variable exists"""
        return name in self.variables or (self.parent and self.parent.exists(name))

# ============ STANDARD LIBRARY - CRYPTO MODULE ============

class CryptoModule:
    """Cryptographic operations"""
    
    @staticmethod
    def generate_key(algorithm: str, size: int = 256) -> KeyValue:
        """Generate symmetric key"""
        if not CRYPTO_AVAILABLE:
            # Simulate key generation
            key_bytes = secrets.token_bytes(size // 8)
            return KeyValue(algorithm, key_bytes, False)
        
        if algorithm.startswith("AES"):
            key_size = int(algorithm[3:]) // 8  # AES256 -> 32 bytes
            key_bytes = secrets.token_bytes(key_size)
            return KeyValue(algorithm, key_bytes, False)
        
        raise RuntimeError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def generate_key_pair(algorithm: str) -> KeyPair:
        """Generate asymmetric key pair"""
        if not CRYPTO_AVAILABLE:
            # Simulate key pair
            private_key = KeyValue(algorithm, secrets.token_bytes(32), True)
            public_key = KeyValue(algorithm, secrets.token_bytes(32), False)
            return KeyPair(private_key, public_key)
        
        if algorithm.startswith("RSA"):
            key_size = int(algorithm[3:])  # RSA4096 -> 4096 bits
            private_key_obj = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            public_key_obj = private_key_obj.public_key()
            
            private_key = KeyValue(algorithm, private_key_obj, True)
            public_key = KeyValue(algorithm, public_key_obj, False)
            return KeyPair(private_key, public_key)
        
        elif algorithm.startswith("ECDSA"):
            # ECDSA_P256, ECDSA_P384
            if "P256" in algorithm:
                curve = ec.SECP256R1()
            elif "P384" in algorithm:
                curve = ec.SECP384R1()
            else:
                curve = ec.SECP256R1()
            
            private_key_obj = ec.generate_private_key(curve, default_backend())
            public_key_obj = private_key_obj.public_key()
            
            private_key = KeyValue(algorithm, private_key_obj, True)
            public_key = KeyValue(algorithm, public_key_obj, False)
            return KeyPair(private_key, public_key)
        
        raise RuntimeError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def derive_key(password: str, salt: bytes, algorithm: str, iterations: int) -> KeyValue:
        """Derive key from password"""
        if not CRYPTO_AVAILABLE:
            # Simulate key derivation
            key_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
            return KeyValue("AES256", key_bytes, False)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key_bytes = kdf.derive(password.encode())
        return KeyValue("AES256", key_bytes, False)
    
    @staticmethod
    def encrypt_aes(plaintext: str, key: KeyValue, mode: str = "GCM") -> CipherValue:
        """Encrypt with AES"""
        if not CRYPTO_AVAILABLE:
            # Simulate encryption
            iv = secrets.token_bytes(16)
            data = plaintext.encode()
            return CipherValue(f"AES-{mode}", data, iv, secrets.token_bytes(16))
        
        plaintext_bytes = plaintext.encode('utf-8')
        iv = secrets.token_bytes(16)
        
        if mode == "GCM":
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
            tag = encryptor.tag
            return CipherValue(f"AES-{mode}", ciphertext, iv, tag)
        
        else:
            # CBC mode
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Padding
            padding_length = 16 - (len(plaintext_bytes) % 16)
            padded = plaintext_bytes + bytes([padding_length] * padding_length)
            
            ciphertext = encryptor.update(padded) + encryptor.finalize()
            return CipherValue(f"AES-{mode}", ciphertext, iv)
    
    @staticmethod
    def decrypt_aes(cipher_value: CipherValue, key: KeyValue) -> str:
        """Decrypt AES"""
        if not CRYPTO_AVAILABLE:
            # Simulate decryption
            return cipher_value.data.decode('utf-8', errors='ignore')
        
        try:
            if "GCM" in cipher_value.algorithm:
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.GCM(cipher_value.iv, cipher_value.tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                plaintext_bytes = decryptor.update(cipher_value.data) + decryptor.finalize()
            else:
                # CBC mode
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.CBC(cipher_value.iv),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                padded = decryptor.update(cipher_value.data) + decryptor.finalize()
                
                # Remove padding
                padding_length = padded[-1]
                plaintext_bytes = padded[:-padding_length]
            
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def hash_data(data: str, algorithm: str) -> HashValue:
        """Hash data"""
        data_bytes = data.encode('utf-8')
        
        if algorithm == "SHA256":
            digest = hashlib.sha256(data_bytes).digest()
        elif algorithm == "SHA3_256":
            digest = hashlib.sha3_256(data_bytes).digest()
        elif algorithm == "SHA3_512":
            digest = hashlib.sha3_512(data_bytes).digest()
        elif algorithm == "BLAKE2b":
            digest = hashlib.blake2b(data_bytes).digest()
        elif algorithm == "BLAKE2s":
            digest = hashlib.blake2s(data_bytes).digest()
        else:
            raise RuntimeError(f"Unsupported hash algorithm: {algorithm}")
        
        return HashValue(algorithm, digest)
    
    @staticmethod
    def hmac_data(data: str, key: KeyValue, algorithm: str) -> HashValue:
        """HMAC"""
        data_bytes = data.encode('utf-8')
        
        if algorithm == "SHA256":
            h = hmac.new(key.key_data, data_bytes, hashlib.sha256)
        elif algorithm == "SHA3_256":
            h = hmac.new(key.key_data, data_bytes, hashlib.sha3_256)
        else:
            raise RuntimeError(f"Unsupported HMAC algorithm: {algorithm}")
        
        return HashValue(f"HMAC-{algorithm}", h.digest())
    
    @staticmethod
    def sign_data(data: str, key: KeyValue, algorithm: str) -> SignatureValue:
        """Sign data"""
        if not CRYPTO_AVAILABLE:
            # Simulate signature
            sig_bytes = hashlib.sha256(data.encode()).digest()
            return SignatureValue(algorithm, sig_bytes)
        
        data_bytes = data.encode('utf-8')
        
        if algorithm == "ECDSA":
            signature = key.key_data.sign(
                data_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return SignatureValue(algorithm, signature)
        
        elif algorithm == "RSA":
            signature = key.key_data.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return SignatureValue(algorithm, signature)
        
        raise RuntimeError(f"Unsupported signature algorithm: {algorithm}")
    
    @staticmethod
    def verify_signature(data: str, signature: SignatureValue, key: KeyValue) -> bool:
        """Verify signature"""
        if not CRYPTO_AVAILABLE:
            # Simulate verification
            return True
        
        data_bytes = data.encode('utf-8')
        
        try:
            if signature.algorithm == "ECDSA":
                key.key_data.verify(
                    signature.signature,
                    data_bytes,
                    ec.ECDSA(hashes.SHA256())
                )
                return True
            
            elif signature.algorithm == "RSA":
                key.key_data.verify(
                    signature.signature,
                    data_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
        except Exception:
            return False
        
        return False
    
    @staticmethod
    def random_bytes(size: int) -> bytes:
        """Generate random bytes"""
        return secrets.token_bytes(size)

# ============ STANDARD LIBRARY - DNA MODULE ============

class DNAModule:
    """DNA operations"""
    
    # DNA encoding mappings
    BINARY_2BIT = {
        '00': 'A', '01': 'T', '10': 'G', '11': 'C'
    }
    
    BINARY_2BIT_REVERSE = {
        'A': '00', 'T': '01', 'G': '10', 'C': '11'
    }
    
    @staticmethod
    def encode(data: bytes, mapping: str) -> DNAValue:
        """Encode binary data to DNA"""
        if mapping == "BINARY_2BIT":
            # Convert bytes to binary string
            binary = ''.join(format(byte, '08b') for byte in data)
            
            # Pad to multiple of 2
            if len(binary) % 2 != 0:
                binary += '0'
            
            # Convert to DNA
            dna_sequence = ''
            for i in range(0, len(binary), 2):
                bits = binary[i:i+2]
                dna_sequence += DNAModule.BINARY_2BIT[bits]
            
            return DNAValue(dna_sequence)
        
        raise RuntimeError(f"Unsupported encoding: {mapping}")
    
    @staticmethod
    def decode(dna: DNAValue, mapping: str) -> bytes:
        """Decode DNA to binary data"""
        if mapping == "BINARY_2BIT":
            # Convert DNA to binary
            binary = ''
            for nucleotide in dna.sequence:
                binary += DNAModule.BINARY_2BIT_REVERSE[nucleotide]
            
            # Convert binary to bytes
            byte_array = bytearray()
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                if len(byte) == 8:
                    byte_array.append(int(byte, 2))
            
            return bytes(byte_array)
        
        raise RuntimeError(f"Unsupported decoding: {mapping}")
    
    @staticmethod
    def complement(sequence: str) -> str:
        """Get complement of DNA sequence"""
        complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return ''.join(complement_map[base] for base in sequence)
    
    @staticmethod
    def reverse(sequence: str) -> str:
        """Reverse DNA sequence"""
        return sequence[::-1]
    
    @staticmethod
    def reverse_complement(sequence: str) -> str:
        """Get reverse complement"""
        return DNAModule.reverse(DNAModule.complement(sequence))
    
    @staticmethod
    def transcribe(sequence: str) -> str:
        """Transcribe DNA to RNA (T -> U)"""
        return sequence.replace('T', 'U')
    
    @staticmethod
    def gc_content(sequence: str) -> float:
        """Calculate GC content"""
        if not sequence:
            return 0.0
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence)
    
    @staticmethod
    def validate(sequence: str) -> bool:
        """Check if valid DNA sequence"""
        return all(base in 'ATGC' for base in sequence.upper())
    
    @staticmethod
    def length(sequence: str) -> int:
        """Get sequence length"""
        return len(sequence)
    
    @staticmethod
    def to_codons(sequence: str) -> list:
        """Split into codons"""
        codons = []
        for i in range(0, len(sequence), 3):
            codon = sequence[i:i+3]
            if len(codon) == 3:
                codons.append(codon)
        return codons
    
    @staticmethod
    def find_motif(sequence: str, motif: str) -> list:
        """Find motif positions"""
        positions = []
        for i in range(len(sequence) - len(motif) + 1):
            if sequence[i:i+len(motif)] == motif:
                positions.append(i)
        return positions
    
    @staticmethod
    def find_orfs(sequence: str) -> list:
        """Find open reading frames"""
        orfs = []
        start_codon = "ATG"
        stop_codons = ["TAA", "TAG", "TGA"]
        
        # Find all start codons
        for i in range(len(sequence) - 2):
            if sequence[i:i+3] == start_codon:
                # Look for stop codon in frame
                for j in range(i + 3, len(sequence) - 2, 3):
                    if sequence[j:j+3] in stop_codons:
                        orfs.append({
                            'start': i,
                            'end': j + 3,
                            'length': j + 3 - i,
                            'sequence': sequence[i:j+3]
                        })
                        break
        
        return orfs

# ============ STANDARD LIBRARY - BIO MODULE ============

class BioModule:
    """Biological operations"""
    
    @staticmethod
    def adjust_gc_content(sequence: str, target: float) -> str:
        """Adjust GC content (simplified)"""
        current_gc = DNAModule.gc_content(sequence)
        
        if abs(current_gc - target) < 0.01:
            return sequence
        
        # Simplified adjustment - in real implementation would be more sophisticated
        return sequence
    
    @staticmethod
    def make_realistic(sequence: str, config: dict) -> DNAValue:
        """Make DNA sequence biologically realistic"""
        result = sequence
        
        # Add gene structure if requested
        if config.get('add_structure', False):
            # Add 5' UTR
            utr5 = "GCCGCCACC"
            # Add start codon
            start = "ATG"
            # Add stop codon at end
            stop = "TAA"
            # Add 3' UTR
            utr3 = "AATAAA"
            
            result = utr5 + start + result + stop + utr3
        
        # Adjust GC content
        target_gc = config.get('gc_content', 0.5)
        result = BioModule.adjust_gc_content(result, target_gc)
        
        return DNAValue(result)
    
    @staticmethod
    def create_gene(sequence: str, metadata: dict) -> GeneValue:
        """Create gene with metadata"""
        return GeneValue(sequence, metadata)
    
    @staticmethod
    def realism_score(sequence: str) -> float:
        """Calculate biological realism score"""
        score = 1.0
        
        # Check GC content (should be 0.4-0.6)
        gc = DNAModule.gc_content(sequence)
        if gc < 0.4 or gc > 0.6:
            score -= 0.3
        
        # Check for start/stop codons
        has_start = "ATG" in sequence
        has_stop = any(stop in sequence for stop in ["TAA", "TAG", "TGA"])
        if not (has_start and has_stop):
            score -= 0.2
        
        return max(0.0, score)

# ============ INTERPRETER ============

class DNACryptInterpreter:
    """DNACrypt language interpreter"""
    
    def __init__(self):
        self.global_env = Environment()
        self.crypto = CryptoModule()
        self.dna = DNAModule()
        self.bio = BioModule()
        
        # Setup built-in functions
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions and modules"""
        # Built-in modules
        self.global_env.define("crypto", RuntimeValue(ValueType.DICT, self.crypto))
        self.global_env.define("dna", RuntimeValue(ValueType.DICT, self.dna))
        self.global_env.define("bio", RuntimeValue(ValueType.DICT, self.bio))
        self.global_env.define("DNA", RuntimeValue(ValueType.DICT, self.dna))
        
        # DNA constants
        self.global_env.define("BINARY_2BIT", RuntimeValue(ValueType.STRING, "BINARY_2BIT"))
        self.global_env.define("BINARY_3BIT", RuntimeValue(ValueType.STRING, "BINARY_3BIT"))
        self.global_env.define("CODON_TABLE", RuntimeValue(ValueType.STRING, "CODON_TABLE"))
        
        # Crypto constants
        self.global_env.define("AES128", RuntimeValue(ValueType.STRING, "AES128"))
        self.global_env.define("AES256", RuntimeValue(ValueType.STRING, "AES256"))
        self.global_env.define("RSA2048", RuntimeValue(ValueType.STRING, "RSA2048"))
        self.global_env.define("RSA4096", RuntimeValue(ValueType.STRING, "RSA4096"))
        self.global_env.define("ECDSA_P256", RuntimeValue(ValueType.STRING, "ECDSA_P256"))
        self.global_env.define("ECDSA_P384", RuntimeValue(ValueType.STRING, "ECDSA_P384"))
        self.global_env.define("ECDSA", RuntimeValue(ValueType.STRING, "ECDSA"))
        
        # Hash algorithms
        self.global_env.define("SHA256", RuntimeValue(ValueType.STRING, "SHA256"))
        self.global_env.define("SHA3_256", RuntimeValue(ValueType.STRING, "SHA3_256"))
        self.global_env.define("SHA3_512", RuntimeValue(ValueType.STRING, "SHA3_512"))
        self.global_env.define("BLAKE2b", RuntimeValue(ValueType.STRING, "BLAKE2b"))
        
        # KDF
        self.global_env.define("PBKDF2", RuntimeValue(ValueType.STRING, "PBKDF2"))
        
        # Modes
        self.global_env.define("GCM", RuntimeValue(ValueType.STRING, "GCM"))
        self.global_env.define("CBC", RuntimeValue(ValueType.STRING, "CBC"))
        
        # Special
        self.global_env.define("autoGenerate", RuntimeValue(ValueType.STRING, "autoGenerate"))
    
    def interpret(self, ast):
        """Interpret the AST"""
        from .parser import Program
        
        if isinstance(ast, Program):
            result = None
            for statement in ast.statements:
                result = self.eval_node(statement, self.global_env)
            return result
        else:
            return self.eval_node(ast, self.global_env)
    
    def eval_node(self, node, env: Environment):
        """Evaluate an AST node"""
        from .parser import (
            VariableDeclaration, Assignment, FunctionDeclaration,
            ReturnStatement, IfStatement, WhileStatement, ForStatement,
            TryStatement, ThrowStatement, BreakStatement, ContinueStatement,
            ImportStatement, ExportStatement, BinaryOperation, UnaryOperation,
            FunctionCall, MethodCall, MemberAccess, IndexAccess,
            StringLiteral, NumberLiteral, DNALiteral, BooleanLiteral,
            NullLiteral, Identifier, DictionaryLiteral, ArrayLiteral
        )
        
        # Statements
        if isinstance(node, VariableDeclaration):
            return self.eval_variable_declaration(node, env)
        
        elif isinstance(node, Assignment):
            return self.eval_assignment(node, env)
        
        elif isinstance(node, FunctionCall):
            return self.eval_function_call(node, env)
        
        elif isinstance(node, MethodCall):
            return self.eval_method_call(node, env)
        
        elif isinstance(node, IfStatement):
            return self.eval_if_statement(node, env)
        
        elif isinstance(node, WhileStatement):
            return self.eval_while_statement(node, env)
        
        elif isinstance(node, ReturnStatement):
            if node.value:
                return ('return', self.eval_node(node.value, env))
            return ('return', RuntimeValue(ValueType.NULL, None))
        
        # Expressions
        elif isinstance(node, BinaryOperation):
            return self.eval_binary_operation(node, env)
        
        elif isinstance(node, UnaryOperation):
            return self.eval_unary_operation(node, env)
        
        elif isinstance(node, MemberAccess):
            return self.eval_member_access(node, env)
        
        # Literals
        elif isinstance(node, StringLiteral):
            return RuntimeValue(ValueType.STRING, node.value)
        
        elif isinstance(node, NumberLiteral):
            return RuntimeValue(ValueType.NUMBER, node.value)
        
        elif isinstance(node, DNALiteral):
            return RuntimeValue(ValueType.DNA, DNAValue(node.sequence))
        
        elif isinstance(node, BooleanLiteral):
            return RuntimeValue(ValueType.BOOLEAN, node.value)
        
        elif isinstance(node, NullLiteral):
            return RuntimeValue(ValueType.NULL, None)
        
        elif isinstance(node, Identifier):
            return env.get(node.name)
        
        elif isinstance(node, DictionaryLiteral):
            return self.eval_dictionary(node, env)
        
        elif isinstance(node, ArrayLiteral):
            return self.eval_array(node, env)
        
        elif isinstance(node, ImportStatement):
            # Import is already handled in builtins
            return RuntimeValue(ValueType.NULL, None)
        
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def eval_variable_declaration(self, node, env):
        """Evaluate variable declaration"""
        value = None
        if node.initializer:
            value = self.eval_node(node.initializer, env)
        else:
            value = RuntimeValue(ValueType.NULL, None)
        
        env.define(node.name, value)
        return value
    
    def eval_assignment(self, node, env):
        """Evaluate assignment"""
        value = self.eval_node(node.value, env)
        
        if node.operator == '=':
            env.set(node.name, value)
        elif node.operator == '+=':
            current = env.get(node.name)
            if current.type == ValueType.NUMBER and value.type == ValueType.NUMBER:
                env.set(node.name, RuntimeValue(ValueType.NUMBER, current.value + value.value))
        # Add other compound assignments as needed
        
        return value
    
    def eval_function_call(self, node, env):
        """Evaluate function call"""
        # Evaluate arguments
        args = [self.eval_node(arg, env) for arg in node.arguments]
        named_args = {name: self.eval_node(val, env) for name, val in node.named_arguments.items()}
        
        # Built-in functions
        if node.name == "generate":
            # generate(AES256)
            algorithm = args[0].value
            return RuntimeValue(ValueType.KEY, self.crypto.generate_key(algorithm))
        
        elif node.name == "generate_pair":
            # generate_pair(RSA4096)
            algorithm = args[0].value
            keypair = self.crypto.generate_key_pair(algorithm)
            return RuntimeValue(ValueType.DICT, keypair)
        
        elif node.name == "derive_key":
            # derive_key(password: "pass", salt: bytes, algorithm: PBKDF2, iterations: 100000)
            password = named_args['password'].value
            salt = named_args['salt'].value
            algorithm = named_args['algorithm'].value
            iterations = named_args['iterations'].value
            key = self.crypto.derive_key(password, salt, algorithm, iterations)
            return RuntimeValue(ValueType.KEY, key)
        
        elif node.name == "random_bytes":
            # random_bytes(32)
            size = args[0].value
            return RuntimeValue(ValueType.STRING, self.crypto.random_bytes(size))
        
        elif node.name == "AES256" or node.name == "AES128":
            # AES256(plaintext, key: key, mode: GCM)
            plaintext = args[0].value
            key = named_args['key'].value
            mode = named_args.get('mode', RuntimeValue(ValueType.STRING, "GCM")).value
            cipher = self.crypto.encrypt_aes(plaintext, key, mode)
            return RuntimeValue(ValueType.CIPHER, cipher)
        
        elif node.name == "decrypt":
            # decrypt(cipher, key: key)
            cipher = args[0].value
            key = named_args['key'].value
            plaintext = self.crypto.decrypt_aes(cipher, key)
            return RuntimeValue(ValueType.STRING, plaintext)
        
        elif node.name == "SHA256" or node.name in ["SHA3_256", "BLAKE2b"]:
            # SHA256(data)
            data = args[0].value
            hash_val = self.crypto.hash_data(data, node.name)
            return RuntimeValue(ValueType.HASH, hash_val)
        
        elif node.name == "SIGN":
            # SIGN(data, key: private_key, algorithm: ECDSA)
            data = args[0].value if isinstance(args[0].value, str) else args[0].value.sequence
            key = named_args['key'].value
            algorithm = named_args['algorithm'].value
            sig = self.crypto.sign_data(data, key, algorithm)
            return RuntimeValue(ValueType.SIGNATURE, sig)
        
        elif node.name == "VERIFY":
            # VERIFY(data, signature: sig, key: public_key)
            data = args[0].value if isinstance(args[0].value, str) else args[0].value.sequence
            signature = named_args['signature'].value
            key = named_args['key'].value
            result = self.crypto.verify_signature(data, signature, key)
            return RuntimeValue(ValueType.BOOLEAN, result)
        
        elif node.name == "print":
            # print(value)
            for arg in args:
                print(self._format_value(arg))
            return RuntimeValue(ValueType.NULL, None)
        
        else:
            raise RuntimeError(f"Unknown function: {node.name}")
    
    def eval_method_call(self, node, env):
        """Evaluate method call"""
        obj = self.eval_node(node.object, env)
        
        # Evaluate arguments
        args = [self.eval_node(arg, env) for arg in node.arguments]
        named_args = {name: self.eval_node(val, env) for name, val in node.named_arguments.items()}
        
        # DNA module methods
        if obj.value is self.dna or str(type(obj.value).__name__) == 'DNAModule':
            if node.method == "encode":
                # DNA.encode(data, mapping: BINARY_2BIT)
                data = args[0].value
                mapping = named_args['mapping'].value
                
                # Convert to bytes if needed
                if isinstance(data, CipherValue):
                    data_bytes = data.data
                elif isinstance(data, str):
                    data_bytes = data.encode('utf-8')
                else:
                    data_bytes = data
                
                dna = self.dna.encode(data_bytes, mapping)
                return RuntimeValue(ValueType.DNA, dna)
            
            elif node.method == "decode":
                # DNA.decode(dna, mapping: BINARY_2BIT)
                dna = args[0].value
                mapping = named_args['mapping'].value
                data = self.dna.decode(dna, mapping)
                return RuntimeValue(ValueType.STRING, data)
            
            elif node.method == "gc_content":
                # DNA.gc_content(sequence)
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else args[0].value
                gc = self.dna.gc_content(sequence)
                return RuntimeValue(ValueType.NUMBER, gc)
            
            elif node.method == "complement":
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else str(args[0].value)
                result = self.dna.complement(sequence)
                return RuntimeValue(ValueType.DNA, DNAValue(result))
            
            elif node.method == "reverse_complement":
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else str(args[0].value)
                result = self.dna.reverse_complement(sequence)
                return RuntimeValue(ValueType.DNA, DNAValue(result))
            
            elif node.method == "find_orfs":
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else args[0].value
                orfs = self.dna.find_orfs(sequence)
                return RuntimeValue(ValueType.ARRAY, orfs)
        
        # Bio module methods
        elif obj.value is self.bio or str(type(obj.value).__name__) == 'BioModule':
            if node.method == "make_realistic":
                # bio.make_realistic(sequence, config: {...})
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else args[0].value
                config = named_args['config'].value
                result = self.bio.make_realistic(sequence, config)
                return RuntimeValue(ValueType.DNA, result)
            
            elif node.method == "create_gene":
                sequence = args[0].value
                metadata = named_args['metadata'].value
                gene = self.bio.create_gene(sequence, metadata)
                return RuntimeValue(ValueType.GENE, gene)
            
            elif node.method == "realism_score":
                sequence = args[0].value.sequence if isinstance(args[0].value, DNAValue) else args[0].value
                score = self.bio.realism_score(sequence)
                return RuntimeValue(ValueType.NUMBER, score)
        
        raise RuntimeError(f"Unknown method: {node.method}")
    
    def eval_binary_operation(self, node, env):
        """Evaluate binary operation"""
        left = self.eval_node(node.left, env)
        right = self.eval_node(node.right, env)
        
        if node.operator == '+':
            return RuntimeValue(ValueType.NUMBER, left.value + right.value)
        elif node.operator == '-':
            return RuntimeValue(ValueType.NUMBER, left.value - right.value)
        elif node.operator == '*':
            return RuntimeValue(ValueType.NUMBER, left.value * right.value)
        elif node.operator == '/':
            return RuntimeValue(ValueType.NUMBER, left.value / right.value)
        elif node.operator == '**':
            return RuntimeValue(ValueType.NUMBER, left.value ** right.value)
        elif node.operator == '%':
            return RuntimeValue(ValueType.NUMBER, left.value % right.value)
        elif node.operator == '==':
            return RuntimeValue(ValueType.BOOLEAN, left.value == right.value)
        elif node.operator == '!=':
            return RuntimeValue(ValueType.BOOLEAN, left.value != right.value)
        elif node.operator == '<':
            return RuntimeValue(ValueType.BOOLEAN, left.value < right.value)
        elif node.operator == '>':
            return RuntimeValue(ValueType.BOOLEAN, left.value > right.value)
        elif node.operator == '<=':
            return RuntimeValue(ValueType.BOOLEAN, left.value <= right.value)
        elif node.operator == '>=':
            return RuntimeValue(ValueType.BOOLEAN, left.value >= right.value)
        elif node.operator == '&&':
            return RuntimeValue(ValueType.BOOLEAN, left.value and right.value)
        elif node.operator == '||':
            return RuntimeValue(ValueType.BOOLEAN, left.value or right.value)
        
        raise RuntimeError(f"Unknown operator: {node.operator}")
    
    def eval_unary_operation(self, node, env):
        """Evaluate unary operation"""
        operand = self.eval_node(node.operand, env)
        
        if node.operator == '-':
            return RuntimeValue(ValueType.NUMBER, -operand.value)
        elif node.operator == '!':
            return RuntimeValue(ValueType.BOOLEAN, not operand.value)
        
        raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def eval_member_access(self, node, env):
        """Evaluate member access"""
        obj = self.eval_node(node.object, env)
        
        # Access dictionary member
        if obj.type == ValueType.DICT:
            if isinstance(obj.value, KeyPair):
                if node.member == 'private':
                    return RuntimeValue(ValueType.KEY, obj.value.private)
                elif node.member == 'public':
                    return RuntimeValue(ValueType.KEY, obj.value.public)
            elif isinstance(obj.value, dict):
                return RuntimeValue(ValueType.STRING, obj.value[node.member])
        
        # Access gene members
        elif obj.type == ValueType.GENE:
            if node.member == 'sequence':
                return RuntimeValue(ValueType.DNA, DNAValue(obj.value.sequence))
            elif node.member == 'metadata':
                return RuntimeValue(ValueType.DICT, obj.value.metadata)
        
        # Module access (DNA, bio, crypto)
        elif obj.value == self.dna:
            return RuntimeValue(ValueType.DICT, self.dna)
        elif obj.value == self.bio:
            return RuntimeValue(ValueType.DICT, self.bio)
        
        raise RuntimeError(f"Cannot access member: {node.member}")
    
    def eval_if_statement(self, node, env):
        """Evaluate if statement"""
        condition = self.eval_node(node.condition, env)
        
        if condition.value:
            for stmt in node.then_block:
                result = self.eval_node(stmt, env)
                if isinstance(result, tuple) and result[0] == 'return':
                    return result
        elif node.else_block:
            for stmt in node.else_block:
                result = self.eval_node(stmt, env)
                if isinstance(result, tuple) and result[0] == 'return':
                    return result
        
        return RuntimeValue(ValueType.NULL, None)
    
    def eval_while_statement(self, node, env):
        """Evaluate while statement"""
        while True:
            condition = self.eval_node(node.condition, env)
            if not condition.value:
                break
            
            for stmt in node.body:
                result = self.eval_node(stmt, env)
                if isinstance(result, tuple) and result[0] == 'return':
                    return result
        
        return RuntimeValue(ValueType.NULL, None)
    
    def eval_dictionary(self, node, env):
        """Evaluate dictionary literal"""
        result = {}
        for key, value in node.pairs:
            result[key] = self.eval_node(value, env).value
        return RuntimeValue(ValueType.DICT, result)
    
    def eval_array(self, node, env):
        """Evaluate array literal"""
        result = [self.eval_node(elem, env).value for elem in node.elements]
        return RuntimeValue(ValueType.ARRAY, result)
    
    def _format_value(self, value: RuntimeValue) -> str:
        """Format value for printing"""
        if value.type == ValueType.STRING:
            return value.value
        elif value.type == ValueType.NUMBER:
            return str(value.value)
        elif value.type == ValueType.BOOLEAN:
            return str(value.value)
        elif value.type == ValueType.DNA:
            # Don't print if it's an empty DNA value
            if hasattr(value.value, 'sequence') and value.value.sequence:
                return f"DNA({value.value.sequence})"
            return ""
        elif value.type == ValueType.KEY:
            return f"Key({value.value.algorithm})"
        elif value.type == ValueType.CIPHER:
            return f"Cipher({value.value.algorithm})"
        elif value.type == ValueType.HASH:
            return f"Hash({value.value.algorithm}, {value.value.digest.hex()[:16]}...)"
        elif value.type == ValueType.SIGNATURE:
            return f"Signature({value.value.algorithm})"
        else:
            return str(value.value)


if __name__ == "__main__":
    print("=" * 70)
    print("DNACrypt Interpreter - Execution Engine")
    print("=" * 70)
    print("\nThe interpreter is ready!")
    print("\nTo use:")
    print("""
from .lexer import DNACryptLexer
from .parser import DNACryptParser
from .interpreter import DNACryptInterpreter

code = '''
let message = "Hello World"
let key = generate(AES256)
let encrypted = AES256(message, key: key, mode: GCM)
print(encrypted)
'''

lexer = DNACryptLexer(code)
tokens = lexer.tokenize()

parser = DNACryptParser(tokens)
ast = parser.parse()

interpreter = DNACryptInterpreter()
interpreter.interpret(ast)
""")