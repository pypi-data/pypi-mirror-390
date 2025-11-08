from mehta import telegram

def test_error_handling():
    """Test error handler registration"""
    bot = telegram()
    
    @bot.error()
    def error_handler(error, message):
        return text(f"Error: {str(error)}")
    
    assert bot.errorhandler is not None

def test_exception_handling():
    """Test exception in command handler"""
    bot = telegram()
    
    @bot.commands(['crash'])
    def crash_handler(message):
        raise ValueError("Test error")
    
    # This should not crash the test
    try:
        mock_msg = MockMessage(text="/crash")
        result = bot.commandhandlers['crash'](mock_msg)
    except Exception as e:
        # Error should be caught by bot's internal handling
        assert "Test error" in str(e)