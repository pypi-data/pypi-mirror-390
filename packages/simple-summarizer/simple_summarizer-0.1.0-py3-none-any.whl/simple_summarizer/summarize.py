
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
import heapq

# Download essential NLTK components if not already downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def summarize_text(text, num_sentences):
    """
    Summarizes the input text into the specified number of sentences.

    Args:
        text (str): The input text to summarize.
        num_sentences (int): The desired number of sentences in the summary.

    Returns:
        str: The summarized text.
    """
    # Tokenize the text into individual words
    words = word_tokenize(text.lower())

    # Get English Stopwords
    stop_words = set(stopwords.words('english'))

    # Create a dictionary to store word frequencies
    word_frequencies = defaultdict(int)
    for word in words:
        # Remove punctuation and check for stop words
        if word.isalnum() and word not in stop_words:
            word_frequencies[word] += 1

    # Calculate the WEIGHTED frequency (normalization)
    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / max_frequency)

    # Tokenize the original text into sentences
    sentence_list = sent_tokenize(text)

    # Create a dictionary to store sentence scores
    sentence_scores = defaultdict(int)
    for sentence in sentence_list:
        for word in word_tokenize(sentence.lower()):
            if word.isalnum() and word in word_frequencies.keys():
                sentence_scores[sentence] += word_frequencies[word]

    # Get the top N sentences based on their scores
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)

    # Join the selected sentences to form the summary
    summary = ' '.join(summary_sentences)

    return summary
