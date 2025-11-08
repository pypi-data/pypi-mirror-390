"""
DNACrypt Language Parser (AST Builder)
Builds Abstract Syntax Tree from tokens
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union


# Import TokenType and Token from lexer
from dnacrypt_lexer import Token, TokenType


# ============ AST NODE DEFINITIONS ============

class ASTNode:
    """Base class for all AST nodes"""
    def __repr__(self):
        return f"{self.__class__.__name__}()"

@dataclass
class Program(ASTNode):
    """Root node of the AST"""
    statements: List[ASTNode]
    
    def __repr__(self):
        return f"Program(statements={len(self.statements)})"

@dataclass
class VariableDeclaration(ASTNode):
    """Variable declaration: let x = value"""
    name: str
    type_annotation: Optional[str]
    initializer: Optional[ASTNode]
    is_const: bool = False
    
    def __repr__(self):
        return f"VarDecl({self.name}: {self.type_annotation} = {self.initializer})"

@dataclass
class Assignment(ASTNode):
    """Assignment: x = value"""
    name: str
    operator: str
    value: ASTNode
    
    def __repr__(self):
        return f"Assign({self.name} {self.operator} {self.value})"

@dataclass
class FunctionDeclaration(ASTNode):
    """Function declaration"""
    name: str
    parameters: List[tuple]
    return_type: Optional[str]
    body: List[ASTNode]
    
    def __repr__(self):
        return f"FuncDecl({self.name})"

@dataclass
class ReturnStatement(ASTNode):
    """Return statement"""
    value: Optional[ASTNode]
    
    def __repr__(self):
        return f"Return({self.value})"

@dataclass
class IfStatement(ASTNode):
    """If-else statement"""
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]]
    
    def __repr__(self):
        return f"If({self.condition})"

@dataclass
class WhileStatement(ASTNode):
    """While loop"""
    condition: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"While({self.condition})"

@dataclass
class ForStatement(ASTNode):
    """For loop"""
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"For({self.variable} in {self.iterable})"

@dataclass
class TryStatement(ASTNode):
    """Try-catch block"""
    try_block: List[ASTNode]
    catch_variable: str
    catch_block: List[ASTNode]
    
    def __repr__(self):
        return f"Try-Catch({self.catch_variable})"

@dataclass
class ThrowStatement(ASTNode):
    """Throw statement"""
    exception: ASTNode
    
    def __repr__(self):
        return f"Throw({self.exception})"

@dataclass
class BreakStatement(ASTNode):
    """Break statement"""
    pass

@dataclass
class ContinueStatement(ASTNode):
    """Continue statement"""
    pass

@dataclass
class ImportStatement(ASTNode):
    """Import statement"""
    module: str
    items: Optional[List[str]]
    
    def __repr__(self):
        return f"Import({self.module})"

@dataclass
class ExportStatement(ASTNode):
    """Export statement"""
    value: ASTNode
    
    def __repr__(self):
        return f"Export({self.value})"

@dataclass
class BinaryOperation(ASTNode):
    """Binary operation: left op right"""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __repr__(self):
        return f"BinOp({self.left} {self.operator} {self.right})"

@dataclass
class UnaryOperation(ASTNode):
    """Unary operation: op operand"""
    operator: str
    operand: ASTNode
    
    def __repr__(self):
        return f"UnaryOp({self.operator}{self.operand})"

@dataclass
class FunctionCall(ASTNode):
    """Function call: func(args)"""
    name: str
    arguments: List[ASTNode]
    named_arguments: dict
    
    def __repr__(self):
        return f"Call({self.name})"

@dataclass
class MethodCall(ASTNode):
    """Method call: object.method(args)"""
    object: ASTNode
    method: str
    arguments: List[ASTNode]
    named_arguments: dict
    
    def __repr__(self):
        return f"MethodCall({self.object}.{self.method})"

@dataclass
class MemberAccess(ASTNode):
    """Member access: object.member"""
    object: ASTNode
    member: str
    
    def __repr__(self):
        return f"MemberAccess({self.object}.{self.member})"

@dataclass
class IndexAccess(ASTNode):
    """Index access: array[index]"""
    object: ASTNode
    index: ASTNode
    
    def __repr__(self):
        return f"IndexAccess({self.object}[{self.index}])"

@dataclass
class StringLiteral(ASTNode):
    """String literal"""
    value: str
    
    def __repr__(self):
        return f"String({repr(self.value)})"

@dataclass
class NumberLiteral(ASTNode):
    """Number literal"""
    value: Union[int, float]
    
    def __repr__(self):
        return f"Number({self.value})"

@dataclass
class DNALiteral(ASTNode):
    """DNA sequence literal"""
    sequence: str
    
    def __repr__(self):
        return f"DNA({self.sequence})"

@dataclass
class BooleanLiteral(ASTNode):
    """Boolean literal"""
    value: bool
    
    def __repr__(self):
        return f"Bool({self.value})"

@dataclass
class NullLiteral(ASTNode):
    """Null literal"""
    def __repr__(self):
        return "Null"

@dataclass
class Identifier(ASTNode):
    """Identifier (variable reference)"""
    name: str
    
    def __repr__(self):
        return f"Id({self.name})"

@dataclass
class DictionaryLiteral(ASTNode):
    """Dictionary literal: {key: value, ...}"""
    pairs: List[tuple]
    
    def __repr__(self):
        return f"Dict({len(self.pairs)} pairs)"

@dataclass
class ArrayLiteral(ASTNode):
    """Array literal: [item1, item2, ...]"""
    elements: List[ASTNode]
    
    def __repr__(self):
        return f"Array({len(self.elements)} elements)"

class ParseError(Exception):
    """Parser error"""
    pass

class DNACryptParser:
    """Parser for DNACrypt language"""
    
    def __init__(self, tokens: List[Token]):
        """Initialize parser with tokens"""
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
        
    def error(self, message: str):
        """Raise parse error with location info"""
        if self.current_token:
            raise ParseError(
                f"Parse error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        raise ParseError(f"Parse error: {message}")
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Token:
        """Move to next token"""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type"""
        if not self.current_token or self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}")
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        if not self.current_token:
            return False
        return self.current_token.type in token_types
    
    def parse(self) -> Program:
        """Parse the entire program"""
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        if not self.current_token:
            return None
        
        if self.current_token.type == TokenType.EOF:
            return None
        
        if self.match(TokenType.LET, TokenType.CONST):
            return self.parse_variable_declaration()
        
        if self.match(TokenType.FUNC):
            return self.parse_function_declaration()
        
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        
        if self.match(TokenType.TRY):
            return self.parse_try_statement()
        
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        
        if self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        
        if self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStatement()
        
        if self.match(TokenType.THROW):
            return self.parse_throw_statement()
        
        if self.match(TokenType.IMPORT):
            return self.parse_import_statement()
        
        if self.match(TokenType.EXPORT):
            return self.parse_export_statement()
        
        return self.parse_expression_statement()
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parse variable declaration: let x: type = value"""
        is_const = self.current_token.type == TokenType.CONST
        self.advance()
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.parse_type()
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()
        
        return VariableDeclaration(name, type_annotation, initializer, is_const)
    
    def parse_type(self) -> str:
        """Parse type annotation"""
        type_tokens = [
            TokenType.TYPE_STRING, TokenType.TYPE_BYTES, TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT, TokenType.TYPE_BOOL, TokenType.TYPE_DNA,
            TokenType.TYPE_RNA, TokenType.TYPE_KEY, TokenType.TYPE_CIPHER,
            TokenType.TYPE_HASH, TokenType.TYPE_SIGNATURE, TokenType.TYPE_CODON,
            TokenType.TYPE_GENE
        ]
        
        if self.match(*type_tokens):
            type_token = self.advance()
            return type_token.value
        
        self.error(f"Expected type annotation")
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration"""
        self.expect(TokenType.FUNC)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        parameters = []
        
        while not self.match(TokenType.RPAREN):
            param_name = self.expect(TokenType.IDENTIFIER).value
            
            param_type = None
            if self.match(TokenType.COLON):
                self.advance()
                param_type = self.parse_type()
            
            parameters.append((param_name, param_type))
            
            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RPAREN)
        
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()
        
        body = self.parse_block()
        
        return FunctionDeclaration(name, parameters, return_type, body)
    
    def parse_block(self) -> List[ASTNode]:
        """Parse block of statements: { ... }"""
        self.expect(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return statements
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement"""
        self.expect(TokenType.IF)
        
        condition = self.parse_expression()
        then_block = self.parse_block()
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            if self.match(TokenType.IF):
                else_block = [self.parse_if_statement()]
            else:
                else_block = self.parse_block()
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while statement"""
        self.expect(TokenType.WHILE)
        
        condition = self.parse_expression()
        body = self.parse_block()
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for statement"""
        self.expect(TokenType.FOR)
        
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        
        return ForStatement(variable, iterable, body)
    
    def parse_try_statement(self) -> TryStatement:
        """Parse try-catch statement"""
        self.expect(TokenType.TRY)
        
        try_block = self.parse_block()
        
        self.expect(TokenType.CATCH)
        catch_variable = self.expect(TokenType.IDENTIFIER).value
        catch_block = self.parse_block()
        
        return TryStatement(try_block, catch_variable, catch_block)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement"""
        self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.RBRACE):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_throw_statement(self) -> ThrowStatement:
        """Parse throw statement"""
        self.expect(TokenType.THROW)
        
        exception = self.parse_expression()
        return ThrowStatement(exception)
    
    def parse_import_statement(self) -> ImportStatement:
        """Parse import statement"""
        self.expect(TokenType.IMPORT)
        
        module = self.expect(TokenType.IDENTIFIER).value
        
        items = None
        if self.match(TokenType.FROM):
            pass
        
        return ImportStatement(module, items)
    
    def parse_export_statement(self) -> ExportStatement:
        """Parse export statement"""
        self.expect(TokenType.EXPORT)
        
        value = self.parse_expression()
        return ExportStatement(value)
    
    def parse_expression_statement(self) -> ASTNode:
        """Parse expression statement (assignment or expression)"""
        if self.match(TokenType.IDENTIFIER) and self.peek(1) and self.peek(1).type in [
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN
        ]:
            name = self.advance().value
            operator = self.advance().value
            value = self.parse_expression()
            return Assignment(name, operator, value)
        
        return self.parse_expression()
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with precedence"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR"""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            operator = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND"""
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            operator = self.advance().value
            right = self.parse_equality()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality (==, !=)"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.advance().value
            right = self.parse_comparison()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison (<, >, <=, >=)"""
        left = self.parse_additive()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN,
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.advance().value
            right = self.parse_additive()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse addition/subtraction"""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division/modulo"""
        left = self.parse_power()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().value
            right = self.parse_power()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_power(self) -> ASTNode:
        """Parse power (**)"""
        left = self.parse_unary()
        
        if self.match(TokenType.POWER):
            operator = self.advance().value
            right = self.parse_power()
            return BinaryOperation(left, operator, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary operations"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.advance().value
            operand = self.parse_unary()
            return UnaryOperation(operator, operand)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix operations (method calls, member access, indexing)"""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                
                if self.match(TokenType.LPAREN):
                    args, named_args = self.parse_arguments()
                    expr = MethodCall(expr, member, args, named_args)
                else:
                    expr = MemberAccess(expr, member)
            
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            
            elif self.match(TokenType.LPAREN) and isinstance(expr, Identifier):
                args, named_args = self.parse_arguments()
                expr = FunctionCall(expr.name, args, named_args)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions"""
        if self.match(TokenType.STRING):
            value = self.advance().value
            return StringLiteral(value)
        
        if self.match(TokenType.DNA_SEQUENCE):
            sequence = self.advance().value
            return DNALiteral(sequence)
        
        if self.match(TokenType.NUMBER):
            value = self.advance().value
            return NumberLiteral(value)
        
        if self.match(TokenType.BOOLEAN):
            value = self.advance().value
            return BooleanLiteral(value)
        
        if self.match(TokenType.NULL):
            self.advance()
            return NullLiteral()
        if self.match(TokenType.TYPE_DNA, TokenType.TYPE_RNA, TokenType.TYPE_KEY, 
                  TokenType.TYPE_CIPHER, TokenType.TYPE_HASH, TokenType.TYPE_SIGNATURE,
                  TokenType.TYPE_GENE, TokenType.TYPE_CODON):
            name = self.advance().value
            return Identifier(name)
        
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            if self.match(TokenType.LPAREN):
                args, named_args = self.parse_arguments()
                return FunctionCall(name, args, named_args)
            
            return Identifier(name)
        
        if self.match(TokenType.AUTO_GENERATE):
            self.advance()
            return Identifier("autoGenerate")
        
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        if self.match(TokenType.LBRACE):
            return self.parse_dictionary()
        
        if self.match(TokenType.LBRACKET):
            return self.parse_array()
        
        self.error(f"Unexpected token: {self.current_token.type.name if self.current_token else 'EOF'}")
    
    def parse_arguments(self) -> tuple:
        """Parse function arguments: (arg1, arg2, name: value)"""
        self.expect(TokenType.LPAREN)
        
        args = []
        named_args = {}
        
        while not self.match(TokenType.RPAREN):
            if self.match(TokenType.IDENTIFIER) and self.peek(1) and self.peek(1).type == TokenType.COLON:
                name = self.advance().value
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                named_args[name] = value
            else:
                args.append(self.parse_expression())
            
            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RPAREN)
        return args, named_args
    
    def parse_dictionary(self) -> DictionaryLiteral:
        """Parse dictionary literal: {key: value, ...}"""
        self.expect(TokenType.LBRACE)
        
        pairs = []
        
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.IDENTIFIER):
                key = self.advance().value
            elif self.match(TokenType.STRING):
                key = self.advance().value
            else:
                self.error("Expected key in dictionary")
            
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            
            pairs.append((key, value))
            
            if not self.match(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RBRACE)
        return DictionaryLiteral(pairs)
    
    def parse_array(self) -> ArrayLiteral:
        """Parse array literal: [elem1, elem2, ...]"""
        self.expect(TokenType.LBRACKET)
        
        elements = []
        
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            
            if not self.match(TokenType.RBRACKET):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RBRACKET)
        return ArrayLiteral(elements)


def print_ast(node: ASTNode, indent: int = 0):
    """Pretty print the AST"""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, VariableDeclaration):
        const_str = "const" if node.is_const else "let"
        type_str = f": {node.type_annotation}" if node.type_annotation else ""
        print(f"{prefix}{const_str} {node.name}{type_str} =")
        if node.initializer:
            print_ast(node.initializer, indent + 1)
    
    elif isinstance(node, Assignment):
        print(f"{prefix}{node.name} {node.operator}")
        print_ast(node.value, indent + 1)
    
    elif isinstance(node, FunctionDeclaration):
        params_str = ", ".join([f"{name}: {type}" for name, type in node.parameters])
        return_str = f" -> {node.return_type}" if node.return_type else ""
        print(f"{prefix}func {node.name}({params_str}){return_str}")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, IfStatement):
        print(f"{prefix}if:")
        print_ast(node.condition, indent + 1)
        print(f"{prefix}then:")
        for stmt in node.then_block:
            print_ast(stmt, indent + 1)
        if node.else_block:
            print(f"{prefix}else:")
            for stmt in node.else_block:
                print_ast(stmt, indent + 1)
    
    elif isinstance(node, WhileStatement):
        print(f"{prefix}while:")
        print_ast(node.condition, indent + 1)
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, ForStatement):
        print(f"{prefix}for {node.variable} in:")
        print_ast(node.iterable, indent + 1)
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, ReturnStatement):
        print(f"{prefix}return:")
        if node.value:
            print_ast(node.value, indent + 1)
    
    elif isinstance(node, BinaryOperation):
        print(f"{prefix}{node.operator}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    
    elif isinstance(node, UnaryOperation):
        print(f"{prefix}{node.operator}")
        print_ast(node.operand, indent + 1)
    
    elif isinstance(node, FunctionCall):
        print(f"{prefix}call {node.name}(")
        for arg in node.arguments:
            print_ast(arg, indent + 1)
        for name, value in node.named_arguments.items():
            print(f"{prefix}  {name}:")
            print_ast(value, indent + 2)
        print(f"{prefix})")
    
    elif isinstance(node, MethodCall):
        print(f"{prefix}method call:")
        print_ast(node.object, indent + 1)
        print(f"{prefix}  .{node.method}(")
        for arg in node.arguments:
            print_ast(arg, indent + 2)
        for name, value in node.named_arguments.items():
            print(f"{prefix}    {name}:")
            print_ast(value, indent + 3)
        print(f"{prefix}  )")
    
    elif isinstance(node, MemberAccess):
        print(f"{prefix}member access:")
        print_ast(node.object, indent + 1)
        print(f"{prefix}  .{node.member}")
    
    elif isinstance(node, StringLiteral):
        print(f"{prefix}String: {repr(node.value)}")
    
    elif isinstance(node, NumberLiteral):
        print(f"{prefix}Number: {node.value}")
    
    elif isinstance(node, DNALiteral):
        print(f"{prefix}DNA: {node.sequence}")
    
    elif isinstance(node, BooleanLiteral):
        print(f"{prefix}Bool: {node.value}")
    
    elif isinstance(node, NullLiteral):
        print(f"{prefix}null")
    
    elif isinstance(node, Identifier):
        print(f"{prefix}Id: {node.name}")
    
    elif isinstance(node, DictionaryLiteral):
        print(f"{prefix}Dict:")
        for key, value in node.pairs:
            print(f"{prefix}  {key}:")
            print_ast(value, indent + 2)
    
    elif isinstance(node, ArrayLiteral):
        print(f"{prefix}Array:")
        for elem in node.elements:
            print_ast(elem, indent + 1)
    
    elif isinstance(node, ImportStatement):
        print(f"{prefix}import {node.module}")
    
    elif isinstance(node, TryStatement):
        print(f"{prefix}try:")
        for stmt in node.try_block:
            print_ast(stmt, indent + 1)
        print(f"{prefix}catch {node.catch_variable}:")
        for stmt in node.catch_block:
            print_ast(stmt, indent + 1)
    
    else:
        print(f"{prefix}{node}")


if __name__ == "__main__":
    print("=" * 70)
    print("DNACrypt Parser - Clean Version")
    print("=" * 70)
    print("\nParser is ready to use!")