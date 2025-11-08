# adipylib/summarizer.py

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation

# This is a one-time download for NLTK models
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpus/stopwords')
except LookupError:
    print("Downloading NLTK models (one-time setup)...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

def extractive_summary(text, num_sentences=3):
    """
    Creates a simple extractive summary of a text.
    
    :param text: The text to summarize
    :param num_sentences: The number of sentences in the final summary
    :return: A string containing the summary
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Split the text into sentences
    sentences = sent_tokenize(text)
    
    if len(sentences) <= num_sentences:
        return text # Return original text if it's already short

    # 2. Set up stop words (common words) and punctuation
    stop_words = set(stopwords.words('english') + list(punctuation))
    
    # 3. Calculate word frequencies (excluding stop words)
    word_freq = {}
    for word in word_tokenize(text.lower()):
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
            
    # 4. Score each sentence based on the frequency of its words
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_freq[word]
                
    # 5. Get the top N highest-scoring sentences
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    
    # 6. Re-order the top sentences to match their original order in the text
    summary_sentences = sorted(top_sentences, key=lambda s: sentences.index(s))
    
    return " ".join(summary_sentences)