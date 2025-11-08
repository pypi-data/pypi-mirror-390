from mehta import telegram

def test_command_registration():
    """Test command registration"""
    bot = telegram()
    
    @bot.commands(['start', 'help'])
    def handle_start(message):
        return text("Welcome!")
    
    assert 'start' in bot.commandhandlers
    assert 'help' in bot.commandhandlers

def test_command_execution():
    """Test command execution with mock message"""
    bot = telegram()
    
    @bot.commands(['test'])
    def handle_test(message):
        return text("Test successful!")
    
    # Mock message object
    class MockMessage:
        def __init__(self):
            self.text = '/test'
            self.chat = type('Chat', (), {'id': 123})()
            self.message_id = 1
    
    result = bot.commandhandlers['test'](MockMessage())
    assert result['text'] == 'Test successful!'