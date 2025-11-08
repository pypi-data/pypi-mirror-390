# adipylib/keywords.py

# We'll use scikit-learn's TF-IDF vectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text, num_keywords=5):
    """
    Extracts the most important keywords from a block of text.
    
    :param text: The text to analyze
    :param num_keywords: The number of keywords to return
    :return: A list of the top keywords
    """
    if not text or not isinstance(text, str):
        return []

    # 1. Create the vectorizer
    #    stop_words='english' removes common words like 'the', 'is', 'in'
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # 2. Process the text
    #    We put the text in a list [text] because the vectorizer expects a collection
    tfidf_matrix = vectorizer.fit_transform([text])
    
    # 3. Get the words (feature names)
    feature_names = vectorizer.get_feature_names_out()
    
    # 4. Get the scores for our single document
    scores = tfidf_matrix.toarray()[0]
    
    # 5. Get the indices of the top N scores
    #    This is a fancy numpy-style way to sort
    top_indices = scores.argsort()[-num_keywords:][::-1]
    
    # 6. Map the top indices back to the actual words
    top_keywords = [feature_names[i] for i in top_indices]
    
    return top_keywords