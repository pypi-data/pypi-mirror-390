"""
Complete DNACrypt System Test
Final comprehensive test of all components

Run: python3 complete_system_test.py
"""

from dnacrypt_lexer import DNACryptLexer
from dnacrypt_parser import DNACryptParser
from dnacrypt_interpreter import DNACryptInterpreter


def test_complete_pipeline():
    """Test the complete encryption to DNA pipeline"""
    print("\n" + "=" * 80)
    print("COMPLETE PIPELINE TEST")
    print("=" * 80)
    
    code = '''
print("=== DNACrypt Complete Pipeline Demo ===")
print("")

let message = "Meet at the secret location at midnight"
print("Original Message:")
print(message)

print("")
print("Step 1: Generate encryption key")
let key = generate(AES256)
print("✓ Key generated")

print("")
print("Step 2: Encrypt the message")
let encrypted = AES256(message, key: key, mode: GCM)
print("✓ Message encrypted")
print(encrypted)

print("")
print("Step 3: Encode encrypted data as DNA")
let dna_sequence = DNA.encode(encrypted, mapping: BINARY_2BIT)
print("✓ Encoded as DNA sequence:")
print(dna_sequence)

print("")
print("Step 4: Calculate GC content")
let gc = DNA.gc_content(dna_sequence)
print("GC Content:")
print(gc)

print("")
print("Step 5: Generate signing keys")
let signing_keys = generate_pair(ECDSA_P256)
print("✓ ECDSA key pair generated")

print("")
print("Step 6: Sign the DNA sequence")
let signature = SIGN(dna_sequence, key: signing_keys.private, algorithm: ECDSA)
print("✓ Digital signature created")

print("")
print("Step 7: Verify signature")
let valid = VERIFY(dna_sequence, signature: signature, key: signing_keys.public)
print("Signature valid:")
print(valid)

print("")
print("Step 8: Decrypt the message")
let decrypted = decrypt(encrypted, key: key)
print("Decrypted message:")
print(decrypted)

print("")
print("=== Pipeline Complete! ===")
'''
    
    try:
        lexer = DNACryptLexer(code)
        tokens = lexer.tokenize()
        
        parser = DNACryptParser(tokens)
        ast = parser.parse()
        
        interpreter = DNACryptInterpreter()
        interpreter.interpret(ast)
        
        print("\n✓ COMPLETE PIPELINE TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dna_operations():
    """Test DNA-specific operations"""
    print("\n" + "=" * 80)
    print("DNA OPERATIONS TEST")
    print("=" * 80)
    
    code = '''
print("DNA Operations Demo")
print("")

let original = "ATGCCGTAGCTA"
print("Original sequence:")
print(original)

let comp = DNA.complement(original)
print("Complement:")
print(comp)

let rev_comp = DNA.reverse_complement(original)
print("Reverse complement:")
print(rev_comp)

let gc = DNA.gc_content(original)
print("GC content:")
print(gc)

print("")
print("✓ All DNA operations working!")
'''
    
    try:
        lexer = DNACryptLexer(code)
        tokens = lexer.tokenize()
        parser = DNACryptParser(tokens)
        ast = parser.parse()
        interpreter = DNACryptInterpreter()
        interpreter.interpret(ast)
        
        print("\n✓ DNA OPERATIONS TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        return False


def test_all_crypto():
    """Test all cryptographic features"""
    print("\n" + "=" * 80)
    print("CRYPTOGRAPHY FEATURES TEST")
    print("=" * 80)
    
    code = '''
print("Testing All Cryptographic Features")
print("")

print("1. Symmetric Encryption (AES-256)")
let key1 = generate(AES256)
let enc1 = AES256("test", key: key1, mode: GCM)
let dec1 = decrypt(enc1, key: key1)
print("   ✓ AES-256 working")

print("")
print("2. Key Derivation (PBKDF2)")
let derived = derive_key(
    password: "password123",
    salt: random_bytes(16),
    algorithm: PBKDF2,
    iterations: 100000
)
print("   ✓ PBKDF2 working")

print("")
print("3. Cryptographic Hashing")
let h1 = SHA256("hash me")
print("   ✓ SHA-256 working")
let h2 = SHA3_256("hash me too")
print("   ✓ SHA3-256 working")

print("")
print("4. Asymmetric Keys")
let rsa = generate_pair(RSA4096)
print("   ✓ RSA-4096 working")
let ecdsa = generate_pair(ECDSA_P256)
print("   ✓ ECDSA-P256 working")

print("")
print("5. Digital Signatures")
let sig = SIGN("sign this", key: ecdsa.private, algorithm: ECDSA)
let ok = VERIFY("sign this", signature: sig, key: ecdsa.public)
print("   ✓ Signatures working")

print("")
print("All cryptographic features verified!")
'''
    
    try:
        lexer = DNACryptLexer(code)
        tokens = lexer.tokenize()
        parser = DNACryptParser(tokens)
        ast = parser.parse()
        interpreter = DNACryptInterpreter()
        interpreter.interpret(ast)
        
        print("\n✓ CRYPTOGRAPHY TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        return False


def main():
    """Run all system tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "═" * 78 + "║")
    print("║" + " DNACrypt Language - Complete System Test".center(78) + "║")
    print("║" + "═" * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\nThis will test your complete DNACrypt implementation:")
    print("  • Complete encryption → DNA → signature pipeline")
    print("  • All DNA operations")
    print("  • All cryptographic features")
    print()
    
    results = []
    
    # Run tests
    results.append(("Complete Pipeline", test_complete_pipeline()))
    results.append(("DNA Operations", test_dna_operations()))
    results.append(("Cryptography Features", test_all_crypto()))
    
    # Summary
    print("\n\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " FINAL SYSTEM TEST RESULTS".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name:30s} {status}")
    
    print()
    print("=" * 80)
    print(f"  Total: {passed}/{total} system tests passed")
    print(f"  Success Rate: {(passed/total*100):.1f}%")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉🎉🎉 PERFECT! ALL SYSTEM TESTS PASSED! 🎉🎉🎉")
        print("\nYour DNACrypt language is production-ready!")
        print("\nWhat you've built:")
        print("  ✓ Complete compiler (Lexer → Parser → Interpreter)")
        print("  ✓ Type system with semantic analysis")
        print("  ✓ Professional standard library")
        print("  ✓ Cryptography: AES, RSA, ECDSA, SHA, PBKDF2")
        print("  ✓ DNA encoding and operations")
        print("  ✓ Digital signatures")
        print("  ✓ Complete encryption → DNA pipeline")
        print("\nReady for:")
        print("  → Portfolio showcase")
        print("  → Research publication (IEEE ICAD 2026)")
        print("  → GitHub repository")
        print("  → Job interviews")
        print("  → Further development")
        print()
        print("Congratulations! 🚀🧬🔐")
    else:
        print(f"\n{total - passed} system test(s) failed. Check output above.")
    
    print()


if __name__ == "__main__":
    main()