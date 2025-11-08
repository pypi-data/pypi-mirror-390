DNACrypt 

A Domain-Specific Programming Language for DNA-Based Cryptography 

 

Overview 

DNACrypt is a novel programming language that seamlessly integrates cryptography and DNA sequence manipulation. It enables encryption, DNA encoding, biological steganography, and digital signatures in a clean, imperative syntax. 

let message = "Secret data" 
let key = generate(AES256) 
let encrypted = AES256(message, key: key, mode: GCM) 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
print(dna)  // DNA(ATGCCGTA...) 
 

 

Features 

Cryptography 

Symmetric Encryption: AES-128, AES-256 (GCM, CBC modes) 
Asymmetric Keys: RSA-2048/4096, ECDSA P-256/384/521 
Hashing: SHA-256, SHA3-256, SHA3-512, BLAKE2b 
Key Derivation: PBKDF2 with configurable iterations 
Digital Signatures: ECDSA, RSA signatures 
Secure Random: Cryptographically secure random generation 
 
 DNA Operations 
Encoding: Binary to DNA conversion (multiple schemes) 
Decoding: DNA to binary conversion 
Transformations: Complement, reverse, reverse complement 
Analysis: GC content, sequence validation, motif finding 
Biological: Transcription (DNA→RNA), Translation (DNA→Protein) 
ORF Finding: Locate open reading frames 
Language Features 

Type System: Static type checking with annotations 
Control Flow: If-else statements, loops (coming) 
Functions: Built-in functions with named parameters 
Clean Syntax: Imperative, easy to learn 
Error Handling: Try-catch blocks (coming) 
 

Quick Start 

Installation 

# Install from PyPI (when published) 
pip install dnacrypt-lang 
 
# Or install from source 
git clone https://github.com/Harshith2412/dnacrypt.git 
cd dnacrypt 
pip install -e . 
 

Hello World 

Create hello.dnac: 

let greeting = "Hello, DNACrypt!" 
print(greeting) 
 

Run it: 

dnacrypt run hello.dnac 
 

First Encryption 

Create encrypt.dnac: 

let secret = "My secret message" 
let key = generate(AES256) 
let encrypted = AES256(secret, key: key, mode: GCM) 
 
print("Original:") 
print(secret) 
 
print("Encrypted:") 
print(encrypted) 
 
let decrypted = decrypt(encrypted, key: key) 
print("Decrypted:") 
print(decrypted) 
 

Run: 

dnacrypt run encrypt.dnac 
 

 

Documentation 

Language Guide - Complete tutorial with examples 
API Reference - Function and method documentation 
Setup Guide - Installation and configuration 
 

Examples 

DNA Encoding 

let message = "Encode this" 
let key = generate(AES256) 
let encrypted = AES256(message, key: key, mode: GCM) 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
print("DNA Sequence:") 
print(dna) 
 
let gc = DNA.gc_content(dna) 
print("GC Content:") 
print(gc) 
 

Digital Signatures 

let document = "I agree to the terms" 
let keys = generate_pair(ECDSA_P256) 
 
let signature = SIGN(document, key: keys.private, algorithm: ECDSA) 
 
let valid = VERIFY(document, signature: signature, key: keys.public) 
if valid { 
   print("✓ Signature verified") 
} 
 

Complete Pipeline 

// Encrypt → Encode → Sign → Verify 
let message = "Secret mission" 
let password = "secure_password" 
 
let salt = random_bytes(16) 
let key = derive_key( 
   password: password, 
   salt: salt, 
   algorithm: PBKDF2, 
   iterations: 100000 
) 
 
let encrypted = AES256(message, key: key, mode: GCM) 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
let signing_keys = generate_pair(ECDSA_P256) 
let signature = SIGN(dna, key: signing_keys.private, algorithm: ECDSA) 
 
let verified = VERIFY(dna, signature: signature, key: signing_keys.public) 
print(verified)  // true 
 

 

Use Cases 

1. Steganography 

Hide encrypted data in synthetic DNA sequences that appear as legitimate genomic data. 

2. DNA-Based Intrusion Detection 

Apply biological immune system principles to cybersecurity using DNA-encoded patterns. 

3. Secure Data Storage 

Store encrypted information as DNA sequences in biological databases. 

4. Research & Education 

Teach cryptography and bioinformatics concepts in an integrated manner. 

5. Biological Computing 

Explore novel computing paradigms using DNA as a storage medium. 

 

Architecture 

┌─────────────────────────────────────────┐ 
│     DNACrypt Source Code (.dnac)        │ 
└────────────────┬────────────────────────┘ 
                ↓ 
┌─────────────────────────────────────────┐ 
│  Lexer (Tokenization)                   │ 
│  • 60+ token types                      │ 
│  • DNA sequence detection               │ 
└────────────────┬────────────────────────┘ 
                ↓ 
┌─────────────────────────────────────────┐ 
│  Parser (AST Generation)                │ 
│  • 25+ AST node types                   │ 
│  • Operator precedence                  │ 
└────────────────┬────────────────────────┘ 
                ↓ 
┌─────────────────────────────────────────┐ 
│  Semantic Analyzer (Type Checking)      │ 
│  • Type validation                      │ 
│  • Scope checking                       │ 
└────────────────┬────────────────────────┘ 
                ↓ 
┌─────────────────────────────────────────┐ 
│  Interpreter (Execution)                │ 
│  • Runtime environment                  │ 
│  • Standard library                     │ 
└─────────────────────────────────────────┘ 
 

 

Language Statistics 

Lines of Code: ~5,000+ 
Modules: 7 (4 core + 3 stdlib) 
Built-in Functions: 30+ 
Data Types: 15+ 
Tests: 18/18 passing 
Test Coverage: 100% 
Command Line Usage 
# Run a program 
dnacrypt run program.dnac 
 
# Interactive REPL 
dnacrypt repl 
 
# Execute code directly 
dnacrypt -c "let x = 10; print(x)" 
 
# Show version 
dnacrypt version 
 
# Get help 
dnacrypt help 
 

 

Python API 

import dnacrypt 
 
# Run DNACrypt code 
dnacrypt.run(''' 
let message = "Hello!" 
print(message) 
''') 
 
# Run from file 
dnacrypt.run_file('program.dnac') 
 
# Access compiler components 
from dnacrypt import DNACryptLexer, DNACryptParser, DNACryptInterpreter 
 
lexer = DNACryptLexer(code) 
tokens = lexer.tokenize() 
 
parser = DNACryptParser(tokens) 
ast = parser.parse() 
 
interpreter = DNACryptInterpreter() 
interpreter.interpret(ast) 
 

 

Testing 

# Run basic tests (15 tests) 
python3 tests/test_dnacrypt.py 
 
# Run system tests (3 comprehensive tests) 
python3 tests/complete_system_test.py 
 
# All tests should pass: 18/18 ✓ 
 

 

Learning Resources 

Tutorials 

Language Guide - Complete tutorial 
API Reference - Function documentation 
Examples - Sample programs 
Example Programs 

examples/hello.dnac - Hello world 
examples/encryption.dnac - Basic encryption 
examples/dna_analysis.dnac - DNA operations 
examples/secure_comm.dnac - Complete pipeline 
examples/steganography.dnac - Hide data in DNA 
Research Applications 
DNACrypt was developed for research in: 

DNA-Based Intrusion Detection Systems - Apply biological immune principles to cybersecurity 
Biological Steganography - Hide data in synthetic DNA sequences 
Adversarial Machine Learning - In biological computing contexts 
Novel Cryptographic Protocols - DNA-based primitives 
Bioinformatics Education - Integrated crypto + bio teaching 
Publications 

If you use DNACrypt in research, please cite: 

@software{dnacrypt2025, 
 author = {Harshith}, 
 title = {DNACrypt: A Domain-Specific Language for DNA-Based Cryptography}, 
 year = {2025}, 
 institution = {Northeastern University}, 
 url = {https://github.com/yourusername/dnacrypt} 
} 
 

 

Contributing 

Contributions are welcome! Areas for contribution: 

Additional encryption algorithms (ChaCha20, etc.) 
More DNA encoding schemes 
Biological realism improvements 
Loop execution implementation 
User-defined functions 
File I/O operations 
Performance optimizations 
Documentation improvements 
Example programs 
Bug fixes 
Development Setup 

# Clone repository 
git clone https://github.com/Harshith2412/dnacrypt.git 
cd dnacrypt 
 
# Install in development mode 
pip install -e . 
 
# Run tests 
python3 tests/test_dnacrypt.py 
 
# Make changes and test 
dnacrypt run examples/test.dnac 
 

 

Roadmap 

Version 1.0 (Current)  

Complete lexer, parser, interpreter 
Cryptographic operations 
DNA encoding/decoding 
Type checking 
CLI tool 
Comprehensive tests 
Version 1.1 (Planned) 

[ ] User-defined functions execution 
[ ] While/For loop execution 
[ ] Try-catch execution 
[ ] File I/O operations 
[ ] Array/Dictionary operations 
[ ] REPL improvements 
Version 2.0 (Future) 

[ ] Compilation to bytecode 
[ ] Performance optimizations 
[ ] Package manager 
[ ] VS Code extension 
[ ] Web-based playground 
[ ] Debugger 
[ ] Standard library expansion 
 

License 

MIT License - See LICENSE file for details. 

 

Author 

Harshith Madhavaram 
MS in Cybersecurity, Northeastern University 
Research Focus: DNA-based Intrusion Detection Systems, Adversarial ML, Cybersecurity 

 

Acknowledgments 

Python cryptography library for crypto primitives 
Standard bioinformatics algorithms 
Modern compiler design principles 
Research in biological computing 
 

Support 

Documentation: See LANGUAGE_GUIDE.md and API_REFERENCE.md 
Examples: Check examples/ folder 
Tests: See tests/ for usage examples 
 

Project Status 

Version: 1.0.0 
Status: Beta (Production Ready) 
Tests: 18/18 passing (100%) 
Stability: Stable 
Maintained: Yes 
 

DNACrypt - Where Cryptography Meets Biology  

Built with ❤️ for research, education, and innovation 

 

Copyright © 2025 Harshith Madhavaram. All rights reserved. 

 