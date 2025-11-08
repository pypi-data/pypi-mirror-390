"""
DNACrypt Language Semantic Analyzer
Performs type checking, scope validation, and semantic analysis
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

# Import AST node types
from dnacrypt_parser import (
    ASTNode, Program, VariableDeclaration, Assignment, FunctionDeclaration,
    ReturnStatement, IfStatement, WhileStatement, ForStatement,
    TryStatement, ThrowStatement, BreakStatement, ContinueStatement,
    ImportStatement, ExportStatement, BinaryOperation, UnaryOperation,
    FunctionCall, MethodCall, MemberAccess, IndexAccess,
    StringLiteral, NumberLiteral, DNALiteral, BooleanLiteral,
    NullLiteral, Identifier, DictionaryLiteral, ArrayLiteral
)


class DNACryptType(Enum):
    """Type system for DNACrypt"""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    NUMBER = "number"  # Generic number (int or float)
    BOOL = "bool"
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
    ANY = "any"  # For flexible typing
    VOID = "void"  # For functions with no return


@dataclass
class SemanticError(Exception):
    """Semantic error information"""
    def __init__(self, message: str, line: int = 0, column: int = 0, node: Optional[ASTNode] = None):
        self.message = message
        self.line = line
        self.column = column
        self.node = node
        super().__init__(message)
    
    def __str__(self):
        if self.line and self.column:
            return f"Semantic Error at line {self.line}, column {self.column}: {self.message}"
        return f"Semantic Error: {self.message}"


@dataclass
class Symbol:
    """Symbol table entry"""
    name: str
    type: DNACryptType
    is_const: bool = False
    is_function: bool = False
    function_params: Optional[List[tuple]] = None  # [(name, type), ...]
    return_type: Optional[DNACryptType] = None
    scope_level: int = 0
    
    def __repr__(self):
        if self.is_function:
            return f"Symbol({self.name}: function -> {self.return_type})"
        return f"Symbol({self.name}: {self.type.value}, const={self.is_const})"


class SymbolTable:
    """Symbol table for semantic analysis"""
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
        self.scope_level = 0 if parent is None else parent.scope_level + 1
        self.children: List['SymbolTable'] = []
        
    def define(self, name: str, symbol: Symbol):
        """Define a symbol in current scope"""
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' already defined in this scope")
        symbol.scope_level = self.scope_level
        self.symbols[name] = symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up symbol in current and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def exists_in_scope(self, name: str) -> bool:
        """Check if symbol exists in current scope only"""
        return name in self.symbols
    
    def create_child_scope(self) -> 'SymbolTable':
        """Create a child scope"""
        child = SymbolTable(parent=self)
        self.children.append(child)
        return child


class SemanticAnalyzer:
    """Semantic analyzer for DNACrypt"""
    
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors: List[SemanticError] = []
        self.in_loop = False
        self.in_function = False
        self.current_function_return_type: Optional[DNACryptType] = None
        
        # Setup built-in types and functions
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions and constants"""
        
        # Built-in functions
        builtins = [
            # Crypto functions
            ("AES128", DNACryptType.FUNCTION, [], DNACryptType.CIPHER),
            ("AES256", DNACryptType.FUNCTION, [], DNACryptType.CIPHER),
            ("SHA256", DNACryptType.FUNCTION, [], DNACryptType.HASH),
            ("SHA3_256", DNACryptType.FUNCTION, [], DNACryptType.HASH),
            ("BLAKE2b", DNACryptType.FUNCTION, [], DNACryptType.HASH),
            ("generate", DNACryptType.FUNCTION, [("algorithm", DNACryptType.STRING)], DNACryptType.KEY),
            ("generate_pair", DNACryptType.FUNCTION, [("algorithm", DNACryptType.STRING)], DNACryptType.DICT),
            ("derive_key", DNACryptType.FUNCTION, [], DNACryptType.KEY),
            ("random_bytes", DNACryptType.FUNCTION, [("size", DNACryptType.INT)], DNACryptType.STRING),
            ("decrypt", DNACryptType.FUNCTION, [], DNACryptType.STRING),
            ("BLAKE2b", DNACryptType.FUNCTION, [("data", DNACryptType.STRING)], DNACryptType.HASH),
            ("SIGN", DNACryptType.FUNCTION, [], DNACryptType.SIGNATURE),
            ("VERIFY", DNACryptType.FUNCTION, [], DNACryptType.BOOL),
            ("HMAC", DNACryptType.FUNCTION, [], DNACryptType.HASH),
            
            # I/O functions
            ("print", DNACryptType.FUNCTION, [("value", DNACryptType.ANY)], DNACryptType.VOID),
            ("read_file", DNACryptType.FUNCTION, [("path", DNACryptType.STRING)], DNACryptType.STRING),
            ("write_file", DNACryptType.FUNCTION, [], DNACryptType.VOID),
        ]
        
        for name, ftype, params, return_type in builtins:
            self.global_scope.define(name, Symbol(
                name=name,
                type=ftype,
                is_function=True,
                function_params=params,
                return_type=return_type
            ))
        
        # Built-in modules
        modules = ["crypto", "dna", "bio", "DNA"]
        for module in modules:
            self.global_scope.define(module, Symbol(
                name=module,
                type=DNACryptType.DICT
            ))
        
        # Built-in constants
        constants = [
            ("BINARY_2BIT", DNACryptType.STRING),
            ("BINARY_3BIT", DNACryptType.STRING),
            ("CODON_TABLE", DNACryptType.STRING),
            ("RSA2048", DNACryptType.STRING),
            ("RSA4096", DNACryptType.STRING),
            ("ECDSA_P256", DNACryptType.STRING),
            ("ECDSA_P384", DNACryptType.STRING),
            ("ECDSA", DNACryptType.STRING),
            ("PBKDF2", DNACryptType.STRING),
            ("GCM", DNACryptType.STRING),
            ("CBC", DNACryptType.STRING),
            ("autoGenerate", DNACryptType.STRING),
        ]
        
        for name, ctype in constants:
            self.global_scope.define(name, Symbol(
                name=name,
                type=ctype,
                is_const=True
            ))
    
    def analyze(self, ast: Program) -> bool:
        """Analyze the AST and return True if no errors"""
        self.errors.clear()
        
        try:
            self.visit_program(ast)
        except SemanticError as e:
            self.errors.append(e)
        
        return len(self.errors) == 0
    
    def add_error(self, message: str, node: Optional[ASTNode] = None):
        """Add a semantic error"""
        self.errors.append(SemanticError(message, node=node))
    
    def visit_program(self, node: Program):
        """Visit program node"""
        for statement in node.statements:
            self.visit(statement)
    
    def visit(self, node: ASTNode) -> Optional[DNACryptType]:
        """Visit a node and return its type"""
        
        if isinstance(node, VariableDeclaration):
            return self.visit_variable_declaration(node)
        
        elif isinstance(node, Assignment):
            return self.visit_assignment(node)
        
        elif isinstance(node, FunctionDeclaration):
            return self.visit_function_declaration(node)
        
        elif isinstance(node, ReturnStatement):
            return self.visit_return_statement(node)
        
        elif isinstance(node, IfStatement):
            return self.visit_if_statement(node)
        
        elif isinstance(node, WhileStatement):
            return self.visit_while_statement(node)
        
        elif isinstance(node, ForStatement):
            return self.visit_for_statement(node)
        
        elif isinstance(node, TryStatement):
            return self.visit_try_statement(node)
        
        elif isinstance(node, BreakStatement):
            return self.visit_break_statement(node)
        
        elif isinstance(node, ContinueStatement):
            return self.visit_continue_statement(node)
        
        elif isinstance(node, BinaryOperation):
            return self.visit_binary_operation(node)
        
        elif isinstance(node, UnaryOperation):
            return self.visit_unary_operation(node)
        
        elif isinstance(node, FunctionCall):
            return self.visit_function_call(node)
        
        elif isinstance(node, MethodCall):
            return self.visit_method_call(node)
        
        elif isinstance(node, MemberAccess):
            return self.visit_member_access(node)
        
        elif isinstance(node, IndexAccess):
            return self.visit_index_access(node)
        
        elif isinstance(node, StringLiteral):
            return DNACryptType.STRING
        
        elif isinstance(node, NumberLiteral):
            if isinstance(node.value, int):
                return DNACryptType.INT
            return DNACryptType.FLOAT
        
        elif isinstance(node, DNALiteral):
            return DNACryptType.DNA
        
        elif isinstance(node, BooleanLiteral):
            return DNACryptType.BOOL
        
        elif isinstance(node, NullLiteral):
            return DNACryptType.NULL
        
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        
        elif isinstance(node, DictionaryLiteral):
            return DNACryptType.DICT
        
        elif isinstance(node, ArrayLiteral):
            return DNACryptType.ARRAY
        
        elif isinstance(node, ImportStatement):
            return DNACryptType.VOID
        
        else:
            return DNACryptType.ANY
    
    def visit_variable_declaration(self, node: VariableDeclaration) -> DNACryptType:
        """Visit variable declaration"""
        
        # Check if already defined in current scope
        if self.current_scope.exists_in_scope(node.name):
            self.add_error(f"Variable '{node.name}' already defined in this scope", node)
            return DNACryptType.ANY
        
        # Get type from initializer or annotation
        var_type = DNACryptType.ANY
        
        if node.initializer:
            var_type = self.visit(node.initializer)
        
        if node.type_annotation:
            # Map string type to enum
            type_map = {
                "string": DNACryptType.STRING,
                "int": DNACryptType.INT,
                "float": DNACryptType.FLOAT,
                "bool": DNACryptType.BOOL,
                "DNA": DNACryptType.DNA,
                "RNA": DNACryptType.RNA,
                "Key": DNACryptType.KEY,
                "Cipher": DNACryptType.CIPHER,
                "Hash": DNACryptType.HASH,
                "Signature": DNACryptType.SIGNATURE,
                "Codon": DNACryptType.CODON,
                "Gene": DNACryptType.GENE,
            }
            
            annotated_type = type_map.get(node.type_annotation, DNACryptType.ANY)
            
            # Check type compatibility if both annotation and initializer exist
            if node.initializer and var_type != DNACryptType.ANY:
                if not self.is_compatible(var_type, annotated_type):
                    self.add_error(
                        f"Type mismatch: cannot assign {var_type.value} to {annotated_type.value}",
                        node
                    )
            
            var_type = annotated_type
        
        # Define symbol
        symbol = Symbol(
            name=node.name,
            type=var_type,
            is_const=node.is_const
        )
        self.current_scope.define(node.name, symbol)
        
        return var_type
    
    def visit_assignment(self, node: Assignment) -> DNACryptType:
        """Visit assignment"""
        
        # Check if variable exists
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            self.add_error(f"Undefined variable: '{node.name}'", node)
            return DNACryptType.ANY
        
        # Check if trying to assign to const
        if symbol.is_const:
            self.add_error(f"Cannot assign to const variable: '{node.name}'", node)
            return symbol.type
        
        # Check type compatibility
        value_type = self.visit(node.value)
        
        if not self.is_compatible(value_type, symbol.type):
            self.add_error(
                f"Type mismatch: cannot assign {value_type.value} to {symbol.type.value}",
                node
            )
        
        return symbol.type
    
    def visit_function_declaration(self, node: FunctionDeclaration) -> DNACryptType:
        """Visit function declaration"""
        
        # Check if function already defined
        if self.current_scope.exists_in_scope(node.name):
            self.add_error(f"Function '{node.name}' already defined", node)
            return DNACryptType.FUNCTION
        
        # Map return type
        return_type = DNACryptType.VOID
        if node.return_type:
            type_map = {
                "string": DNACryptType.STRING,
                "int": DNACryptType.INT,
                "Cipher": DNACryptType.CIPHER,
                "DNA": DNACryptType.DNA,
                "Key": DNACryptType.KEY,
            }
            return_type = type_map.get(node.return_type, DNACryptType.ANY)
        
        # Define function symbol
        symbol = Symbol(
            name=node.name,
            type=DNACryptType.FUNCTION,
            is_function=True,
            function_params=node.parameters,
            return_type=return_type
        )
        self.current_scope.define(node.name, symbol)
        
        # Create new scope for function body
        function_scope = self.current_scope.create_child_scope()
        prev_scope = self.current_scope
        self.current_scope = function_scope
        
        # Define parameters
        for param_name, param_type in node.parameters:
            if param_type:
                type_map = {
                    "string": DNACryptType.STRING,
                    "int": DNACryptType.INT,
                    "Key": DNACryptType.KEY,
                }
                ptype = type_map.get(param_type, DNACryptType.ANY)
            else:
                ptype = DNACryptType.ANY
            
            self.current_scope.define(param_name, Symbol(
                name=param_name,
                type=ptype
            ))
        
        # Analyze function body
        prev_in_function = self.in_function
        prev_return_type = self.current_function_return_type
        self.in_function = True
        self.current_function_return_type = return_type
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.in_function = prev_in_function
        self.current_function_return_type = prev_return_type
        self.current_scope = prev_scope
        
        return DNACryptType.FUNCTION
    
    def visit_return_statement(self, node: ReturnStatement) -> DNACryptType:
        """Visit return statement"""
        
        if not self.in_function:
            self.add_error("Return statement outside of function", node)
            return DNACryptType.VOID
        
        if node.value:
            return_type = self.visit(node.value)
            
            # Check return type matches function signature
            if self.current_function_return_type and self.current_function_return_type != DNACryptType.VOID:
                if not self.is_compatible(return_type, self.current_function_return_type):
                    self.add_error(
                        f"Return type mismatch: expected {self.current_function_return_type.value}, got {return_type.value}",
                        node
                    )
        else:
            if self.current_function_return_type and self.current_function_return_type != DNACryptType.VOID:
                self.add_error("Function must return a value", node)
        
        return DNACryptType.VOID
    
    def visit_if_statement(self, node: IfStatement) -> DNACryptType:
        """Visit if statement"""
        
        # Check condition is boolean
        condition_type = self.visit(node.condition)
        if condition_type not in [DNACryptType.BOOL, DNACryptType.ANY]:
            self.add_error(f"If condition must be boolean, got {condition_type.value}", node)
        
        # Create scope for then block
        then_scope = self.current_scope.create_child_scope()
        prev_scope = self.current_scope
        self.current_scope = then_scope
        
        for stmt in node.then_block:
            self.visit(stmt)
        
        self.current_scope = prev_scope
        
        # Else block
        if node.else_block:
            else_scope = self.current_scope.create_child_scope()
            self.current_scope = else_scope
            
            for stmt in node.else_block:
                self.visit(stmt)
            
            self.current_scope = prev_scope
        
        return DNACryptType.VOID
    
    def visit_while_statement(self, node: WhileStatement) -> DNACryptType:
        """Visit while statement"""
        
        # Check condition is boolean
        condition_type = self.visit(node.condition)
        if condition_type not in [DNACryptType.BOOL, DNACryptType.ANY]:
            self.add_error(f"While condition must be boolean, got {condition_type.value}", node)
        
        # Create scope for body
        body_scope = self.current_scope.create_child_scope()
        prev_scope = self.current_scope
        self.current_scope = body_scope
        
        prev_in_loop = self.in_loop
        self.in_loop = True
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.in_loop = prev_in_loop
        self.current_scope = prev_scope
        
        return DNACryptType.VOID
    
    def visit_for_statement(self, node: ForStatement) -> DNACryptType:
        """Visit for statement"""
        
        # Check iterable
        iterable_type = self.visit(node.iterable)
        if iterable_type not in [DNACryptType.ARRAY, DNACryptType.STRING, DNACryptType.ANY]:
            self.add_error(f"Cannot iterate over {iterable_type.value}", node)
        
        # Create scope for body
        body_scope = self.current_scope.create_child_scope()
        prev_scope = self.current_scope
        self.current_scope = body_scope
        
        # Define loop variable
        self.current_scope.define(node.variable, Symbol(
            name=node.variable,
            type=DNACryptType.ANY
        ))
        
        prev_in_loop = self.in_loop
        self.in_loop = True
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.in_loop = prev_in_loop
        self.current_scope = prev_scope
        
        return DNACryptType.VOID
    
    def visit_try_statement(self, node: TryStatement) -> DNACryptType:
        """Visit try statement"""
        
        # Try block
        try_scope = self.current_scope.create_child_scope()
        prev_scope = self.current_scope
        self.current_scope = try_scope
        
        for stmt in node.try_block:
            self.visit(stmt)
        
        self.current_scope = prev_scope
        
        # Catch block
        catch_scope = self.current_scope.create_child_scope()
        self.current_scope = catch_scope
        
        # Define catch variable
        self.current_scope.define(node.catch_variable, Symbol(
            name=node.catch_variable,
            type=DNACryptType.STRING
        ))
        
        for stmt in node.catch_block:
            self.visit(stmt)
        
        self.current_scope = prev_scope
        
        return DNACryptType.VOID
    
    def visit_break_statement(self, node: BreakStatement) -> DNACryptType:
        """Visit break statement"""
        if not self.in_loop:
            self.add_error("Break statement outside of loop", node)
        return DNACryptType.VOID
    
    def visit_continue_statement(self, node: ContinueStatement) -> DNACryptType:
        """Visit continue statement"""
        if not self.in_loop:
            self.add_error("Continue statement outside of loop", node)
        return DNACryptType.VOID
    
    def visit_binary_operation(self, node: BinaryOperation) -> DNACryptType:
        """Visit binary operation"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        # Arithmetic operators
        if node.operator in ['+', '-', '*', '/', '%', '**']:
            if left_type in [DNACryptType.INT, DNACryptType.FLOAT, DNACryptType.NUMBER, DNACryptType.ANY] and \
               right_type in [DNACryptType.INT, DNACryptType.FLOAT, DNACryptType.NUMBER, DNACryptType.ANY]:
                # Result type
                if left_type == DNACryptType.FLOAT or right_type == DNACryptType.FLOAT:
                    return DNACryptType.FLOAT
                return DNACryptType.INT
            else:
                self.add_error(f"Invalid operands for {node.operator}: {left_type.value} and {right_type.value}", node)
                return DNACryptType.ANY
        
        # Comparison operators
        elif node.operator in ['<', '>', '<=', '>=']:
            return DNACryptType.BOOL
        
        # Equality operators
        elif node.operator in ['==', '!=']:
            return DNACryptType.BOOL
        
        # Logical operators
        elif node.operator in ['&&', '||']:
            if left_type != DNACryptType.BOOL and left_type != DNACryptType.ANY:
                self.add_error(f"Left operand of {node.operator} must be boolean", node)
            if right_type != DNACryptType.BOOL and right_type != DNACryptType.ANY:
                self.add_error(f"Right operand of {node.operator} must be boolean", node)
            return DNACryptType.BOOL
        
        return DNACryptType.ANY
    
    def visit_unary_operation(self, node: UnaryOperation) -> DNACryptType:
        """Visit unary operation"""
        operand_type = self.visit(node.operand)
        
        if node.operator == '-':
            if operand_type in [DNACryptType.INT, DNACryptType.FLOAT, DNACryptType.NUMBER, DNACryptType.ANY]:
                return operand_type
            else:
                self.add_error(f"Cannot negate {operand_type.value}", node)
                return DNACryptType.ANY
        
        elif node.operator == '!':
            if operand_type in [DNACryptType.BOOL, DNACryptType.ANY]:
                return DNACryptType.BOOL
            else:
                self.add_error(f"Cannot apply logical NOT to {operand_type.value}", node)
                return DNACryptType.BOOL
        
        return DNACryptType.ANY
    
    def visit_function_call(self, node: FunctionCall) -> DNACryptType:
        """Visit function call"""
        
        # Look up function
        symbol = self.current_scope.lookup(node.name)
        
        if not symbol:
            self.add_error(f"Undefined function: '{node.name}'", node)
            return DNACryptType.ANY
        
        if not symbol.is_function:
            self.add_error(f"'{node.name}' is not a function", node)
            return DNACryptType.ANY
        
        # Type check arguments (simplified)
        for arg in node.arguments:
            self.visit(arg)
        
        for name, value in node.named_arguments.items():
            self.visit(value)
        
        return symbol.return_type if symbol.return_type else DNACryptType.ANY
    
    def visit_method_call(self, node: MethodCall) -> DNACryptType:
        """Visit method call"""
        
        # Visit object
        obj_type = self.visit(node.object)
        
        # Visit arguments
        for arg in node.arguments:
            self.visit(arg)
        
        for name, value in node.named_arguments.items():
            self.visit(value)
        
        # Return appropriate type based on method
        method_returns = {
            "encode": DNACryptType.DNA,
            "decode": DNACryptType.STRING,
            "gc_content": DNACryptType.FLOAT,
            "complement": DNACryptType.DNA,
            "reverse_complement": DNACryptType.DNA,
            "find_orfs": DNACryptType.ARRAY,
            "make_realistic": DNACryptType.DNA,
            "realism_score": DNACryptType.FLOAT,
        }
        
        return method_returns.get(node.method, DNACryptType.ANY)
    
    def visit_member_access(self, node: MemberAccess) -> DNACryptType:
        """Visit member access"""
        obj_type = self.visit(node.object)
        
        # Specific member types
        if node.member in ["private", "public"]:
            return DNACryptType.KEY
        elif node.member == "sequence":
            return DNACryptType.DNA
        elif node.member == "metadata":
            return DNACryptType.DICT
        elif node.member == "length":
            return DNACryptType.INT
        
        return DNACryptType.ANY
    
    def visit_index_access(self, node: IndexAccess) -> DNACryptType:
        """Visit index access"""
        obj_type = self.visit(node.object)
        index_type = self.visit(node.index)
        
        if index_type not in [DNACryptType.INT, DNACryptType.ANY]:
            self.add_error(f"Array index must be integer, got {index_type.value}", node)
        
        return DNACryptType.ANY
    
    def visit_identifier(self, node: Identifier) -> DNACryptType:
        """Visit identifier"""
        symbol = self.current_scope.lookup(node.name)
        
        if not symbol:
            self.add_error(f"Undefined variable: '{node.name}'", node)
            return DNACryptType.ANY
        
        return symbol.type
    
    def is_compatible(self, source: DNACryptType, target: DNACryptType) -> bool:
        """Check if source type is compatible with target type"""
        
        # ANY is compatible with everything
        if source == DNACryptType.ANY or target == DNACryptType.ANY:
            return True
        
        # Same type
        if source == target:
            return True
        
        # Number types are compatible
        if source in [DNACryptType.INT, DNACryptType.FLOAT, DNACryptType.NUMBER] and \
           target in [DNACryptType.INT, DNACryptType.FLOAT, DNACryptType.NUMBER]:
            return True
        
        return False
    
    def print_errors(self):
        """Print all semantic errors"""
        if not self.errors:
            print("✓ No semantic errors found")
            return
        
        print(f"❌ Found {len(self.errors)} semantic error(s):")
        for error in self.errors:
            print(f"  • {error}")
    
    def get_symbol_table_info(self) -> str:
        """Get symbol table information"""
        def format_scope(scope: SymbolTable, level: int = 0) -> str:
            indent = "  " * level
            result = f"{indent}Scope (level {scope.scope_level}):\n"
            
            for name, symbol in scope.symbols.items():
                result += f"{indent}  {symbol}\n"
            
            for child in scope.children:
                result += format_scope(child, level + 1)
            
            return result
        
        return format_scope(self.global_scope)


# ============ TESTING ============

if __name__ == "__main__":
    print("=" * 70)
    print("DNACrypt Semantic Analyzer")
    print("=" * 70)
    print("\nThe semantic analyzer is ready!")
    print("\nTo use:")
    print("""
from dnacrypt_lexer import DNACryptLexer
from dnacrypt_parser import DNACryptParser
from dnacrypt_semantic import SemanticAnalyzer

code = '''
let message: string = "Hello"
let count: int = 42
let key = generate(AES256)
'''

lexer = DNACryptLexer(code)
tokens = lexer.tokenize()

parser = DNACryptParser(tokens)
ast = parser.parse()

analyzer = SemanticAnalyzer()
if analyzer.analyze(ast):
    print("✓ Semantic analysis passed!")
else:
    analyzer.print_errors()
""")