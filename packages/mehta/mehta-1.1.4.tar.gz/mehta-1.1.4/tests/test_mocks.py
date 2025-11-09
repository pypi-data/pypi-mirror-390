class MockMessage:
    """Mock Telegram Message object"""
    def __init__(self, text="", chat_id=123, message_id=1):
        self.text = text
        self.chat = type('Chat', (), {'id': chat_id})()
        self.message_id = message_id
        self.from_user = type('User', (), {'id': 456})()

class MockUser:
    """Mock Telegram User object"""
    def __init__(self, user_id=456):
        self.id = user_id
        self.first_name = "Test"
        self.username = "testuser"

class MockChat:
    """Mock Telegram Chat object"""
    def __init__(self, chat_id=123):
        self.id = chat_id
        self.type = "private"
        self.title = "Test Chat"