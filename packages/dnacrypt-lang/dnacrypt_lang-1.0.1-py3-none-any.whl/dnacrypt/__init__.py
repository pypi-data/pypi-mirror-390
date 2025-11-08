"""
DNACrypt - A Domain-Specific Language for DNA-Based Cryptography
"""

__version__ = "1.0.1"
__author__ = "Harshith Madhavaram"
__license__ = "MIT"

from .lexer import DNACryptLexer
from .parser import DNACryptParser
from .interpreter import DNACryptInterpreter

try:
    from .semantic import SemanticAnalyzer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


def run(code: str, use_semantic_analysis: bool = False):
    """
    Run DNACrypt code
    
    Example:
        import dnacrypt
        dnacrypt.run('let x = 10; print(x)')
    """
    try:
        lexer = DNACryptLexer(code.strip())
        tokens = lexer.tokenize()
        parser = DNACryptParser(tokens)
        ast = parser.parse()
        
        if use_semantic_analysis and SEMANTIC_AVAILABLE:
            analyzer = SemanticAnalyzer()
            if not analyzer.analyze(ast):
                analyzer.print_errors()
                return False
        
        interpreter = DNACryptInterpreter()
        interpreter.interpret(ast)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_file(filename: str, use_semantic_analysis: bool = False):
    """
    Run DNACrypt file
    
    Example:
        import dnacrypt
        dnacrypt.run_file('program.dnac')
    """
    with open(filename, 'r') as f:
        code = f.read()
    return run(code, use_semantic_analysis)


__all__ = ['run', 'run_file', 'DNACryptLexer', 'DNACryptParser', 'DNACryptInterpreter']
