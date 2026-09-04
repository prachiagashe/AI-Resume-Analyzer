import re

COMMON_TITLES = [
    "Business Analyst", "IT Business Analyst", "Business Systems Analyst", "Junior Business Analyst",
    "Senior Business Analyst", "Functional Analyst", "Data Analyst", "Data Scientist",
    "Python Developer", "Software Engineer", "Full Stack Developer", "Frontend Developer",
    "React Developer", "Backend Developer", "Java Developer", "DevOps Engineer"
]


def calculate_job_title_match(target_title, resume_text):
    """
    Compare target job title against extracted resume roles and compute title match score.
    """
    if not target_title or not isinstance(target_title, str) or target_title.strip() == "":
        return {
            "target": "Not specified",
            "candidate": "Candidate Role",
            "score": 100.0
        }

    target_clean = target_title.strip()
    target_lower = target_clean.lower()
    resume_lower = (resume_text or "").lower()

    # Check for exact match in resume
    if target_lower in resume_lower:
        return {
            "target": target_clean,
            "candidate": target_clean,
            "score": 100.0
        }

    # Search for related roles in resume text
    best_role = target_clean
    best_score = 50.0  # default baseline if no direct role found

    # Check common title variations
    for role in COMMON_TITLES:
        role_lower = role.lower()
        if role_lower in resume_lower:
            # Check overlap between target_lower and role_lower
            target_words = set(target_lower.split())
            role_words = set(role_lower.split())
            overlap = target_words.intersection(role_words)

            if len(overlap) > 0:
                similarity = (len(overlap) / max(len(target_words), len(role_words))) * 100.0
                # Boost if target is substring of candidate role (e.g. IT Business Analyst vs Business Analyst)
                if target_lower in role_lower or role_lower in target_lower:
                    similarity = max(similarity, 92.0)
                
                if similarity > best_score:
                    best_score = round(similarity, 1)
                    best_role = role

    # Fallback check if any target words exist in resume
    if best_score == 50.0:
        target_words = [w for w in target_lower.split() if len(w) > 2]
        matched_words = [w for w in target_words if w in resume_lower]
        if matched_words:
            best_score = round((len(matched_words) / len(target_words)) * 100.0, 1)
            best_role = f"Related {matched_words[0].title()} Role"

    return {
        "target": target_clean,
        "candidate": best_role,
        "score": min(best_score, 100.0)
    }
