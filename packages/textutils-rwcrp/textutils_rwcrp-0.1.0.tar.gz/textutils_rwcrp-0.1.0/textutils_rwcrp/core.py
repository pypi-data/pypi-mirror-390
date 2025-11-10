import string

def reverse(text: str) -> str:
    """Return the reversed string."""
    return text[::-1]

def word_count(text: str) -> int:
    """Count the number of words in the text."""
    return len(text.split())

def remove_punctuation(text: str) -> str:
    """Remove punctuation from the text."""
    return text.translate(str.maketrans("", "", string.punctuation))
