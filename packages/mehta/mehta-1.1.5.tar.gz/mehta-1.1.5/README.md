**Note**: This package is a **wrapper** that uses [pyTeleBot](https://github.com/eternnoir/pyTelegramBotAPI) and [Telethon](https://github.com/LonamiWebs/Telethon) for Telegram-related features.  
When you install it, all required dependencies including [pyTeleBot](https://github.com/eternnoir/pyTelegramBotAPI), [Telethon](https://github.com/LonamiWebs/Telethon), and others are automatically installed to ensure full functionality and seamless integration.


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
    return text("Hello World!")

bot.run("BOT_TOKEN")
```