# -*- coding: utf-8 -*-
import sys, traceback, os, requests
from telebot.types import *
from io import BytesIO
import threading, time
import telebot

"""
Main source for mehta package:

It works with two different types of syntax:
    1. Dictionary Based
    2. Function Based    

Project Metadata:
    Author: Starexx
    License: MIT
"""

class telegram:
    def __init__(self):
        """Initialize telegram bot with all helper functions available globally"""
        self.bot = None
        self.commandhandlers = {}
        self.messagehandler = None
        self.errorhandler = None
        self.rate_limits = {}
        self._inject_helpers()
    
    def _inject_helpers(self):
        """Inject all helper functions into caller's global namespace"""
        import inspect
        
        # Get the module where telegram class was imported
        caller_frame = inspect.stack()[2]  # Changed from 1 to 2 to get the actual caller module
        caller_globals = caller_frame[0].f_globals
        
        helpers = {
            'text': self._text, 'photo': self._photo, 'button': self._button, 
            'keyboard': self._keyboard, 'inline': self._inline, 'video': self._video,
            'audio': self._audio, 'document': self._document, 'voice': self._voice,
            'sticker': self._sticker, 'animation': self._animation, 'location': self._location,
            'poll': self._poll, 'dice': self._dice, 'delete': self._delete, 'edit': self._edit,
            'forward': self._forward, 'copy': self._copy, 'contact': self._contact,
            'venue': self._venue, 'mediagroup': self._mediagroup, 'remove_keyboard': self._remove_keyboard,
            'force_reply': self._force_reply, 'pin': self._pin, 'unpin': self._unpin,
            'unpin_all': self._unpin_all, 'ban': self._ban, 'unban': self._unban,
            'restrict': self._restrict, 'promote': self._promote, 'chat_info': self._chat_info,
            'member_count': self._member_count, 'member_info': self._member_info,
            'invite_link': self._invite_link, 'set_title': self._set_title,
            'set_description': self._set_description, 'set_photo': self._set_photo,
            'delete_photo': self._delete_photo
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
    
    def _dice(self, emoji='🎲', receiver=None, reply_to=None, notify=True):
        return {'type': 'dice', 'emoji': emoji, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _delete(self, message_id, receiver=None):
        return {'type': 'delete', 'message_id': message_id, 'receiver': receiver}
    
    def _edit(self, message_id, text, parse=None, receiver=None, preview=True):
        return {'type': 'edittext', 'message_id': message_id, 'text': text, 'parse': parse, 'receiver': receiver, 'preview': preview}
    
    def _forward(self, to_chat, message_id, receiver=None, notify=True):
        return {'type': 'forward', 'to': to_chat, 'message_id': message_id, 'receiver': receiver, 'notify': notify}
    
    def _copy(self, to_chat, message_id, caption=None, parse=None, receiver=None, notify=True):
        return {'type': 'copy', 'to': to_chat, 'message_id': message_id, 'caption': caption, 'parse': parse, 'receiver': receiver, 'notify': notify}
    
    def _contact(self, phone, first_name, last_name=None, receiver=None, reply_to=None, notify=True):
        return {'type': 'contact', 'phone': phone, 'first_name': first_name, 'last_name': last_name, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _venue(self, lat, lon, title, address, receiver=None, reply_to=None, notify=True):
        return {'type': 'venue', 'lat': lat, 'lon': lon, 'title': title, 'address': address, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _mediagroup(self, media_list, receiver=None, reply_to=None, notify=True):
        return {'type': 'mediagroup', 'media': media_list, 'receiver': receiver, 'reply_to': reply_to, 'notify': notify}
    
    def _remove_keyboard(self, text, parse=None, receiver=None, reply_to=None, preview=True, notify=True):
        return {'type': 'removekeyboard', 'text': text, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'preview': preview, 'notify': notify}
    
    def _force_reply(self, text, parse=None, receiver=None, reply_to=None, preview=True, notify=True):
        return {'type': 'forcereply', 'text': text, 'parse': parse, 'receiver': receiver, 'reply_to': reply_to, 'preview': preview, 'notify': notify}
    
    def _pin(self, message_id, receiver=None, notify=True):
        return {'type': 'pin', 'message_id': message_id, 'receiver': receiver, 'notify': notify}
    
    def _unpin(self, message_id=None, receiver=None):
        return {'type': 'unpin', 'message_id': message_id, 'receiver': receiver}
    
    def _unpin_all(self, receiver=None):
        return {'type': 'unpinall', 'receiver': receiver}
    
    def _ban(self, user_id, until_date=None, receiver=None):
        return {'type': 'ban', 'user': user_id, 'until': until_date, 'receiver': receiver}
    
    def _unban(self, user_id, receiver=None):
        return {'type': 'unban', 'user': user_id, 'receiver': receiver}
    
    def _restrict(self, user_id, permissions=None, until_date=None, receiver=None):
        return {'type': 'restrict', 'user': user_id, 
                'send': permissions.get('send', False) if permissions else False,
                'media': permissions.get('media', False) if permissions else False,
                'polls': permissions.get('polls', False) if permissions else False,
                'other': permissions.get('other', False) if permissions else False,
                'previews': permissions.get('previews', False) if permissions else False,
                'until': until_date, 'receiver': receiver}

    def _promote(self, user_id, privileges=None, receiver=None):
        return {'type': 'promote', 'user': user_id,
                'change_info': privileges.get('change_info', False) if privileges else False,
                'post': privileges.get('post', False) if privileges else False,
                'edit': privileges.get('edit', False) if privileges else False,
                'delete': privileges.get('delete', False) if privileges else False,
                'invite': privileges.get('invite', False) if privileges else False,
                'restrict': privileges.get('restrict', False) if privileges else False,
                'pin': privileges.get('pin', False) if privileges else False,
                'promote': privileges.get('promote', False) if privileges else False,
                'receiver': receiver}

    def _chat_info(self, receiver=None):
        return {'type': 'chatinfo', 'receiver': receiver}
    
    def _member_count(self, receiver=None):
        return {'type': 'membercount', 'receiver': receiver}
    
    def _member_info(self, user_id, receiver=None):
        return {'type': 'memberinfo', 'user': user_id, 'receiver': receiver}
    
    def _invite_link(self, receiver=None):
        return {'type': 'invitelink', 'receiver': receiver}
    
    def _set_title(self, title, receiver=None):
        return {'type': 'settitle', 'title': title, 'receiver': receiver}
    
    def _set_description(self, description, receiver=None):
        return {'type': 'setdescription', 'description': description, 'receiver': receiver}
    
    def _set_photo(self, file, receiver=None):
        return {'type': 'setphoto', 'file': file, 'receiver': receiver}
    
    def _delete_photo(self, receiver=None):
        return {'type': 'deletephoto', 'receiver': receiver}

    # -*- bot decorators -*-
    def commands(self, commandlist, rate_limit=None, timeout=None):
        """Decorator to register command handlers"""
        def decorator(func):
            for cmd in commandlist:
                self.commandhandlers[cmd] = {
                    'func': func,
                    'rate_limit': rate_limit,
                    'timeout': timeout
                }
            return func
        return decorator
    
    def message(self):
        """Decorator to register message handler"""
        def decorator(func):
            self.messagehandler = func
            return func
        return decorator
    
    def error(self):
        """Decorator to register error handler"""
        def decorator(func):
            self.errorhandler = func
            return func
        return decorator

    # -*- bot operations -*-
    def run(self, token):
        """Start bot polling"""
        try:
            self.bot = telebot.TeleBot(token)
            
            # Register command handlers
            for cmd, handler_data in self.commandhandlers.items():
                @self.bot.message_handler(commands=[cmd])
                def handlecommand(message, cmd=cmd, handler_data=handler_data):
                    if self._check_rate_limit(message.from_user.id, cmd, handler_data['rate_limit']):
                        self._execute_with_timeout(message, handler_data, cmd)
                    else:
                        self.bot.reply_to(message, "Rate limit exceeded. Please wait.")
            
            # Register message handler
            if self.messagehandler:
                @self.bot.message_handler(func=lambda m: True)
                def handlemessage(message):
                    self._execute_handler(message, self.messagehandler)
            
            self.bot.polling(none_stop=True, timeout=60)
            
        except Exception as e:
            self._handle_error(e)
    
    def webhook(self, token, url, port=8000):
        """Set webhook for bot"""
        try:
            self.bot = telebot.TeleBot(token)
            self.bot.set_webhook(url=url)
            print(f"Webhook set: {url}")
        except Exception as e:
            self._handle_error(e)

    # -*- internal methods -*-
    def _check_rate_limit(self, user_id, command, rate_limit):
        """Check if user has exceeded rate limit"""
        if not rate_limit: return True
            
        key = f"{user_id}:{command}"
        now = time.time()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old entries
        self.rate_limits[key] = [t for t in self.rate_limits[key] if now - t < 60]
        
        if len(self.rate_limits[key]) < rate_limit:
            self.rate_limits[key].append(now)
            return True
        return False
    
    def _execute_with_timeout(self, message, handler_data, cmd):
        """Execute handler with timeout"""
        def target():
            try:
                result = handler_data['func'](message)
                self._send_response(message, result)
            except Exception as e:
                self._handle_error(e, message)
        
        if handler_data['timeout']:
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(handler_data['timeout'])
            if thread.is_alive():
                self.bot.reply_to(message, f"Command timeout after {handler_data['timeout']} seconds")
        else:
            target()
    
    def _execute_handler(self, message, handler):
        """Execute message handler"""
        try:
            result = handler(message)
            self._send_response(message, result)
        except Exception as e:
            self._handle_error(e, message)
    
    def _handle_error(self, error, message=None):
        """Handle errors gracefully"""
        error_msg = self._clean_error()
        print(f"Error: {error_msg}")
        
        if self.errorhandler and message:
            try:
                result = self.errorhandler(error, message)
                self._send_response(message, result)
            except: pass
    
    def _clean_error(self):
        """Clean error traceback"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for i, line in enumerate(tb_list):
            line = line.replace('telebot.', 'mehta.')
            tb_list[i] = line
        return tb_list[-1].strip()
    
    def _get_file_content(self, fileinput):
        """Get file content from various sources"""
        if isinstance(fileinput, str):
            if fileinput.startswith(('http://', 'https://')):
                response = requests.get(fileinput)
                return BytesIO(response.content)
            elif os.path.exists(fileinput):
                with open(fileinput, 'rb') as f:
                    return BytesIO(f.read())
            else:
                return fileinput
        return fileinput
    
    def _send_response(self, message, result):
        """Send response to user - MAIN FIX: Auto-fill receiver and reply_to"""
        try:
            if result is None: return
                
            if isinstance(result, dict):
                # CRITICAL FIX: Auto-fill missing fields
                if 'receiver' not in result or result['receiver'] is None:
                    result['receiver'] = message.chat.id
                if 'reply_to' not in result or result['reply_to'] is None:
                    result['reply_to'] = message.message_id
                self._process_dict_result(message, result)
            else:
                # For string responses, use simple reply
                self.bot.reply_to(message, str(result))
                
        except Exception as e:
            self._handle_error(e, message)
    
    def _process_dict_result(self, message, result):
        """Process dictionary-based responses"""
        msgtype = result.get('type', 'text')
        parse = result.get('parse')
        receiver = result.get('receiver', message.chat.id)
        replyto = result.get('reply_to', message.message_id)
        preview = result.get('preview', True)
        notify = result.get('notify', True)
        
        # Handle different message types
        if msgtype == 'text':
            self.bot.send_message(receiver, result['text'], parse_mode=parse,
                                reply_to_message_id=replyto, disable_web_page_preview=not preview,
                                disable_notification=not notify)
        
        elif msgtype == 'photo':
            file = self._get_file_content(result['file'])
            self.bot.send_photo(receiver, file, caption=result.get('caption'),
                              parse_mode=parse, reply_to_message_id=replyto,
                              disable_notification=not notify)
        
        elif msgtype == 'video':
            file = self._get_file_content(result['file'])
            self.bot.send_video(receiver, file, caption=result.get('caption'),
                              parse_mode=parse, reply_to_message_id=replyto,
                              disable_notification=not notify)
        
        elif msgtype == 'audio':
            file = self._get_file_content(result['file'])
            self.bot.send_audio(receiver, file, caption=result.get('caption'),
                              parse_mode=parse, reply_to_message_id=replyto,
                              disable_notification=not notify)
        
        elif msgtype == 'document':
            file = self._get_file_content(result['file'])
            self.bot.send_document(receiver, file, caption=result.get('caption'),
                                 parse_mode=parse, reply_to_message_id=replyto,
                                 disable_notification=not notify)
        
        elif msgtype == 'sticker':
            file = self._get_file_content(result['file'])
            self.bot.send_sticker(receiver, file, reply_to_message_id=replyto,
                                disable_notification=not notify)
        
        elif msgtype == 'voice':
            file = self._get_file_content(result['file'])
            self.bot.send_voice(receiver, file, caption=result.get('caption'),
                              parse_mode=parse, reply_to_message_id=replyto,
                              disable_notification=not notify)
        
        elif msgtype == 'animation':
            file = self._get_file_content(result['file'])
            self.bot.send_animation(receiver, file, caption=result.get('caption'),
                                  parse_mode=parse, reply_to_message_id=replyto,
                                  disable_notification=not notify)
        
        elif msgtype == 'location':
            self.bot.send_location(receiver, result['lat'], result['lon'],
                                 reply_to_message_id=replyto, disable_notification=not notify)
        
        elif msgtype == 'venue':
            self.bot.send_venue(receiver, result['lat'], result['lon'],
                              result['title'], result['address'], reply_to_message_id=replyto,
                              disable_notification=not notify)
        
        elif msgtype == 'contact':
            self.bot.send_contact(receiver, result['phone'], result['first_name'],
                                result.get('last_name'), reply_to_message_id=replyto,
                                disable_notification=not notify)
        
        elif msgtype == 'poll':
            self.bot.send_poll(receiver, result['question'], result['options'],
                             reply_to_message_id=replyto, disable_notification=not notify)
        
        elif msgtype == 'dice':
            self.bot.send_dice(receiver, result.get('emoji', '🎲'),
                             reply_to_message_id=replyto, disable_notification=not notify)
        
        elif msgtype == 'mediagroup':
            media = []
            for item in result['media']:
                file = self._get_file_content(item['file'])
                if item['type'] == 'photo':
                    media.append(InputMediaPhoto(file, caption=item.get('caption'), parse_mode=parse))
                elif item['type'] == 'video':
                    media.append(InputMediaVideo(file, caption=item.get('caption'), parse_mode=parse))
            self.bot.send_media_group(receiver, media, disable_notification=not notify)
        
        elif msgtype == 'keyboard':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            for row in result['buttons']:
                markup.add(*[KeyboardButton(btn) for btn in row])
            self.bot.send_message(receiver, result['text'], reply_markup=markup,
                                parse_mode=parse, reply_to_message_id=replyto,
                                disable_web_page_preview=not preview, disable_notification=not notify)
        
        elif msgtype == 'inline':
            markup = InlineKeyboardMarkup()
            for row in result['buttons']:
                rowbuttons = []
                for btn in row:
                    if btn.get('url'):
                        rowbuttons.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                    elif btn.get('data'):
                        rowbuttons.append(InlineKeyboardButton(btn['text'], callback_data=btn['data']))
                    else:
                        rowbuttons.append(InlineKeyboardButton(btn['text']))
                markup.add(*rowbuttons)
            self.bot.send_message(receiver, result['text'], reply_markup=markup,
                                parse_mode=parse, reply_to_message_id=replyto,
                                disable_web_page_preview=not preview, disable_notification=not notify)
        
        elif msgtype == 'removekeyboard':
            self.bot.send_message(receiver, result['text'],
                                reply_markup=ReplyKeyboardRemove(), parse_mode=parse,
                                reply_to_message_id=replyto, disable_web_page_preview=not preview,
                                disable_notification=not notify)
        
        elif msgtype == 'forcereply':
            self.bot.send_message(receiver, result['text'],
                                reply_markup=ForceReply(), parse_mode=parse,
                                reply_to_message_id=replyto, disable_web_page_preview=not preview,
                                disable_notification=not notify)
        
        elif msgtype == 'delete':
            self.bot.delete_message(receiver, result.get('message_id', message.message_id))
        
        elif msgtype == 'edittext':
            self.bot.edit_message_text(result['text'], receiver,
                                     result.get('message_id', message.message_id),
                                     parse_mode=parse, disable_web_page_preview=not preview)
        
        elif msgtype == 'editcaption':
            self.bot.edit_message_caption(receiver, result.get('message_id', message.message_id),
                                        caption=result['caption'], parse_mode=parse)
        
        elif msgtype == 'editmarkup':
            markup = InlineKeyboardMarkup()
            for row in result['buttons']:
                rowbuttons = []
                for btn in row:
                    if btn.get('url'):
                        rowbuttons.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                    elif btn.get('data'):
                        rowbuttons.append(InlineKeyboardButton(btn['text'], callback_data=btn['data']))
                    else:
                        rowbuttons.append(InlineKeyboardButton(btn['text']))
                markup.add(*rowbuttons)
            self.bot.edit_message_reply_markup(receiver, result.get('message_id', message.message_id),
                                             reply_markup=markup)
        
        elif msgtype == 'pin':
            self.bot.pin_chat_message(receiver, result.get('message_id', message.message_id),
                                    disable_notification=not notify)
        
        elif msgtype == 'unpin':
            self.bot.unpin_chat_message(receiver, result.get('message_id', message.message_id))
        
        elif msgtype == 'unpinall':
            self.bot.unpin_all_chat_messages(receiver)
        
        elif msgtype == 'forward':
            self.bot.forward_message(result['to'], receiver,
                                   result.get('message_id', message.message_id),
                                   disable_notification=not notify)
        
        elif msgtype == 'copy':
            self.bot.copy_message(result['to'], receiver,
                                result.get('message_id', message.message_id),
                                caption=result.get('caption'), parse_mode=parse,
                                disable_notification=not notify)
        
        elif msgtype == 'ban':
            self.bot.ban_chat_member(receiver, result['user'],
                                   until_date=result.get('until'))
        
        elif msgtype == 'unban':
            self.bot.unban_chat_member(receiver, result['user'])
        
        elif msgtype == 'kick':
            self.bot.kick_chat_member(receiver, result['user'])
        
        elif msgtype == 'leave':
            self.bot.leave_chat(receiver)
        
        elif msgtype == 'restrict':
            self.bot.restrict_chat_member(receiver, result['user'],
                                        until_date=result.get('until'),
                                        can_send_messages=result.get('send', False),
                                        can_send_media_messages=result.get('media', False),
                                        can_send_polls=result.get('polls', False),
                                        can_send_other_messages=result.get('other', False),
                                        can_add_web_page_previews=result.get('previews', False))
        
        elif msgtype == 'promote':
            self.bot.promote_chat_member(receiver, result['user'],
                                       can_change_info=result.get('change_info', False),
                                       can_post_messages=result.get('post', False),
                                       can_edit_messages=result.get('edit', False),
                                       can_delete_messages=result.get('delete', False),
                                       can_invite_users=result.get('invite', False),
                                       can_restrict_members=result.get('restrict', False),
                                       can_pin_messages=result.get('pin', False),
                                       can_promote_members=result.get('promote', False))
        
        elif msgtype == 'settitle':
            self.bot.set_chat_title(receiver, result['title'])
        
        elif msgtype == 'setdescription':
            self.bot.set_chat_description(receiver, result['description'])
        
        elif msgtype == 'setphoto':
            file = self._get_file_content(result['file'])
            self.bot.set_chat_photo(receiver, file)
        
        elif msgtype == 'deletephoto':
            self.bot.delete_chat_photo(receiver)
        
        elif msgtype == 'invitelink':
            link = self.bot.export_chat_invite_link(receiver)
            self.bot.send_message(receiver, f"Invite: {link}")
        
        elif msgtype == 'chatinfo':
            info = self.bot.get_chat(receiver)
            self.bot.send_message(receiver, str(info))
        
        elif msgtype == 'membercount':
            count = self.bot.get_chat_members_count(receiver)
            self.bot.send_message(receiver, f"Members: {count}")
        
        elif msgtype == 'memberinfo':
            info = self.bot.get_chat_member(receiver, result['user'])
            self.bot.send_message(receiver, str(info))
        
        else:
            self.bot.send_message(receiver, str(result), parse_mode=parse,
                                reply_to_message_id=replyto, disable_web_page_preview=not preview,
                                disable_notification=not notify)