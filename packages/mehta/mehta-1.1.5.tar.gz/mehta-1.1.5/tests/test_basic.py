from mehta import telegram

def test_import():
    """Test if module imports correctly"""
    bot = telegram()
    assert bot is not None

def test_helper_functions():
    """Test if helper functions are available"""
    bot = telegram()
    
    # Test text function
    result = text("Hello")
    assert result['type'] == 'text'
    assert result['text'] == 'Hello'
    
    # Test photo function
    result = photo("test.jpg", caption="Test")
    assert result['type'] == 'photo'
    assert result['file'] == 'test.jpg'