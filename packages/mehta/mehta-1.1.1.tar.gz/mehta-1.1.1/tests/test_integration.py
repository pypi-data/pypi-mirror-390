import pytest
from mehta import telegram

class TestIntegration:
    def setup_method(self):
        self.bot = telegram()
    
    def test_complete_flow(self):
        """Test complete bot flow"""
        @self.bot.commands(['echo'])
        def echo_handler(message):
            return text(f"Echo: {message.text}")
        
        @self.bot.message()
        def message_handler(message):
            return text(f"You said: {message.text}")
        
        # Test command
        mock_msg = MockMessage(text="/echo hello")
        result = self.bot.commandhandlers['echo'](mock_msg)
        assert "Echo: /echo hello" in result['text']
        
        # Test message
        mock_msg = MockMessage(text="regular message")
        result = message_handler(mock_msg)
        assert "You said: regular message" in result['text']