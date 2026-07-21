import spacy

# Load spaCy NLP model (make sure to run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: 'en_core_web_sm' model not found. Downloading it now...")
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define our Skill Database as requested
SKILL_DB = [
    "Python", "Java", "SQL", "MySQL", "React", "JavaScript", "HTML", 
    "CSS", "Flask", "Django", "Machine Learning", "Data Analysis", 
    "Power BI", "Excel", "Git", "GitHub", "Docker", "AWS"
]

def extract_skills(text):
    """
    Extract technical skills from the resume text using spaCy PhraseMatcher or basic NER-like extraction.
    
    Args:
        text (str): Preprocessed or raw text of the resume.
        
    Returns:
        list: Extracted skills.
    """
    if not text:
        return []
        
    # Process text using spaCy
    doc = nlp(text)
    
    # We can use spaCy's built-in PhraseMatcher for exact multi-word matching,
    # or just do a simple lemma/text match for this beginner-friendly approach.
    extracted = set()
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    for skill in SKILL_DB:
        skill_lower = skill.lower()
        
        # Simple exact substring match (or word boundary match)
        # Using word boundaries to avoid partial word matches like "CSS" inside "ACCESS"
        import re
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        if re.search(pattern, text_lower):
            extracted.add(skill)
            
    return list(extracted)
