from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_text, job_description, resume_skills=None, job_skills=None):
    """
    Calculates ATS score using AI similarity (TF-IDF and Cosine Similarity)
    and Skill Match Percentage.
    
    Args:
        resume_text (str): Preprocessed resume text.
        job_description (str): Preprocessed job description text.
        resume_skills (list): Extracted skills from resume.
        job_skills (list): Extracted skills from job description.
        
    Returns:
        dict: A dictionary containing 'score', 'similarity', and 'skill_match_percentage'.
    """
    similarity_score = 0.0
    if resume_text and job_description:
        try:
            # Initialize TF-IDF Vectorizer
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = float(similarity_matrix[0][0])
        except Exception as e:
            print(f"Error calculating similarity: {e}")

    # Skill match percentage calculation
    if job_skills and len(job_skills) > 0:
        matched_count = len([s for s in job_skills if resume_skills and s in resume_skills])
        skill_match_percentage = round((matched_count / len(job_skills)) * 100, 2)
        score = int(skill_match_percentage)
    else:
        skill_match_percentage = 0.0
        score = int(similarity_score * 100)

    return {
        "score": score,
        "similarity": similarity_score,
        "skill_match_percentage": skill_match_percentage
    }
