import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EDU_ALIASES_PATH = os.path.join(BASE_DIR, 'data', 'education_aliases.json')

_edu_data_cache = None

LEVEL_HIERARCHY = {
    'doctorate': 3,
    'master': 2,
    'bachelor': 1,
    'any': 0
}


def load_education_aliases(file_path=None):
    """
    Load education degree levels and related field aliases from education_aliases.json.
    """
    global _edu_data_cache
    if file_path is None:
        file_path = DEFAULT_EDU_ALIASES_PATH
        
    if _edu_data_cache is not None:
        return _edu_data_cache
        
    if not os.path.exists(file_path):
        _edu_data_cache = {
            "degree_levels": {
                "doctorate": ["phd", "ph.d", "doctorate"],
                "master": ["master", "m.tech", "m.e.", "mca", "m.sc", "mba", "ma", "ms"],
                "bachelor": ["bachelor", "b.tech", "b.e.", "bca", "b.sc", "bba", "ba", "bs", "degree"]
            },
            "fields": {
                "computer_science": ["computer science", "computer engineering", "cs"],
                "information_technology": ["information technology", "information systems", "it"],
                "business": ["business administration", "management", "business"]
            }
        }
        return _edu_data_cache

    with open(file_path, 'r', encoding='utf-8') as f:
        _edu_data_cache = json.load(f)
        
    return _edu_data_cache


def extract_jd_education(jd_text):
    """
    Extract education requirements from Job Description text.
    """
    if not jd_text or not isinstance(jd_text, str):
        return {
            "specified": False,
            "degree_level": None,
            "raw_text": "Education requirement not specified.",
            "degree_names": [],
            "fields": []
        }
        
    jd_lower = jd_text.lower()
    data = load_education_aliases()
    levels = data.get("degree_levels", {})
    
    detected_level = None
    detected_degree_names = []
    
    # Check for PhD / Doctorate
    for alias in levels.get("doctorate", []):
        if re.search(r'\b' + re.escape(alias) + r'\b', jd_lower):
            detected_level = "doctorate"
            detected_degree_names.append("PhD")
            break

    # Check for Master's / MBA / MCA / M.Tech
    if not detected_level:
        for alias in levels.get("master", []):
            if re.search(r'\b' + re.escape(alias) + r'\b', jd_lower):
                detected_level = "master"
                detected_degree_names.append(alias.upper() if len(alias) <= 4 else alias.title())

    # Check for Bachelor's / B.Tech / BE / BCA / B.Sc
    if not detected_level:
        for alias in levels.get("bachelor", []):
            if re.search(r'\b' + re.escape(alias) + r'\b', jd_lower):
                detected_level = "bachelor"
                detected_degree_names.append(alias.upper() if len(alias) <= 4 else alias.title())

    # Check for "Any graduate" or "Any degree"
    if not detected_level and re.search(r'\b(any graduate|any degree|bachelor|degree)\b', jd_lower):
        detected_level = "bachelor"
        detected_degree_names.append("Bachelor's Degree")

    if not detected_level:
        return {
            "specified": False,
            "degree_level": None,
            "raw_text": "Education requirement not specified.",
            "degree_names": [],
            "fields": []
        }

    # Detect requested fields
    fields_data = data.get("fields", {})
    detected_fields = []
    for field_cat, aliases in fields_data.items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', jd_lower):
                detected_fields.append(field_cat)
                break

    return {
        "specified": True,
        "degree_level": detected_level,
        "degree_names": list(set(detected_degree_names)),
        "fields": detected_fields,
        "raw_text": f"{detected_level.title()}'s degree" + (f" in {', '.join(detected_fields)}" if detected_fields else "")
    }


def extract_resume_education(resume_text):
    """
    Extract candidate degree, level, field, institution, and year from resume text.
    """
    if not resume_text or not isinstance(resume_text, str):
        return {
            "degree_level": None,
            "degree": "Not specified",
            "field": "Not specified",
            "institution": "Not specified",
            "year": None
        }

    resume_lower = resume_text.lower()
    data = load_education_aliases()
    levels = data.get("degree_levels", {})

    detected_level = None
    detected_degree = "Not specified"

    # Search hierarchy (Doctorate -> Master -> Bachelor)
    for lvl in ["doctorate", "master", "bachelor"]:
        for alias in levels.get(lvl, []):
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, resume_lower):
                detected_level = lvl
                # Format neat display name
                if alias.lower() in ['b.tech', 'btech']:
                    detected_degree = "B.Tech"
                elif alias.lower() in ['b.e.', 'be']:
                    detected_degree = "B.E."
                elif alias.lower() in ['mba']:
                    detected_degree = "MBA"
                elif alias.lower() in ['m.tech', 'mtech']:
                    detected_degree = "M.Tech"
                elif alias.lower() in ['bca']:
                    detected_degree = "BCA"
                elif alias.lower() in ['mca']:
                    detected_degree = "MCA"
                elif alias.lower() in ['b.sc', 'bsc']:
                    detected_degree = "B.Sc"
                elif alias.lower() in ['m.sc', 'msc']:
                    detected_degree = "M.Sc"
                elif alias.lower() in ['phd', 'ph.d']:
                    detected_degree = "PhD"
                else:
                    detected_degree = alias.title()
                break
        if detected_level:
            break

    # Extract field
    detected_fields = []
    fields_data = data.get("fields", {})
    for field_cat, aliases in fields_data.items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', resume_lower):
                detected_fields.append(alias.title())
                break

    field_str = ", ".join(detected_fields) if detected_fields else "General Studies"

    # Extract graduation year (e.g. 2020 - 2024)
    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', resume_text)
    grad_year = int(year_match.group(1)) if year_match else None

    return {
        "degree_level": detected_level,
        "degree": detected_degree,
        "field": field_str,
        "institution": "University",
        "year": grad_year
    }


def calculate_education_match(jd_edu, resume_edu):
    """
    Compare JD education requirements against candidate's resume education.
    """
    if not jd_edu.get("specified", True) or not jd_edu.get("degree_level"):
        return {
            "required": "Education requirement not specified.",
            "candidate": f"{resume_edu.get('degree', 'Not specified')} ({resume_edu.get('field', '')})".strip(),
            "score": 100.0,
            "status": "Not specified"
        }

    required_level = jd_edu.get("degree_level")
    candidate_level = resume_edu.get("degree_level")

    req_val = LEVEL_HIERARCHY.get(required_level, 0)
    cand_val = LEVEL_HIERARCHY.get(candidate_level, 0) if candidate_level else 0

    req_text = jd_edu.get("raw_text") or f"{required_level.title()}'s degree"
    cand_text = f"{resume_edu.get('degree', 'No Degree')} in {resume_edu.get('field', 'General')}"

    if cand_val >= req_val and cand_val > 0:
        return {
            "required": req_text,
            "candidate": cand_text,
            "score": 100.0,
            "status": "Requirement Met"
        }
    elif cand_val > 0:
        # Partial match if candidate has degree but lower level than requested (e.g. Bachelor vs Master)
        return {
            "required": req_text,
            "candidate": cand_text,
            "score": 50.0,
            "status": "Education Gap"
        }
    else:
        return {
            "required": req_text,
            "candidate": "No recognized degree found",
            "score": 0.0,
            "status": "Requirement Not Met"
        }
