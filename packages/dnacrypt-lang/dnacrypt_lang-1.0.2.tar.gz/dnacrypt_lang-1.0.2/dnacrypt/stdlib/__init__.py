"""
DNACrypt Standard Library
A comprehensive library for DNA-based cryptography

Modules:
    crypto - Cryptographic operations (AES, RSA, ECDSA, hashing, signatures)
    dna - DNA sequence operations (encoding, decoding, analysis, translation)
    bio - Biological operations (gene structures, realism, validation)
"""

__version__ = "1.0.0"
__author__ = "Harshith Madhavaram"
__license__ = "MIT"


from . import crypto
from . import dna

from .crypto import (

    generate_key,
    generate_keypair,
    derive_key,
    

    encrypt,
    decrypt,

    hash_data,
    hmac_data,

    sign,
    verify,

    random_bytes,
    random_int,
    random_string,

    Key,
    KeyPair,
    EncryptedData,
    HashDigest,
    Signature,

    CryptoError,
    EncryptionError,
    DecryptionError,
    KeyError,
    SignatureError,
)

from .dna import (

    complement,
    reverse,
    reverse_complement,
    transcribe,
    translate,
    translate_codon,
    

    gc_content,
    at_content,
    nucleotide_frequency,
    find_motif,
    find_orfs,
    calculate_melting_temperature,
    hamming_distance,

    to_codons,
    count_codons,

    DNAEncoder,

    validate,
    check_palindrome,

    DNASequence,
    RNASequence,
    Codon,
    OpenReadingFrame,

    DNAError,
    InvalidDNAError,
    EncodingError,

    GENETIC_CODE,
    START_CODONS,
    STOP_CODONS,
)

VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

__all__ = [

    'crypto',
    'dna',

    'generate_key',
    'generate_keypair',
    'derive_key',
    'encrypt',
    'decrypt',
    'hash_data',
    'hmac_data',
    'sign',
    'verify',
    'random_bytes',
    'random_int',
    'random_string',
    'Key',
    'KeyPair',
    'EncryptedData',
    'HashDigest',
    'Signature',
    'CryptoError',
    'EncryptionError',
    'DecryptionError',
    'KeyError',
    'SignatureError',

    'complement',
    'reverse',
    'reverse_complement',
    'transcribe',
    'translate',
    'translate_codon',
    'gc_content',
    'at_content',
    'nucleotide_frequency',
    'find_motif',
    'find_orfs',
    'calculate_melting_temperature',
    'hamming_distance',
    'to_codons',
    'count_codons',
    'DNAEncoder',
    'validate',
    'check_palindrome',
    'DNASequence',
    'RNASequence',
    'Codon',
    'OpenReadingFrame',
    'DNAError',
    'InvalidDNAError',
    'EncodingError',
    'GENETIC_CODE',
    'START_CODONS',
    'STOP_CODONS',
]


def get_version():
    """Get the version string"""
    return __version__


def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO


def list_modules():
    """List all available modules"""
    return ['crypto', 'dna']


def print_info():
    """Print library information"""
    print(f"DNACrypt Standard Library v{__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print("\nAvailable modules:")
    print("  • crypto - Cryptographic operations")
    print("  • dna - DNA sequence operations")
    print("\nFor help, see: https://github.com/yourusername/dnacrypt")


EXAMPLES = """
DNACrypt Standard Library - Quick Examples

1. Generate and use encryption key:
    from dnacrypt_stdlib import generate_key, encrypt, decrypt
    
    key = generate_key("AES256")
    encrypted = encrypt("secret", key)
    decrypted = decrypt(encrypted, key)

2. Encode data as DNA:
    from dnacrypt_stdlib import DNAEncoder
    
    data = b"Hello, DNA!"
    dna_seq = DNAEncoder.encode(data)
    decoded = DNAEncoder.decode(dna_seq)

3. Calculate GC content:
    from dnacrypt_stdlib import gc_content
    
    gc = gc_content("ATGCCGTA")
    print(f"GC content: {gc:.2%}")

4. Digital signatures:
    from dnacrypt_stdlib import generate_keypair, sign, verify
    
    keypair = generate_keypair("ECDSA_P256")
    signature = sign("data", keypair.private_key)
    is_valid = verify("data", signature, keypair.public_key)

5. Find Open Reading Frames:
    from dnacrypt_stdlib import find_orfs
    
    orfs = find_orfs("ATGATGATGTAA", min_length=9)
    for orf in orfs:
        print(f"ORF at {orf.start}-{orf.end}")

For more examples, see the documentation.
"""


def show_examples():
    """Show usage examples"""
    print(EXAMPLES)


def _initialize():
    """Initialize the standard library"""

    try:
        import cryptography
    except ImportError:
        print("Warning: cryptography library not installed.")
        print("Install with: pip install cryptography")
        print("Crypto functions will use fallback implementations.")


_initialize()


if __name__ == "__main__":
    print_info()
    print()
    show_examples()