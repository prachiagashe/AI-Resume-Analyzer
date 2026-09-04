import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.experience_extractor import extract_jd_experience, extract_resume_experience, calculate_experience_match
from ai.education_extractor import extract_jd_education, extract_resume_education, calculate_education_match
from ai.job_title_matcher import calculate_job_title_match
from ai.ats_calculator import calculate_ats_score


def test_case_1():
    """TEST 1: Business Analyst 2+ yrs, Bachelor CS/IT vs Candidate 2.5 yrs BA, B.Tech CS"""
    jd = "Seeking a Business Analyst with 2+ years of experience. Education: Bachelor's degree in CS/IT."
    res = "Business Analyst at ABC Tech (Jan 2024 - Present). B.Tech in Computer Science."
    
    jd_exp = extract_jd_experience(jd)
    res_exp = extract_resume_experience(res, target_domain=jd_exp.get("domain"))
    exp_res = calculate_experience_match(jd_exp, res_exp)
    
    jd_edu = extract_jd_education(jd)
    res_edu = extract_resume_education(res)
    edu_res = calculate_education_match(jd_edu, res_edu)
    
    assert exp_res["score"] == 100.0, f"Expected Exp score 100.0, got {exp_res['score']}"
    assert edu_res["score"] == 100.0, f"Expected Edu score 100.0, got {edu_res['score']}"
    print("[PASS] TEST 1: Full match for Business Analyst (Exp 100%, Edu 100%)")


def test_case_2():
    """TEST 2: Business Analyst 2+ yrs vs Candidate 6 months BA"""
    jd = "Required: Minimum 2 years of experience in Business Analysis."
    res = "Junior Business Analyst Jan 2026 - Jun 2026 (6 months experience)."
    
    jd_exp = extract_jd_experience(jd)
    res_exp = extract_resume_experience(res, target_domain=jd_exp.get("domain"))
    exp_res = calculate_experience_match(jd_exp, res_exp)
    
    assert exp_res["score"] == 25.0, f"Expected Exp score 25.0, got {exp_res['score']}"
    assert exp_res["status"] == "Experience Gap", f"Expected 'Experience Gap', got {exp_res['status']}"
    print("[PASS] TEST 2: Candidate with 6 months vs 2+ yrs requirement correctly scored at 25% with Experience Gap status.")


def test_case_3():
    """TEST 3: MBA required vs Candidate B.Tech CS"""
    jd = "Requirement: MBA required."
    res = "Education: B.Tech in Computer Science from XYZ University."
    
    jd_edu = extract_jd_education(jd)
    res_edu = extract_resume_education(res)
    edu_res = calculate_education_match(jd_edu, res_edu)
    
    assert edu_res["score"] == 50.0 or edu_res["score"] == 0.0, f"Expected Edu score <= 50.0, got {edu_res['score']}"
    assert edu_res["status"] in ["Requirement Not Met", "Education Gap"], f"Got status: {edu_res['status']}"
    print("[PASS] TEST 3: MBA required vs B.Tech candidate correctly fails mandatory degree level check.")


def test_case_4():
    """TEST 4: Bachelor's in CS/IT vs Candidate B.Tech IT"""
    jd = "Requires a Bachelor's degree in CS/IT or related field."
    res = "Degree: B.Tech Information Technology, 2024."
    
    jd_edu = extract_jd_education(jd)
    res_edu = extract_resume_education(res)
    edu_res = calculate_education_match(jd_edu, res_edu)
    
    assert edu_res["score"] == 100.0, f"Expected Edu score 100.0, got {edu_res['score']}"
    assert edu_res["status"] == "Requirement Met"
    print("[PASS] TEST 4: Bachelor in CS/IT vs B.Tech IT correctly matched via related fields.")


def test_case_5():
    """TEST 5: Freshers welcome vs Candidate 0 years"""
    jd = "Entry-level position. Freshers welcome to apply."
    res = "Recent graduate looking for entry software role."
    
    jd_exp = extract_jd_experience(jd)
    res_exp = extract_resume_experience(res)
    exp_res = calculate_experience_match(jd_exp, res_exp)
    
    assert exp_res["score"] == 100.0
    assert exp_res["status"] == "Eligible"
    print("[PASS] TEST 5: Freshers welcome vs 0 yrs candidate scored 100% Eligible.")


def test_case_6():
    """TEST 6: JD has no education requirement"""
    jd = "Looking for a Python Developer with Flask and SQL experience."
    res = "Python Developer with Flask and SQL skills."
    
    jd_edu = extract_jd_education(jd)
    res_edu = extract_resume_education(res)
    edu_res = calculate_education_match(jd_edu, res_edu)
    
    assert edu_res["score"] == 100.0
    assert edu_res["status"] == "Not specified"
    print("[PASS] TEST 6: Unspecified education requirement defaults to 100% Not specified.")


def test_case_7():
    """TEST 7: JD has no experience requirement"""
    jd = "Seeking a Frontend Developer with React and CSS skills."
    res = "Frontend Developer skilled in React and CSS."
    
    jd_exp = extract_jd_experience(jd)
    res_exp = extract_resume_experience(res)
    exp_res = calculate_experience_match(jd_exp, res_exp)
    
    assert exp_res["score"] == 100.0
    assert exp_res["status"] == "Not specified"
    print("[PASS] TEST 7: Unspecified experience requirement defaults to 100% Not specified.")


if __name__ == "__main__":
    print("--- Running Comprehensive Analyzer Unit Test Suite ---")
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
    test_case_7()
    print("--- ALL 7 TEST CASES PASSED SUCCESSFULLY! ---")
