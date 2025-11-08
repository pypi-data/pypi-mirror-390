DNACrypt Language Guide 

Complete guide to programming in DNACrypt - The DNA-based Cryptography Language 

Version: 1.0.0 | Author: Harshith Madhavaram | Last Updated: November 2025 

 

Table of Contents 

Introduction 
Getting Started 
Basic Syntax 
Variables & Data Types 
Operators 
Control Flow 
Functions 
Cryptography 
DNA Operations 
Complete Examples 
Best Practices 
Common Patterns 
Troubleshooting 
 

Introduction 

DNACrypt is a domain-specific programming language designed specifically for DNA-based cryptography and biological computing. It seamlessly integrates cryptographic operations with DNA sequence manipulation, making it ideal for: 

Steganography using DNA sequences 
DNA-based intrusion detection systems 
Biological computing research 
Secure data encoding in synthetic DNA 
Educational purposes in cryptography and bioinformatics 
Key Features 

Native Cryptography: AES, RSA, ECDSA, SHA-3, PBKDF2 
DNA Operations: Encoding, complement, GC analysis, ORF finding 
Type Safety: Static type checking with semantic analysis 
Clean Syntax: Imperative, easy-to-read syntax 
Integrated: Crypto + DNA operations work seamlessly together 
 

Getting Started 

Installation 

# If installed via pip 
pip install dnacrypt-lang 
 
# Or clone from GitHub 
git clone https://github.com/yourusername/dnacrypt.git 
cd dnacrypt 
pip install -e . 
 

Your First Program 

Create a file hello.dnac: 

let message = "Hello, DNACrypt!" 
print(message) 
 

Run it: 

dnacrypt run hello.dnac 
 

Output: 

Hello, DNACrypt! 
 

Running DNACrypt Code 

Method 1: From files 

dnacrypt run myprogram.dnac 
 

Method 2: Direct execution 

dnacrypt -c "let x = 10; print(x)" 
 

Method 3: Interactive REPL 

dnacrypt repl 
>>> let x = 10 
>>> print(x) 
10 
>>> exit 
 

Method 4: From Python 

import dnacrypt 
 
dnacrypt.run(''' 
let message = "Hello!" 
print(message) 
''') 
 

 

Basic Syntax 

Comments 

// Single-line comment 
 
/* 
Multi-line 
comment 
*/ 
 

Statements 

Statements are the basic building blocks: 

let x = 10                    // Variable declaration 
x = 20                        // Assignment 
print("Hello")                // Function call 
let y = DNA.encode(data, mapping: BINARY_2BIT)  // Method call 
 

Code Structure 

// Imports (parsed, execution coming) 
import crypto 
import dna 
 
// Variable declarations 
let message = "Data" 
let key = generate(AES256) 
 
// Operations 
let encrypted = AES256(message, key: key, mode: GCM) 
 
// Output 
print(encrypted) 
 

 

Variables & Data Types 

Variable Declaration 

Basic Declaration 

let message = "Hello" 
let count = 42 
let price = 19.99 
let active = true 
let empty = null 
 

With Type Annotations 

let name: string = "Alice" 
let age: int = 25 
let temperature: float = 98.6 
let verified: bool = true 
let sequence: DNA = "ATGCCGTA" 
let key: Key = generate(AES256) 
 

Constants 

const PI = 3.14159 
const MAX_USERS = 1000 
const API_KEY = "secret_key" 
 
// PI = 3.14  // Error: Cannot reassign const 
 

Data Types 

Primitive Types 

Type 
Description 
Example 
Range/Notes 
string 
Text data 
"Hello" 
UTF-8 encoded 
int 
Integers 
42, -10 
Whole numbers 
float 
Decimals 
3.14, -0.5 
Floating point 
bool 
Boolean 
true, false 
Logical values 
null 
Null value 
null 
Absence of value 
Biological Types 

Type 
Description 
Example 
DNA 
DNA sequences 
"ATGCCGTA" 
RNA 
RNA sequences 
"AUGCCGUA" 
Codon 
3-nucleotide units 
"ATG" 
Gene 
Structured DNA + metadata 
From bio.create_gene() 
Cryptographic Types 

Type 
Description 
Created By 
Key 
Encryption keys 
generate(), derive_key() 
Cipher 
Encrypted data 
AES256() 
Hash 
Hash digests 
SHA256() 
Signature 
Digital signatures 
SIGN() 
Collection Types (Parsed, execution coming) 

let numbers = [1, 2, 3, 4, 5]           // Array 
let person = {name: "Alice", age: 25}   // Dictionary 
 

Type Inference 

DNACrypt can infer types automatically: 

let x = 10              // Inferred as int 
let y = 3.14            // Inferred as float 
let z = "text"          // Inferred as string 
let k = generate(AES256) // Inferred as Key 
 

DNA Sequence Detection 

Strings containing only A, T, G, C are automatically recognized as DNA: 

let dna = "ATGCCGTA"    // Recognized as DNA sequence 
let text = "HELLO"      // Regular string 
let mixed = "ATG123"    // Regular string (has numbers) 
 

 

Operators 

Arithmetic Operators 

let a = 10 
let b = 5 
 
let sum = a + b         // 15 (addition) 
let diff = a - b        // 5 (subtraction) 
let product = a * b     // 50 (multiplication) 
let quotient = a / b    // 2 (division) 
let remainder = a % b   // 0 (modulo) 
let power = 2 ** 8      // 256 (exponentiation) 
 
// Complex expressions 
let result = (a + b) * 2 - 5  // 25 
 

Comparison Operators 

let x = 10 
let y = 20 
 
let equal = x == y          // false 
let not_equal = x != y      // true 
let less = x < y            // true 
let greater = x > y         // false 
let less_eq = x <= 10       // true 
let greater_eq = x >= 5     // true 
 

Logical Operators 

let a = true 
let b = false 
 
let and_result = a && b     // false (logical AND) 
let or_result = a || b      // true (logical OR) 
let not_result = !a         // false (logical NOT) 
 
// In conditions 
if (x > 5 && x < 15) { 
   print("x is between 5 and 15") 
} 
 
if verified || admin { 
   print("Access granted") 
} 
 

Assignment Operators 

let x = 10 
 
x = 20              // Simple assignment 
 
// Compound assignments (parsed, execution coming) 
x = x + 5           // Currently use this 
// x += 5           // Coming in future version 
 

Operator Precedence (Highest to Lowest) 

** (Power) 
-, ! (Unary minus, NOT) 
*, /, % (Multiplication, Division, Modulo) 
+, - (Addition, Subtraction) 
<, >, <=, >= (Comparison) 
==, != (Equality) 
&& (Logical AND) 
|| (Logical OR) 
let result = 2 + 3 * 4      // 14 (not 20) 
let result2 = (2 + 3) * 4   // 20 (use parentheses) 
 

 

Control Flow 

If-Else Statements 

Simple If 

if temperature > 100 { 
   print("Warning: Too hot!") 
} 
 

If-Else 

if age >= 18 { 
   print("Adult") 
} else { 
   print("Minor") 
} 
 

If-Else If-Else 

if score >= 90 { 
   print("Grade: A") 
} else { 
   if score >= 80 { 
       print("Grade: B") 
   } else { 
       if score >= 70 { 
           print("Grade: C") 
       } else { 
           print("Grade: F") 
       } 
   } 
} 
 

With Complex Conditions 

if (verified && authenticated) || admin { 
   print("Access granted") 
} else { 
   print("Access denied") 
} 
 
let gc = DNA.gc_content(sequence) 
if gc > 0.6 { 
   print("GC-rich") 
} else { 
   if gc > 0.4 { 
       print("Normal GC content") 
   } else { 
       print("AT-rich") 
   } 
} 
 

While Loops (Parsed, execution coming) 

// Syntax is ready, execution in next version 
let counter = 0 
while counter < 10 { 
   print(counter) 
   counter = counter + 1 
} 
 

For Loops (Parsed, execution coming) 

// Syntax is ready, execution in next version 
let items = [1, 2, 3, 4, 5] 
for item in items { 
   print(item) 
} 
 

Try-Catch (Parsed, execution coming) 

// Syntax is ready, execution in next version 
try { 
   let decrypted = decrypt(data, key: wrong_key) 
} catch DecryptionError { 
   print("Decryption failed!") 
} 
 

 

Functions 

Calling Built-in Functions 

Simple Function Calls 

let key = generate(AES256) 
let bytes = random_bytes(16) 
let hash = SHA256("data") 
 

With Named Arguments 

let encrypted = AES256(plaintext, key: myKey, mode: GCM) 
 
let derived = derive_key( 
   password: "mypassword", 
   salt: random_bytes(16), 
   algorithm: PBKDF2, 
   iterations: 100000 
) 
 

Method Calls 

// Module.method(args) 
let dna = DNA.encode(data, mapping: BINARY_2BIT) 
let gc = DNA.gc_content(sequence) 
let comp = DNA.complement(sequence) 
 

Member Access 

let keypair = generate_pair(ECDSA_P256) 
let private_key = keypair.private 
let public_key = keypair.public 
 

Defining Your Own Functions (Parsed, execution coming) 

func encrypt_message(text: string, password: string) -> Cipher { 
   let salt = random_bytes(16) 
   let key = derive_key( 
       password: password, 
       salt: salt, 
       algorithm: PBKDF2, 
       iterations: 100000 
   ) 
   let encrypted = AES256(text, key: key, mode: GCM) 
   return encrypted 
} 
 
// Call it 
let result = encrypt_message("secret", "pass123") 
 

 

Cryptography 

Symmetric Encryption (AES) 

Generate Key 

let key = generate(AES256)  // 256-bit key 
let key128 = generate(AES128)  // 128-bit key 
 

Encrypt Data 

let message = "Secret message" 
let key = generate(AES256) 
 
// GCM mode (recommended - authenticated encryption) 
let encrypted = AES256(message, key: key, mode: GCM) 
 
// CBC mode 
let encrypted2 = AES256(message, key: key, mode: CBC) 
 

Decrypt Data 

let decrypted = decrypt(encrypted, key: key) 
print(decrypted)  // "Secret message" 
 

Complete Example 

print("Symmetric Encryption Demo") 
 
let plaintext = "Top Secret Data" 
print("Original:") 
print(plaintext) 
 
let encryption_key = generate(AES256) 
let ciphertext = AES256(plaintext, key: encryption_key, mode: GCM) 
 
print("Encrypted:") 
print(ciphertext) 
 
let recovered = decrypt(ciphertext, key: encryption_key) 
print("Decrypted:") 
print(recovered) 
 

Asymmetric Encryption (RSA/ECDSA) 

Generate Key Pairs 

// RSA key pairs 
let rsa_keys = generate_pair(RSA4096)  // 4096-bit 
let rsa_keys2 = generate_pair(RSA2048)  // 2048-bit 
 
// ECDSA key pairs 
let ecdsa_keys = generate_pair(ECDSA_P256)  // P-256 curve 
let ecdsa_keys2 = generate_pair(ECDSA_P384)  // P-384 curve 
 

Access Keys 

let keypair = generate_pair(ECDSA_P256) 
 
let private_key = keypair.private 
let public_key = keypair.public 
 
// Use for signing 
let signature = SIGN(data, key: private_key, algorithm: ECDSA) 
 

Cryptographic Hashing 

Hash Functions 

let data = "Hash this data" 
 
// SHA-256 (most common) 
let hash1 = SHA256(data) 
 
// SHA3-256 (Keccak, more modern) 
let hash2 = SHA3_256(data) 
 
// BLAKE2b (fast and secure) 
let hash3 = BLAKE2b(data) 
 
print(hash1)  // Hash(SHA256, 48e50550b5195218...) 
 

Use Cases 

// Integrity checking 
let file_content = "File data here" 
let file_hash = SHA256(file_content) 
// Store hash for later verification 
 
// Password hashing (use derive_key instead!) 
// Don't use SHA256 for passwords 
 

Key Derivation 

From Password (PBKDF2) 

let user_password = "my_secure_password" 
let salt = random_bytes(16)  // Always use random salt! 
 
let encryption_key = derive_key( 
   password: user_password, 
   salt: salt, 
   algorithm: PBKDF2, 
   iterations: 100000  // Minimum recommended 
) 
 
// Use the derived key 
let encrypted = AES256("data", key: encryption_key, mode: GCM) 
 
// IMPORTANT: Save the salt! You need it to decrypt later 
 

Security Recommendations 

//  GOOD: High iteration count 
iterations: 100000   // Minimum 
iterations: 200000   // Better 
iterations: 500000   // Excellent (slower) 
 
//  GOOD: Always use random salt 
let salt = random_bytes(16) 
 
//  GOOD: Use GCM mode 
mode: GCM 
 
// BAD: Hardcoded salt 
let salt = "hardcoded"  // Never do this! 
 
//  BAD: Low iterations 
iterations: 1000  // Too low! 
 

Digital Signatures 

Create Signature 

let document = "Important legal document" 
 
// Generate signing keys 
let signing_keys = generate_pair(ECDSA_P256) 
 
// Sign the document 
let signature = SIGN( 
   document, 
   key: signing_keys.private, 
   algorithm: ECDSA 
) 
 
print(signature)  // Signature(ECDSA) 
 

Verify Signature 

let is_valid = VERIFY( 
   document, 
   signature: signature, 
   key: signing_keys.public 
) 
 
if is_valid { 
   print("✓ Signature is authentic") 
   // Process the document 
} else { 
   print("✗ Signature verification failed!") 
   // Reject the document 
} 
 

Complete Example 

print("Digital Signature Demo") 
 
let contract = "I agree to the terms" 
print("Document:") 
print(contract) 
 
let keys = generate_pair(ECDSA_P256) 
 
let sig = SIGN(contract, key: keys.private, algorithm: ECDSA) 
print("Document signed") 
 
// Verify 
let verified = VERIFY(contract, signature: sig, key: keys.public) 
 
if verified { 
   print("✓ Contract is authentic and unmodified") 
} else { 
   print("✗ Contract has been tampered with!") 
} 
 

Random Generation 

// Cryptographically secure random bytes 
let salt = random_bytes(16)      // 16 bytes 
let nonce = random_bytes(12)     // 12 bytes for GCM 
let session_id = random_bytes(32) // 32 bytes 
 

 

DNA Operations 

Encoding Data as DNA 

Basic Encoding 

let message = "Secret" 
let key = generate(AES256) 
let encrypted = AES256(message, key: key, mode: GCM) 
 
// Encode encrypted data as DNA 
let dna_sequence = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
print(dna_sequence)  // DNA(ATGCCGTA...) 
 

Encoding Schemes 

BINARY_2BIT (Most common) 

2 bits per nucleotide 
00 → A, 01 → T, 10 → G, 11 → C 
Efficient and simple 
let dna = DNA.encode(data, mapping: BINARY_2BIT) 
 

BINARY_3BIT (Higher density) 

3 bits per nucleotide using codons 
More information per base 
let dna = DNA.encode(data, mapping: BINARY_3BIT) 
 

CODON_TABLE (Biological) 

Uses genetic code table 
More biologically realistic 
let dna = DNA.encode(data, mapping: CODON_TABLE) 
 

Decoding DNA to Data 

let original_data = DNA.decode(dna_sequence, mapping: BINARY_2BIT) 
 
// Must use same mapping as encoding! 
 

DNA Transformations 

Complement 

Get the complement strand (A↔T, G↔C): 

let sequence = "ATGCCGTA" 
let complement = DNA.complement(sequence) 
 
print(complement)  // DNA(TACGGCAT) 
 

Reverse 

Reverse the sequence: 

let reversed = DNA.reverse(sequence) 
print(reversed)  // DNA(ATGCCGTA) reversed 
 

Reverse Complement 

Get the reverse complement (used in DNA replication): 

let rev_comp = DNA.reverse_complement(sequence) 
print(rev_comp) 
 

DNA Analysis 

GC Content 

Calculate the percentage of G and C nucleotides: 

let sequence = "ATGCCGTA" 
let gc_ratio = DNA.gc_content(sequence) 
 
print(gc_ratio)  // 0.5 (50%) 
 
if gc_ratio > 0.6 { 
   print("GC-rich region") 
} else { 
   if gc_ratio > 0.4 { 
       print("Normal GC content") 
   } else { 
       print("AT-rich region") 
   } 
} 
 

Biological significance: 

Human genome: ~41% GC 
Bacteria: 25-75% GC 
GC-rich regions: Often contain genes 
AT-rich regions: Often regulatory 
Sequence Validation 

let seq1 = "ATGCCGTA" 
let valid1 = DNA.validate(seq1)  // true 
 
let seq2 = "ATGXYZ" 
let valid2 = DNA.validate(seq2)  // false (contains X, Y, Z) 
 

Sequence Length 

let length = DNA.length(sequence) 
print(length)  // Number of base pairs 
 

Biological Operations 

Transcription (DNA → RNA) 

let dna = "ATGCCGTA" 
let rna = DNA.transcribe(dna) 
 
print(rna)  // "AUGCCGUA" (T → U) 
 

Translation (DNA → Protein) 

let coding_sequence = "ATGGGCAAATAA" 
let protein = DNA.translate(coding_sequence) 
 
print(protein)  // "MGK" (Met-Gly-Lys) 
// Stops at stop codon (TAA, TAG, TGA) 
 

Find Open Reading Frames 

let long_sequence = "ATGATGATGTAA..." 
let orfs = DNA.find_orfs(long_sequence) 
 
// Returns array of ORF objects with: 
// - start position 
// - end position 
// - length 
// - sequence 
 

Find Motifs 

let sequence = "ATGATGCCGATGATG" 
let start_codons = DNA.find_motif(sequence, "ATG") 
 
// Returns array of positions where motif is found 
// [0, 3, 11] 
 

Split into Codons 

let sequence = "ATGCCGTAG" 
let codons = DNA.to_codons(sequence) 
 
// Returns: ["ATG", "CCG", "TAG"] 
 

 

Complete Examples 

Example 1: Basic Encryption 

print(" Basic Encryption Example ") 
print("") 
 
let plaintext = "My secret message" 
print("Original message:") 
print(plaintext) 
 
let key = generate(AES256) 
print("") 
print("Generated encryption key") 
 
let ciphertext = AES256(plaintext, key: key, mode: GCM) 
print("") 
print("Encrypted:") 
print(ciphertext) 
 
let recovered = decrypt(ciphertext, key: key) 
print("") 
print("Decrypted:") 
print(recovered) 
 

Example 2: Password-Based Encryption 

print(" Password-Based Encryption ") 
print("") 
 
let sensitive_data = "Credit card: 1234-5678-9012-3456" 
let user_password = "MySecurePassword123!" 
 
print("Data to protect:") 
print(sensitive_data) 
print("") 
 
print("Deriving encryption key from password...") 
let salt = random_bytes(16) 
let derived_key = derive_key( 
   password: user_password, 
   salt: salt, 
   algorithm: PBKDF2, 
   iterations: 150000 
) 
print(" Key derived (150,000 iterations)") 
 
print("") 
print("Encrypting data...") 
let encrypted_data = AES256(sensitive_data, key: derived_key, mode: GCM) 
print(" Data encrypted") 
 
print("") 
print("To decrypt, you need:") 
print("1. The encrypted data") 
print("2. The correct password") 
print("3. The salt") 
 
print("") 
print("Decrypting with correct password...") 
let decrypted_data = decrypt(encrypted_data, key: derived_key) 
print(" Decrypted:") 
print(decrypted_data) 
 

Example 3: DNA Encoding Pipeline 

print("=== Encryption to DNA Pipeline ===") 
print("") 
 
let message = "Confidential research data" 
print("Original message:") 
print(message) 
 
print("") 
print("Step 1: Encrypt") 
let key = generate(AES256) 
let encrypted = AES256(message, key: key, mode: GCM) 
print(" Encrypted with AES-256-GCM") 
 
print("") 
print("Step 2: Encode as DNA") 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
print("DNA Sequence:") 
print(dna) 
 
print("") 
print("Step 3: Analyze DNA") 
let gc = DNA.gc_content(dna) 
print("GC Content:") 
print(gc) 
 
let length = DNA.length(dna) 
print("Length (bp):") 
print(length) 
 
print("") 
print("Step 4: Sign") 
let keys = generate_pair(ECDSA_P256) 
let sig = SIGN(dna, key: keys.private, algorithm: ECDSA) 
print(" Digitally signed") 
 
print("") 
print(" Pipeline complete!") 
print("Data is now:") 
print("  Encrypted (AES-256)") 
print("   Encoded as DNA") 
print("   Digitally signed") 
 

Example 4: DNA Sequence Analysis 

print("=== DNA Sequence Analysis Tool ===") 
print("") 
 
let genome = "ATGCCGTAGCTAAGCTAGCTAGCTAAGGCTAATGC" 
 
print("Analyzing sequence...") 
print(genome) 
print("") 
 
print("Basic Statistics:") 
let gc = DNA.gc_content(genome) 
print("  GC Content:") 
print(gc) 
 
let len = DNA.length(genome) 
print("  Length:") 
print(len) 
 
print("") 
print("Transformations:") 
 
let comp = DNA.complement(genome) 
print("  Complement:") 
print(comp) 
 
let rev = DNA.reverse_complement(genome) 
print("  Reverse Complement:") 
print(rev) 
 
print("") 
print("Pattern Matching:") 
let atg_positions = DNA.find_motif(genome, "ATG") 
print("  Start codons (ATG) found at positions") 
 
print("") 
print(" Analysis complete") 
 

Example 5: Secure Communication Protocol 

print("=== Secure Communication Protocol ===") 
print("") 
 
let message = "The package will arrive tomorrow" 
let shared_password = "operation_nightfall" 
 
print("Alice (Sender):") 
print("-" * 50) 
 
print("1. Encrypting message") 
let salt = random_bytes(16) 
let key = derive_key( 
   password: shared_password, 
   salt: salt, 
   algorithm: PBKDF2, 
   iterations: 100000 
) 
let encrypted = AES256(message, key: key, mode: GCM) 
print(" Message encrypted") 
 
print("") 
print("2. Encoding as DNA (steganography)") 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
print("DNA Sequence:") 
print(dna) 
 
print("") 
print("3. Signing with private key") 
let alice_keys = generate_pair(ECDSA_P256) 
let signature = SIGN(dna, key: alice_keys.private, algorithm: ECDSA) 
print("✓ Message signed") 
 
print("") 
print("Alice sends: DNA sequence + signature + public key + salt") 
print("") 
 
print("Bob (Receiver):") 
print("-" * 50) 
 
print("1. Verifying signature") 
let verified = VERIFY(dna, signature: signature, key: alice_keys.public) 
 
if verified { 
   print(" Signature verified - message is authentic") 
    
   print("") 
   print("2. Decoding DNA") 
   let decoded = DNA.decode(dna, mapping: BINARY_2BIT) 
   print(" DNA decoded") 
    
   print("") 
   print("3. Deriving key from shared password") 
   let bob_key = derive_key( 
       password: shared_password, 
       salt: salt, 
       algorithm: PBKDF2, 
       iterations: 100000 
   ) 
    
   print("") 
   print("4. Decrypting message") 
   let decrypted = decrypt(encrypted, key: bob_key) 
   print("Original message:") 
   print(decrypted) 
} else { 
   print("✗ Signature invalid - message rejected!") 
} 
 
print("") 
print("=== Communication complete ===") 
 

Example 6: Multi-Layer Security 

print("=== Multi-Layer Security Example ===") 
print("") 
 
let data = "Highly classified information" 
 
print("Applying security layers...") 
print("") 
 
print("Layer 1: AES-256 Encryption") 
let key1 = generate(AES256) 
let layer1 = AES256(data, key: key1, mode: GCM) 
print("✓ Encrypted") 
 
print("") 
print("Layer 2: DNA Encoding") 
let layer2 = DNA.encode(layer1, mapping: BINARY_2BIT) 
print("✓ Encoded as DNA") 
print(layer2) 
 
print("") 
print("Layer 3: GC Content Analysis") 
let gc = DNA.gc_content(layer2) 
print("GC Content:") 
print(gc) 
 
if gc > 0.4 && gc < 0.6 { 
   print("✓ Biologically realistic GC content") 
} 
 
print("") 
print("Layer 4: Digital Signature") 
let keys = generate_pair(ECDSA_P256) 
let sig = SIGN(layer2, key: keys.private, algorithm: ECDSA) 
print("✓ Digitally signed") 
 
print("") 
print("Layer 5: Integrity Hash") 
let integrity = SHA3_256(data) 
print("✓ Integrity hash created") 
 
print("") 
print("Result: Data protected by 5 security layers!") 
 

 

Best Practices 

Security Best Practices 

DO: 

// Use strong encryption 
let key = generate(AES256)  // Not AES128 
 
// Use authenticated encryption (GCM) 
let enc = AES256(data, key: key, mode: GCM) 
 
// Use high iteration counts 
iterations: 100000  // Minimum 
 
// Always use random salts 
let salt = random_bytes(16) 
 
// Verify signatures before trusting data 
let ok = VERIFY(data, signature: sig, key: pubkey) 
if ok { 
   // Process data 
} 
 
// Use strong key sizes 
generate_pair(RSA4096)      // Not RSA2048 
generate_pair(ECDSA_P384)   // Not P256 for high security 
 

DON'T: 

// Don't hardcode secrets 
let password = "hardcoded"  //  Bad! 
 
// Don't reuse salts 
let salt = "same_salt"  // Always random! 
 
// Don't use weak iterations 
iterations: 1000  //  Too low! 
 
// Don't skip verification 
// Just trust the data  //  Always verify! 
 
// Don't use weak algorithms 
generate(AES128)  //  Use AES256 
 

Code Style 

Good Code Style 

// Clear variable names 
let encryption_key = generate(AES256) 
let user_message = "Hello" 
 
// Comments for complex operations 
// Derive key using PBKDF2 with 100k iterations 
let derived_key = derive_key(...) 
 
// Logical grouping 
print("=== Encryption Phase ===") 
let encrypted = AES256(data, key: key, mode: GCM) 
 
print("=== DNA Encoding Phase ===") 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
// Error checking 
if verified { 
   // Process 
} else { 
   print("Verification failed!") 
} 
 

Performance Tips 

// ✓ Reuse keys when encrypting multiple items 
let key = generate(AES256) 
let enc1 = AES256(data1, key: key, mode: GCM) 
let enc2 = AES256(data2, key: key, mode: GCM) 
 
// ✗ Don't regenerate for each encryption 
let enc1 = AES256(data1, key: generate(AES256), mode: GCM) 
let enc2 = AES256(data2, key: generate(AES256), mode: GCM) 
 

 

Common Patterns 

Pattern 1: Encrypt-Encode-Sign 

// 1. Encrypt the data 
let key = generate(AES256) 
let encrypted = AES256(message, key: key, mode: GCM) 
 
// 2. Encode as DNA 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
// 3. Sign it 
let keys = generate_pair(ECDSA_P256) 
let sig = SIGN(dna, key: keys.private, algorithm: ECDSA) 
 
// 4. Verify before using 
let ok = VERIFY(dna, signature: sig, key: keys.public) 
 

Pattern 2: Password-Based Encryption 

// Encrypting 
let user_pw = "password" 
let salt = random_bytes(16) 
let key = derive_key(password: user_pw, salt: salt, algorithm: PBKDF2, iterations: 100000) 
let enc = AES256(data, key: key, mode: GCM) 
 
// Save: encrypted data + salt (NOT the key or password!) 
 
// Decrypting (later) 
// User provides password again 
let decrypt_key = derive_key(password: user_pw, salt: salt, algorithm: PBKDF2, iterations: 100000) 
let dec = decrypt(enc, key: decrypt_key) 
 

Pattern 3: Integrity Checking 

// Sender 
let data = "Important document" 
let data_hash = SHA256(data) 
// Send: data + hash 
 
// Receiver 
let received_data = "Important document" 
let received_hash = SHA256(received_data) 
 
// Compare hashes 
if received_hash == data_hash { 
   print("✓ Data integrity verified") 
} else { 
   print("✗ Data has been modified!") 
} 
 

Pattern 4: Steganography 

// Hide encrypted data in DNA 
let secret = "Hidden message" 
let key = generate(AES256) 
let encrypted = AES256(secret, key: key, mode: GCM) 
let dna = DNA.encode(encrypted, mapping: BINARY_2BIT) 
 
// DNA sequence can be submitted to databases 
// Looks like normal genomic data! 
print("Hidden in plain sight:") 
print(dna) 
 
let gc = DNA.gc_content(dna) 
// Aim for 0.4-0.6 GC to look realistic 
 

 

Troubleshooting 

Common Errors 

"Undefined variable: X" 

print(message)  // Error if not defined 
 
let message = "Hello" 
print(message)  //  Works 
 

"Parse error: Unexpected token" 

let x = 10,  //  Extra comma 
let x = 10   // Correct 
 
if x > 5     //  Missing braces 
if x > 5 {   //  Correct 
   print("yes") 
} 
 

"Unknown function" 

let hash = SHA512(data)  // ✗ SHA512 not available 
let hash = SHA256(data)  // ✓ SHA256 available 
 

"Unknown method" 

let result = DNA.analyze(seq)  // ✗ No analyze method 
let result = DNA.gc_content(seq)  // ✓ Correct method 
 

Debugging Tips 

// Use print statements 
print("Debug: variable =") 
print(my_variable) 
 
// Print at each step 
print("Step 1: Generate key") 
let key = generate(AES256) 
 
print("Step 2: Encrypt") 
let enc = AES256(data, key: key, mode: GCM) 
 
print("Step 3: Done") 
 

 

Quick Reference 

Cheat Sheet 

// Variables 
let x = 10 
const Y = 20 
 
// Encryption 
let k = generate(AES256) 
let e = AES256(msg, key: k, mode: GCM) 
let d = decrypt(e, key: k) 
 
// DNA 
let dna = DNA.encode(e, mapping: BINARY_2BIT) 
let gc = DNA.gc_content(dna) 
let comp = DNA.complement(dna) 
 
// Signatures 
let keys = generate_pair(ECDSA_P256) 
let sig = SIGN(data, key: keys.private, algorithm: ECDSA) 
let ok = VERIFY(data, signature: sig, key: keys.public) 
 
// Hashing 
let h = SHA256(data) 
 
// Key derivation 
let k = derive_key(password: pw, salt: random_bytes(16), algorithm: PBKDF2, iterations: 100000) 
 
// Control flow 
if condition { 
   // code 
} else { 
   // code 
} 
 

 

 

Additional Resources 

API Reference: See API_REFERENCE.md for complete function documentation 
README: See README.md for project overview 
Examples: Check examples/ folder for sample programs 
Tests: See tests/ folder for comprehensive test cases 
 

DNACrypt Language Guide v1.0 

Happy coding with DNACrypt!  

 