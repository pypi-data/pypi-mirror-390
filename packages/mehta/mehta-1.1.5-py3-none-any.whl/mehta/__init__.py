from .apihelper import telegram
from .ext import client

import sys, os, importlib.util


__all__ = ["telegram","client"]


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


def execf(filename):
    try:
        if not filename.endswith('.py'):
            filename += '.py'

        if not os.path.exists(filename):
            print(f"Error: File {filename} not found")
            return

        spec = importlib.util.spec_from_file_location("bot_module", filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'bot') and isinstance(module.bot, telegram):
            module.bot.run()
        else:
            print("Error: No valid bot instance found in file")

    except Exception as e:
        print(f"Error: {e}")