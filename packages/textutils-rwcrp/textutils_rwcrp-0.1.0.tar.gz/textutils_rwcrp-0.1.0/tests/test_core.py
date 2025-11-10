from textutils_rwcrp import reverse, word_count, remove_punctuation

def test_reverse():
    assert reverse("abc") == "cba"

def test_word_count():
    assert word_count("a b c") == 3

def test_remove_punctuation():
    assert remove_punctuation("hi!") == "hi"
