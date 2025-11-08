import os, sys, traceback
from telethon import TelegramClient, events
from telethon.tl.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    ReplyKeyboardRemove, ReplyInlineMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo
)
"""
Project Metadata:
    Author: Starexx
    License: MIT
""""
class client:
    def __init__(self):
        self.client = None
        self.commandhandlers = {}
        self.messagehandler = None
        self._inject_helpers()
        
    def _inject_helpers(self):
        """Inject all helper functions into caller's global namespace"""
        import inspect
        
        # Get the module where telethon class was imported
        caller_frame = inspect.stack()[2]
        caller_globals = caller_frame[0].f_globals
        
        helpers = {
            'text': self._text, 
            'photo': self._photo, 
            'button': self._button, 
            'keyboard': self._keyboard, 
            'inline': self._inline, 
            'video': self._video,
            'audio': self._audio, 
            'document': self._document, 
            'voice': self._voice,
            'sticker': self._sticker, 
            'animation': self._animation, 
            'location': self._location,
            'poll': self._poll, 
            'contact': self._contact,
            'venue': self._venue, 
            'mediagroup': self._mediagroup,
            'delete': self._delete, 
            'edit': self._edit,
            'forward': self._forward, 
            'pin': self._pin, 
            'unpin': self._unpin,
        }
        
        for name, func in helpers.items():
            caller_globals[name] = func

    # -*- helper functions -*-
    def _text(self, content, parse=None, receiver=None, reply_to=None, preview=True, notify=True):
        return {'type': 'text', 'text': content, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'preview': preview, 'notify': notify}
    
    def _photo(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'photo', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _button(self, text, url=None, data=None):
        return {'text': text, 'url': url, 'data': data}
    
    def _keyboard(self, text, buttons, parse=None, receiver=None, reply_to=None, preview=True, notify=True):
        return {'type': 'keyboard', 'text': text, 'buttons': buttons, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'preview': preview, 'notify': notify}
    
    def _inline(self, text, buttons, parse=None, receiver=None, reply_to=None, preview=True, notify=True):
        return {'type': 'inline', 'text': text, 'buttons': buttons, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'preview': preview, 'notify': notify}
    
    def _video(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'video', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _audio(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'audio', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _document(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'document', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _voice(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'voice', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _sticker(self, file, receiver=None, reply_to=None, notify=True):
        return {'type': 'sticker', 'file': file, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _animation(self, file, caption=None, parse=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'animation', 'file': file, 'caption': caption, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _location(self, lat, lon, receiver=None, reply_to=None, notify=True):
        return {'type': 'location', 'lat': lat, 'lon': lon, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _poll(self, question, options, receiver=None, reply_to=None, notify=True):
        return {'type': 'poll', 'question': question, 'options': options, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _contact(self, phone, first_name, last_name=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'contact', 'phone': phone, 'first_name': first_name, 'last_name': last_name, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _venue(self, lat, lon, title, address, receiver=None, reply_to=None, notify=True):
        return {'type': 'venue', 'lat': lat, 'lon': lon, 'title': title, 'address': address, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _mediagroup(self, media_list, receiver=None, reply_to=None, notify=True):
        return {'type': 'mediagroup', 'media': media_list, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _delete(self, message_id, receiver=None):
        return {'type': 'delete', 'message_id': message_id, 'receiver': receiver}
    
    def _edit(self, message_id, text, parse=None, receiver=None, preview=True):
        return {'type': 'edittext', 'message_id': message_id, 'text': text, 'parse': parse, 'receiver': receiver, 'preview': preview}
    
    def _forward(self, to_chat, message_id, receiver=None, notify=True):
        return {'type': 'forward', 'to': to_chat, 'message_id': message_id, 'receiver': receiver, 'notify': notify}
    
    def _pin(self, message_id, receiver=None, notify=True):
        return {'type': 'pin', 'message_id': message_id, 'receiver': receiver, 'notify': notify}
    
    def _unpin(self, message_id=None, receiver=None):
        return {'type': 'unpin', 'message_id': message_id, 'receiver': receiver}
    
    def commands(self, commandlist):
        def decorator(func):
            for cmd in commandlist:
                self.commandhandlers[cmd] = func
            return func
        return decorator
    
    def message(self):
        def decorator(func):
            self.messagehandler = func
            return func
        return decorator
    
    def run(self, api_id, api_hash):
        try:
            self.client = TelegramClient('session', api_id, api_hash)
            
            @self.client.on(events.NewMessage)
            async def handler(event):
                message = event.message
                if message.text and message.text.startswith('/'):
                    command = message.text[1:].split()[0]
                    if command in self.commandhandlers:
                        result = self.commandhandlers[command](message)
                        await self.process(message, result)
                elif self.messagehandler:
                    result = self.messagehandler(message)
                    await self.process(message, result)
            
            print("Bot started...")
            self.client.start()
            self.client.run_until_disconnected()
            
        except Exception:
            error = self.cleanerror()
            print(f"Error: {error}")
    
    def cleanerror(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        return tb_list[-1].strip()
    
    async def process(self, message, result):
        try:
            if result is None:
                return
                
            if isinstance(result, dict):
                msgtype = result.get('type', 'text')
                
                if msgtype == 'text':
                    await message.reply(
                        result['text'],
                        link_preview=result.get('preview', True)
                    )
                
                elif msgtype == 'photo':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'video':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'audio':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'document':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'voice':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'sticker':
                    await message.reply(file=result['file'])
                
                elif msgtype == 'animation':
                    await message.reply(
                        file=result['file'],
                        message=result.get('caption')
                    )
                
                elif msgtype == 'location':
                    await message.reply(
                        location=(result['lat'], result['lon'])
                    )
                
                elif msgtype == 'poll':
                    await message.reply(
                        result['question'],
                        buttons=[str(opt) for opt in result['options']]
                    )
                
                elif msgtype == 'contact':
                    await message.reply(
                        contact=(result['phone'], result['first_name'], result.get('last_name', ''))
                    )
                
                elif msgtype == 'delete':
                    await message.delete()
                
                elif msgtype == 'edittext':
                    await message.edit(result['text'])
                
                elif msgtype == 'forward':
                    await message.forward_to(result['to'])
                
                elif msgtype == 'pin':
                    await message.pin()
                
                elif msgtype == 'unpin':
                    await message.unpin()
                
                else:
                    await message.reply(str(result))
            else:
                await message.reply(str(result))
                
        except Exception:
            error = self.cleanerror()
            print(f"Error: {error}")