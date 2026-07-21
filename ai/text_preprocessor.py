import re

def preprocess_text(text):
    """
    Cleans resume text before analysis by converting to lowercase,
    removing special characters, and tokenizing (with a fallback if NLTK fails).
    
    Args:
        text (str): Raw extracted text.
        
    Returns:
        str: Clean processed text.
    """
    if not text:
        return ""
        
    # 1. Lowercase conversion
    text = text.lower()
    
    # 2. Remove special characters (keep only alphanumeric and spaces)
    text = re.sub(r'[^a-z0-9\s\+#]', ' ', text)
    
    tokens = text.split()
    
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        from nltk.stem import WordNetLemmatizer
        
        # Try to use NLTK if it works without crashing
        try:
            tokens_nltk = word_tokenize(text)
            tokens = tokens_nltk
        except Exception:
            pass
            
        try:
            stop_words = set(stopwords.words('english'))
        except Exception:
            stop_words = set()
            
        filtered_tokens = [word for word in tokens if word not in stop_words]
        
        try:
            lemmatizer = WordNetLemmatizer()
            lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
        except Exception:
            lemmatized_tokens = filtered_tokens
            
        return " ".join(lemmatized_tokens)

    except Exception as e:
        # Fallback if NLTK is corrupted or missing completely
        return " ".join(tokens)
