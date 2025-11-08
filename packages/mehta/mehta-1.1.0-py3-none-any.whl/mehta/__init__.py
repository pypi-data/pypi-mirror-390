import sys, os, re
import importlib.util

from .apihelper import telegram
from .autouser import client

__all__ = ["telegram", "client"]

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command.startswith('run:'):
            parts = command[4:].split()
            filename = parts[0]
            
            run_bot_file(filename)
        else:
            print("bash: mehta run:<filename>")
    else:
        print("bash: mehta run:<filename>")

def run_bot_file(filename):
    try:
        if not filename.endswith('.py'):
            filename += '.py'
        
        if not os.path.exists(filename):
            print(f"Error: File {filename} not found")
            return
        
        with open(filename, 'r') as f:
            content = f.read()
        
        token_match = re.search(r'bot\.run\(["\']([^"\']+)["\']\)', content)
        
        if token_match:
            token = token_match.group(1)
            spec = importlib.util.spec_from_file_location("bot_module", filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'bot') and isinstance(module.bot, telegram):
                module.bot.run(token)
            else:
                print("Error: No bot instance found in file")
                
    except Exception as e:
        print(f"Error: {e}")