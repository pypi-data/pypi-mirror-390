def count_telugu_chars(text):
    """
    Count the number of Telugu characters in a string.

    Args:
        text (str): Input text

    Returns:
        int: Number of Telugu characters
    """
    if text is None or not isinstance(text, str):
        return 0
    return sum(1 for ch in text if '\u0C00' <= ch <= '\u0C7F')


def count_english_chars(text):
    """
    Count the number of English characters in a string.

    Args:
        text (str): Input text

    Returns:
        int: Number of English characters (a-z, A-Z)
    """
    if text is None or not isinstance(text, str):
        return 0
    import re
    return len(re.findall(r'[a-zA-Z]', text))


def count_digits(text):
    """
    Count the number of digits in a string.

    Args:
        text (str): Input text

    Returns:
        int: Number of digit characters
    """
    if text is None or not isinstance(text, str):
        return 0
    return sum(1 for ch in text if ch.isdigit())


def is_telugu_text(text):
    """
    Check if text contains Telugu characters.

    Args:
        text (str): Input text

    Returns:
        bool: True if text contains Telugu characters
    """
    if text is None or not isinstance(text, str):
        return False
    return any('\u0C00' <= ch <= '\u0C7F' for ch in text)


def split_telugu_words(text):
    """
    Split text into Telugu words.

    Args:
        text (str): Input text

    Returns:
        list: List of Telugu words
    """
    if text is None or not isinstance(text, str):
        return []
    import re
    # Match Telugu characters
    words = re.findall(r'[\u0C00-\u0C7F]+', text)
    return words


def get_text_stats(text):
    """
    Get comprehensive statistics about the text.

    Args:
        text (str): Input text

    Returns:
        dict: Dictionary with text statistics
    """
    if text is None or not isinstance(text, str):
        return {
            'total_chars': 0,
            'telugu_chars': 0,
            'english_chars': 0,
            'digits': 0,
            'telugu_words': 0,
            'is_telugu': False
        }
    
    stats = {
        'total_chars': len(text),
        'telugu_chars': count_telugu_chars(text),
        'english_chars': count_english_chars(text),
        'digits': count_digits(text),
        'telugu_words': len(split_telugu_words(text)),
        'is_telugu': is_telugu_text(text)
    }
    return stats
