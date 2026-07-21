from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_text, job_description):
    """
    Calculates ATS score using AI similarity (TF-IDF and Cosine Similarity).
    
    Args:
        resume_text (str): Preprocessed resume text.
        job_description (str): Preprocessed job description text.
        
    Returns:
        dict: A dictionary containing 'score' (0-100) and 'similarity' (0.0-1.0).
    """
    if not resume_text or not job_description:
        return {"score": 0, "similarity": 0.0}

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    
    try:
        # Fit and transform the texts
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        
        # Calculate cosine similarity between the two documents
        # tfidf_matrix[0] is resume, tfidf_matrix[1] is job description
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        similarity_score = float(similarity_matrix[0][0])
        
        # Convert to percentage score
        score_percent = int(similarity_score * 100)
        
        return {
            "score": score_percent,
            "similarity": similarity_score
        }
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return {"score": 0, "similarity": 0.0}
