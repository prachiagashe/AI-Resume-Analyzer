import re
from datetime import datetime

MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
    'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}


def _format_years(val):
    """
    Format numeric year values cleanly without trailing '.0' (e.g. 3.0 -> '3', 2.5 -> '2.5').
    """
    if val is None:
        return "0"
    val_float = float(val)
    if val_float == int(val_float):
        return str(int(val_float))
    return f"{val_float:.1f}"


def extract_jd_experience(jd_text):
    """
    Extract minimum/maximum required experience years and domain from Job Description text.
    """
    if not jd_text or not isinstance(jd_text, str):
        return {
            "min_years": 0,
            "max_years": None,
            "domain": None,
            "raw_text": "Experience requirement not specified.",
            "specified": False
        }
        
    jd_lower = jd_text.lower()
    
    # 1. Check for fresher / entry-level keywords
    if re.search(r'\b(fresher|freshers|entry[-\s]?level|no experience required)\b', jd_lower):
        return {
            "min_years": 0,
            "max_years": 1,
            "domain": None,
            "raw_text": "Freshers are welcome",
            "specified": True,
            "fresher_friendly": True
        }
        
    # 2. Check for range patterns: "1-3 years", "1 to 3 years", "0-2 years"
    range_match = re.search(r'(\d+)\s*(?:-|to|\s+to\s+)\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)', jd_lower)
    if range_match:
        min_y = float(range_match.group(1))
        max_y = float(range_match.group(2))
        return {
            "min_years": min_y,
            "max_years": max_y,
            "domain": _extract_domain_context(jd_text, range_match.start()),
            "raw_text": f"{_format_years(min_y)}-{_format_years(max_y)} years",
            "specified": True
        }
        
    # 3. Check for plus/minimum patterns: "2+ years", "minimum 3 years", "at least 2 yrs"
    plus_match = re.search(r'(?:minimum|at least|min\.?)?\s*(\d+)(?:\+|\s*\+\s*years?|\s*years?|\s*yrs?)\s*(?:of)?\s*(?:experience)?', jd_lower)
    if plus_match:
        min_y = float(plus_match.group(1))
        return {
            "min_years": min_y,
            "max_years": None,
            "domain": _extract_domain_context(jd_text, plus_match.start()),
            "raw_text": f"{_format_years(min_y)}+ years",
            "specified": True
        }

    # Default if no experience pattern detected
    return {
        "min_years": 0,
        "max_years": None,
        "domain": None,
        "raw_text": "Experience requirement not specified.",
        "specified": False
    }


def _extract_domain_context(text, pos):
    """
    Extract domain phrase around experience requirement position.
    """
    snippet = text[max(0, pos - 30):min(len(text), pos + 60)]
    for term in ["business analyst", "php", "python", "software developer", "data scientist", "frontend", "backend", "full stack"]:
        if term in snippet.lower():
            return term.title()
    return None


def _extract_experience_section_text(resume_text):
    """
    Isolate text from Work Experience section to avoid counting pure Education dates.
    """
    lines = resume_text.split('\n')
    in_exp_section = False
    exp_lines = []
    
    exp_headers = re.compile(r'\b(work experience|professional experience|employment history|career history|work history|experience)\b', re.IGNORECASE)
    other_headers = re.compile(r'\b(education|academic|qualifications|certifications|projects|skills|summary|profile|awards)\b', re.IGNORECASE)
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if exp_headers.search(stripped) and len(stripped) < 40:
            in_exp_section = True
            continue
        elif in_exp_section and other_headers.search(stripped) and len(stripped) < 40:
            in_exp_section = False
            
        if in_exp_section:
            exp_lines.append(stripped)
            
    if exp_lines:
        return "\n".join(exp_lines)
        
    # Fallback: Return original text if no section headers detected
    return resume_text


def extract_resume_experience(resume_text, target_domain=None):
    """
    Extract total work experience and domain-relevant experience from resume text.
    Handles date ranges, present/current jobs, and merges overlapping intervals.
    """
    if not resume_text or not isinstance(resume_text, str):
        return {"total_years": 0.0, "relevant_years": 0.0, "roles": []}

    exp_text = _extract_experience_section_text(resume_text)

    current_year = datetime.now().year
    current_month = datetime.now().month

    # 1. Look for explicit statements in experience section
    explicit_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)', exp_text, re.IGNORECASE)
    explicit_years = [float(y) for y in explicit_match]
    
    explicit_months_match = re.findall(r'(\d+)\s*(?:months?|mos?)\s*(?:of)?\s*(?:experience|exp)', exp_text, re.IGNORECASE)
    if explicit_months_match:
        for m_val in explicit_months_match:
            explicit_years.append(float(m_val) / 12.0)

    # 2. Extract date intervals: Month Year - Month Year/Present
    date_intervals = []
    
    pattern = re.compile(
        r'(?P<start_m>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)?\s*'
        r'(?P<start_y>20\d{2}|19\d{2})\s*(?:-|–|to)\s*'
        r'(?P<end_m>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)?\s*'
        r'(?P<end_y>present|current|now|20\d{2}|19\d{2})',
        re.IGNORECASE
    )

    for m in pattern.finditer(exp_text):
        start_y = int(m.group('start_y'))
        start_m_str = (m.group('start_m') or '').lower()
        start_m = MONTH_MAP.get(start_m_str, 1)

        end_y_str = m.group('end_y').lower()
        if end_y_str in ['present', 'current', 'now']:
            end_y = current_year
            end_m = current_month
        else:
            end_y = int(end_y_str)
            end_m_str = (m.group('end_m') or '').lower()
            end_m = MONTH_MAP.get(end_m_str, 12)

        start_total = start_y * 12 + start_m
        end_total = end_y * 12 + end_m + 1

        if end_total > start_total:
            date_intervals.append((start_total, end_total))

    # Also check single year ranges e.g. "2022 - 2024"
    if not date_intervals:
        year_range_pattern = re.compile(r'\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|19\d{2}|present|current)\b', re.IGNORECASE)
        for m in year_range_pattern.finditer(exp_text):
            sy = int(m.group(1))
            ey_str = m.group(2).lower()
            ey = current_year if ey_str in ['present', 'current'] else int(ey_str)
            if ey >= sy:
                date_intervals.append((sy * 12 + 1, (ey + 1) * 12))

    # Merge overlapping intervals to prevent double-counting
    total_months = _merge_and_sum_months(date_intervals)
    calculated_years = total_months / 12.0

    if calculated_years == 0 and explicit_years:
        calculated_years = max(explicit_years)

    relevant_years = calculated_years
    if target_domain and isinstance(target_domain, str):
        domain_lower = target_domain.lower()
        if domain_lower not in exp_text.lower() and calculated_years > 0:
            relevant_years = max(0.5, round(calculated_years * 0.5, 1))

    return {
        "total_years": round(calculated_years, 1),
        "relevant_years": round(relevant_years, 1),
        "intervals_count": len(date_intervals)
    }


def _merge_and_sum_months(intervals):
    """
    Merge overlapping month intervals and return total unique months.
    """
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        if current[0] <= prev_end:
            merged[-1] = (prev_start, max(prev_end, current[1]))
        else:
            merged.append(current)
            
    return sum(end - start for start, end in merged)


def calculate_experience_match(jd_exp, resume_exp):
    """
    Compare JD experience requirement against candidate resume experience.
    Returns score (0-100) and formatted strings.
    """
    if not jd_exp.get("specified", True) or jd_exp.get("raw_text") == "Experience requirement not specified.":
        req_y = 0
        cand_y = resume_exp.get("total_years", 0.0)
        rel_y = resume_exp.get("relevant_years", 0.0)
        return {
            "required_years": req_y,
            "required_years_str": "0",
            "candidate_years": cand_y,
            "candidate_years_str": _format_years(cand_y),
            "relevant_years": rel_y,
            "relevant_years_str": _format_years(rel_y),
            "score": 100.0,
            "score_str": "100",
            "status": "Not specified",
            "gap_years": 0.0,
            "gap_years_str": "0"
        }

    min_required = jd_exp.get("min_years", 0)
    relevant_years = resume_exp.get("relevant_years", 0.0)
    candidate_years = resume_exp.get("total_years", 0.0)

    if jd_exp.get("fresher_friendly") or min_required == 0:
        return {
            "required_years": 0,
            "required_years_str": "0",
            "candidate_years": candidate_years,
            "candidate_years_str": _format_years(candidate_years),
            "relevant_years": relevant_years,
            "relevant_years_str": _format_years(relevant_years),
            "score": 100.0,
            "score_str": "100",
            "status": "Eligible",
            "gap_years": 0.0,
            "gap_years_str": "0"
        }

    if relevant_years >= min_required:
        score = 100.0
        status = "Requirement Met"
        gap = 0.0
    else:
        score = round(min((relevant_years / min_required) * 100, 100.0), 1)
        gap = round(min_required - relevant_years, 1)
        status = "Experience Gap"

    return {
        "required_years": min_required,
        "required_years_str": _format_years(min_required),
        "candidate_years": candidate_years,
        "candidate_years_str": _format_years(candidate_years),
        "relevant_years": relevant_years,
        "relevant_years_str": _format_years(relevant_years),
        "score": score,
        "score_str": _format_years(score),
        "status": status,
        "gap_years": gap,
        "gap_years_str": _format_years(gap)
    }
