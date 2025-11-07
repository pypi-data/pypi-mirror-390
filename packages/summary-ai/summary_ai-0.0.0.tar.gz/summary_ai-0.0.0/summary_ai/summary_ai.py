import re
from collections import Counter

def summarize_text(text, max_sentences=3):
    """
    Generates an extractive summary by selecting the most informative sentences.

    Parameters
    ----------
    text : str
        Input text to summarize.
    max_sentences : int, optional (default=3)
        Number of sentences to include in the summary.

    Returns
    -------
    str
        Extractive summary containing top-ranked sentences.

    Example
    -------
    >>> text = "Artificial Intelligence improves decision making. It automates tasks. It saves time and cost."
    >>> summarize_text(text, max_sentences=2)
    'Artificial Intelligence improves decision making. It automates tasks.'
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")
    if not text.strip():
        return ""

    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    if len(sentences) <= max_sentences:
        return text

    # Tokenize words and compute word frequencies
    words = re.findall(r'\w+', text.lower())
    freq = Counter(words)

    # Score sentences based on word frequency
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = re.findall(r'\w+', sentence.lower())
        score = sum(freq[w] for w in sentence_words)
        sentence_scores[sentence] = score / max(1, len(sentence_words))

    # Select top N sentences
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    return " ".join(top_sentences)


if __name__ == "__main__":
    text = (
        "Artificial Intelligence is transforming industries. "
        "It enables automation and efficient decision-making. "
        "AI-driven systems can analyze large datasets quickly. "
        "This reduces cost and improves productivity."
    )
    print(summarize_text(text, max_sentences=2))
