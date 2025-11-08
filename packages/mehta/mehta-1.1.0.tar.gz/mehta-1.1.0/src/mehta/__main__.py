import sys
import os

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    bot_file = sys.argv[1]
    
    if not os.path.exists(bot_file):
        print(f"Error: File {bot_file} not found")
        sys.exit(1)
    
    try:
        with open(bot_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        globals_dict = {
            '__name__': '__main__',
            '__file__': bot_file
        }
        
        exec(code, globals_dict)
        
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()