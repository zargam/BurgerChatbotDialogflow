from word2number import w2n

def words_to_numbers(text):
    """Converts number words in a string to numbers (handles only full numbers, not partial)."""
    words = text.lower().split()
    converted_words = []

    for word in words:
        try:
            # Try converting word to a number
            number = w2n.word_to_num(word)
            converted_words.append(str(number))
        except ValueError:
            converted_words.append(word)

    return " ".join(converted_words)

def str_to_int(text):
    """Converts a string like 'one' or 'two' or even full phrases like 'twenty five' to int."""
    try:
        return w2n.word_to_num(text.lower())
    except ValueError:
        return text


