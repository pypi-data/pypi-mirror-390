import string

def clean_text(text, stop_words=None):
    """
    Cleans text by removing punctuation, lowercasing, tokenizing,
    and removing stop words.

    Args:
        text (str): input text string.
        stop_words (set, optional): set of stop words to remove.

    Returns:
        list: cleaned tokens.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    if stop_words is None:
        stop_words = {'the', 'is', 'at', 'on', 'in', 'and', 'a', 'to', 'of'}

    text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    tokens = text.split()
    return [word for word in tokens if word not in stop_words]

if __name__ == "__main__":
    example = "This is a simple example sentence to test the function."
    print(clean_text(example))
