from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_text, job_description, resume_skills=None, job_skills=None, exp_score=100.0, edu_score=100.0, title_score=100.0):
    """
    Calculates multi-component weighted ATS score:
    - Skills Match: 40%
    - Experience Match: 25%
    - Education Match: 15%
    - Job Title Match: 10%
    - Semantic Match: 10%
    
    Args:
        resume_text (str): Preprocessed resume text.
        job_description (str): Preprocessed job description text.
        resume_skills (list): Extracted skills from resume.
        job_skills (list): Extracted skills from job description.
        exp_score (float): Experience match score (0-100).
        edu_score (float): Education match score (0-100).
        title_score (float): Job title match score (0-100).
        
    Returns:
        dict: A dictionary containing weighted 'score', 'similarity', 'skill_match_percentage', 'semantic_score', and 'match_status'.
    """
    similarity_score = 0.0
    if resume_text and job_description:
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = float(similarity_matrix[0][0])
        except Exception as e:
            print(f"Error calculating similarity: {e}")

    semantic_score = round(similarity_score * 100, 2)

    # Skill match percentage calculation
    if job_skills and len(job_skills) > 0:
        matched_count = len([s for s in job_skills if resume_skills and s in resume_skills])
        skill_match_percentage = round((matched_count / len(job_skills)) * 100, 2)
    else:
        skill_match_percentage = 100.0 if (job_skills is not None and len(job_skills) == 0) else 0.0

    # Multi-component Weighted ATS Formula
    weighted_score = (
        (skill_match_percentage * 0.40) +
        (exp_score * 0.25) +
        (edu_score * 0.15) +
        (title_score * 0.10) +
        (semantic_score * 0.10)
    )

    final_score = round(min(max(weighted_score, 0.0), 100.0), 2)

    # Overall Match Status
    if final_score >= 80:
        match_status = "STRONG MATCH"
    elif final_score >= 65:
        match_status = "GOOD MATCH"
    elif final_score >= 50:
        match_status = "MODERATE MATCH"
    else:
        match_status = "LOW MATCH"

    return {
        "score": final_score,
        "similarity": similarity_score,
        "skill_match_percentage": skill_match_percentage,
        "semantic_score": semantic_score,
        "match_status": match_status
    }
