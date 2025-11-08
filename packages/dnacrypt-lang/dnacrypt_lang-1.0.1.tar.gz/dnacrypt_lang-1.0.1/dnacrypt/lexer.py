"""
DNACrypt Language Lexer/Tokenizer
Converts source code into tokens for parsing
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    """All token types in DNACrypt language"""
    
    # Literals
    STRING = auto()
    NUMBER = auto()
    DNA_SEQUENCE = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    
    # Keywords - Control Flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    
    # Keywords - Declaration
    LET = auto()
    CONST = auto()
    FUNC = auto()
    
    # Keywords - Types
    TYPE_STRING = auto()
    TYPE_BYTES = auto()
    TYPE_INT = auto()
    TYPE_FLOAT = auto()
    TYPE_BOOL = auto()
    TYPE_DNA = auto()
    TYPE_RNA = auto()
    TYPE_KEY = auto()
    TYPE_CIPHER = auto()
    TYPE_HASH = auto()
    TYPE_SIGNATURE = auto()
    TYPE_CODON = auto()
    TYPE_GENE = auto()
    
    # Keywords - Error Handling
    TRY = auto()
    CATCH = auto()
    THROW = auto()
    
    # Keywords - Module System
    IMPORT = auto()
    EXPORT = auto()
    FROM = auto()
    
    # Keywords - Special
    AUTO_GENERATE = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators - Arithmetic
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()
    
    # Operators - Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Operators - Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Operators - Assignment
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    DOT = auto()
    ARROW = auto()
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()

@dataclass
class Token:
    """Represents a single token"""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"

class DNACryptLexer:
    """Lexer for DNACrypt language"""
    
    # Keywords mapping
    KEYWORDS = {
        # Control flow
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'return': TokenType.RETURN,
        
        # Declaration
        'let': TokenType.LET,
        'const': TokenType.CONST,
        'func': TokenType.FUNC,
        
        # Types
        'string': TokenType.TYPE_STRING,
        'bytes': TokenType.TYPE_BYTES,
        'int': TokenType.TYPE_INT,
        'float': TokenType.TYPE_FLOAT,
        'bool': TokenType.TYPE_BOOL,
        'DNA': TokenType.TYPE_DNA,
        'RNA': TokenType.TYPE_RNA,
        'Key': TokenType.TYPE_KEY,
        'Cipher': TokenType.TYPE_CIPHER,
        'Hash': TokenType.TYPE_HASH,
        'Signature': TokenType.TYPE_SIGNATURE,
        'Codon': TokenType.TYPE_CODON,
        'Gene': TokenType.TYPE_GENE,
        
        # Error handling
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'throw': TokenType.THROW,
        
        # Module system
        'import': TokenType.IMPORT,
        'export': TokenType.EXPORT,
        'from': TokenType.FROM,
        
        # Special
        'autoGenerate': TokenType.AUTO_GENERATE,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'null': TokenType.NULL,
    }
    
    # Two-character operators
    TWO_CHAR_OPERATORS = {
        '==': TokenType.EQUAL,
        '!=': TokenType.NOT_EQUAL,
        '<=': TokenType.LESS_EQUAL,
        '>=': TokenType.GREATER_EQUAL,
        '&&': TokenType.AND,
        '||': TokenType.OR,
        '+=': TokenType.PLUS_ASSIGN,
        '-=': TokenType.MINUS_ASSIGN,
        '*=': TokenType.MULTIPLY_ASSIGN,
        '/=': TokenType.DIVIDE_ASSIGN,
        '**': TokenType.POWER,
        '->': TokenType.ARROW,
    }
    
    # Single-character operators
    SINGLE_CHAR_OPERATORS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '<': TokenType.LESS_THAN,
        '>': TokenType.GREATER_THAN,
        '=': TokenType.ASSIGN,
        '!': TokenType.NOT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ',': TokenType.COMMA,
        ':': TokenType.COLON,
        ';': TokenType.SEMICOLON,
        '.': TokenType.DOT,
    }
    
    def __init__(self, source_code: str):
        """Initialize lexer with source code"""
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def current_char(self) -> Optional[str]:
        """Get current character"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead at next character(s)"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Move to next character"""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace except newlines"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line and multi-line comments"""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Single-line comment
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            self.advance()  # /
            self.advance()  # *
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                self.advance()
    
    def read_string(self) -> str:
        """Read string literal"""
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        result = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                next_char = self.current_char()
                
                # Handle escape sequences
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                }
                
                if next_char in escape_map:
                    result += escape_map[next_char]
                else:
                    result += next_char
                
                self.advance()
            else:
                result += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return result
    
    def read_dna_sequence(self, content: str) -> bool:
        """Check if string is a DNA sequence"""
        # DNA sequence must only contain A, T, G, C
        return all(c in 'ATGC' for c in content.upper())
    
    def read_number(self) -> Token:
        """Read numeric literal"""
        start_line = self.line
        start_col = self.column
        
        num_str = ""
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Second dot, stop
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        # Handle scientific notation
        if self.current_char() and self.current_char() in 'eE':
            num_str += self.current_char()
            self.advance()
            if self.current_char() and self.current_char() in '+-':
                num_str += self.current_char()
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()
        
        value = float(num_str) if has_dot or 'e' in num_str.lower() else int(num_str)
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_line = self.line
        start_col = self.column
        
        result = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            result += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(result, TokenType.IDENTIFIER)
        
        # Handle boolean literals
        if token_type == TokenType.TRUE:
            return Token(TokenType.BOOLEAN, True, start_line, start_col)
        elif token_type == TokenType.FALSE:
            return Token(TokenType.BOOLEAN, False, start_line, start_col)
        elif token_type == TokenType.NULL:
            return Token(TokenType.NULL, None, start_line, start_col)
        
        return Token(token_type, result, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        while self.current_char():
            # Skip whitespace
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current_char() == '\n':
                # Optional: emit NEWLINE tokens if you want to be newline-sensitive
                self.advance()
                continue
            
            # Handle comments
            if self.current_char() == '/' and self.peek_char() in ['/', '*']:
                self.skip_comment()
                continue
            
            start_line = self.line
            start_col = self.column
            
            # String literals
            if self.current_char() in '"\'':
                content = self.read_string()
                
                # Check if it's a DNA sequence
                if self.read_dna_sequence(content):
                    self.tokens.append(Token(TokenType.DNA_SEQUENCE, content, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.STRING, content, start_line, start_col))
                continue
            
            # Numbers
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            two_char = self.current_char() + (self.peek_char() or '')
            if two_char in self.TWO_CHAR_OPERATORS:
                token_type = self.TWO_CHAR_OPERATORS[two_char]
                self.advance()
                self.advance()
                self.tokens.append(Token(token_type, two_char, start_line, start_col))
                continue
            
            # Single-character operators
            if self.current_char() in self.SINGLE_CHAR_OPERATORS:
                char = self.current_char()
                token_type = self.SINGLE_CHAR_OPERATORS[char]
                self.advance()
                self.tokens.append(Token(token_type, char, start_line, start_col))
                continue
            
            # Unknown character
            raise SyntaxError(f"Unexpected character '{self.current_char()}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


# ============ TESTING ============
def test_lexer():
    """Test the lexer with sample DNACrypt code"""
    
    # Test 1: Simple variable declaration
    code1 = '''
    let message = "Hello World"
    let key = generate(AES256)
    '''
    
    print("=" * 60)
    print("TEST 1: Variable Declarations")
    print("=" * 60)
    lexer1 = DNACryptLexer(code1)
    tokens1 = lexer1.tokenize()
    for token in tokens1:
        print(token)
    
    # Test 2: DNA sequence and encryption
    code2 = '''
    let sequence: DNA = "ATGCCGTA"
    let encrypted = AES256(message, key: myKey)
    let dna = DNA.encode(encrypted, mapping: BINARY_2BIT)
    '''
    
    print("\n" + "=" * 60)
    print("TEST 2: DNA Operations")
    print("=" * 60)
    lexer2 = DNACryptLexer(code2)
    tokens2 = lexer2.tokenize()
    for token in tokens2:
        print(token)
    
    # Test 3: Control flow and functions
    code3 = '''
    func encrypt_message(text: string) -> Cipher {
        if text == "" {
            return null
        }
        let encrypted = AES256(text, key: autoGenerate)
        return encrypted
    }
    '''
    
    print("\n" + "=" * 60)
    print("TEST 3: Functions and Control Flow")
    print("=" * 60)
    lexer3 = DNACryptLexer(code3)
    tokens3 = lexer3.tokenize()
    for token in tokens3:
        print(token)
    
    # Test 4: Complex operators and expressions
    code4 = '''
    let x = 10 + 5 * 2
    let y = x >= 20 && true
    counter += 1
    result **= 2
    '''
    
    print("\n" + "=" * 60)
    print("TEST 4: Operators and Expressions")
    print("=" * 60)
    lexer4 = DNACryptLexer(code4)
    tokens4 = lexer4.tokenize()
    for token in tokens4:
        print(token)
    
    # Test 5: Comments
    code5 = '''
    // This is a single-line comment
    let x = 5
    /* This is a
       multi-line comment */
    let y = 10
    '''
    
    print("\n" + "=" * 60)
    print("TEST 5: Comments")
    print("=" * 60)
    lexer5 = DNACryptLexer(code5)
    tokens5 = lexer5.tokenize()
    for token in tokens5:
        print(token)
    
    # Test 6: Full encryption pipeline
    code6 = '''
    import crypto
    import dna
    
    let message = "Secret"
    let key = generate(AES256)
    let encrypted = AES256(message, key: key, mode: GCM)
    let dna_seq = DNA.encode(encrypted, mapping: BINARY_2BIT)
    let signature = SIGN(dna_seq, key: privateKey, algorithm: ECDSA)
    '''
    
    print("\n" + "=" * 60)
    print("TEST 6: Full Pipeline")
    print("=" * 60)
    lexer6 = DNACryptLexer(code6)
    tokens6 = lexer6.tokenize()
    for token in tokens6:
        print(token)


if __name__ == "__main__":
    test_lexer()