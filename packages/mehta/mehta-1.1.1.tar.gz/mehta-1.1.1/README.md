**Note**: This package needs pyTeleBot and Telethon for Telegram-related features. When you install Mehta, all required dependencies, including pyTeleBot, Telethon, and others, will be automatically installed to ensure full functionality and smooth integration.


## Installation
```sh
pip install mehta
```

## Basic Setup
```python
from mehta import telegram

bot = telegram()

@bot.commands(['start'])
def welcome(message):
    return {
        'type': 'text',
        'text': 'Hello World!'
    } 

bot.run("BOT_TOKEN")
```