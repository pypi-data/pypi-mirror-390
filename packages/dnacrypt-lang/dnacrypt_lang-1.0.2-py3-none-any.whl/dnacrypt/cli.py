"""DNACrypt CLI"""
import sys
from . import run, run_file, __version__


def repl():
    """Interactive REPL"""
    print(f"DNACrypt v{__version__} Interactive REPL")
    print("Type 'exit' to quit")
    print("-" * 60)
    
    while True:
        try:
            code = input(">>> ")
            if code.strip().lower() in ['exit', 'quit']:
                break
            if code.strip():
                run(code)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("DNACrypt v" + __version__)
        print("\nUsage:")
        print("  dnacrypt run <file.dnac>")
        print("  dnacrypt repl")
        print("  dnacrypt -c '<code>'")
        print("  dnacrypt version")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'run':
        if len(sys.argv) < 3:
            print("Error: No file specified")
            sys.exit(1)
        run_file(sys.argv[2])
    
    elif cmd == 'repl':
        repl()
    
    elif cmd == '-c':
        if len(sys.argv) < 3:
            print("Error: No code specified")
            sys.exit(1)
        run(sys.argv[2])
    
    elif cmd == 'version':
        print(f"DNACrypt v{__version__}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
