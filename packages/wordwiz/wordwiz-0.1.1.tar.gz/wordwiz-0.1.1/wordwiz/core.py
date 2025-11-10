import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

def preprocess_text(text):
    """
    Tokenize, lowercase, and remove stopwords/non-alphabetic tokens.
    Returns a list of clean tokens.
    """
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return [w for w in tokens if w.isalpha() and w not in stop_words]

def get_word_frequencies(text):
    """
    Compute word frequencies from text and return a Counter object.
    """
    tokens = preprocess_text(text)
    return Counter(tokens)

def show_basic_stats(freqs, top_n=5):
    """
    Display key text statistics: total words, unique words, and most common terms.
    """
    total_words = sum(freqs.values())
    unique_words = len(freqs)
    most_common = freqs.most_common(top_n)

    print("TEXT STATS")
    print(f"Total words (after cleaning): {total_words}")
    print(f"Unique words: {unique_words}")
    print(f"Top {top_n} most common words:")
    for word, count in most_common:
        print(f"  • {word}: {count}")
