import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.skill_extractor import load_skills, load_aliases, normalize_skill, extract_skills
from ai.ats_calculator import calculate_ats_score


def test_load_data():
    skills = load_skills()
    aliases = load_aliases()
    
    assert isinstance(skills, dict), "load_skills() should return a dict"
    assert isinstance(aliases, dict), "load_aliases() should return a dict"
    assert "Programming" in skills, "skills.json should contain 'Programming' category"
    assert "react" in aliases, "skill_aliases.json should contain 'react' alias"
    print("[PASS] load_skills() & load_aliases() verified.")


def test_normalize_skill():
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("NodeJS") == "Node.js"
    assert normalize_skill("Node JS") == "Node.js"
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("ml") == "Machine Learning"
    assert normalize_skill("powerbi") == "Power BI"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("sklearn") == "Scikit-Learn"
    assert normalize_skill("Python") == "Python"
    print("[PASS] normalize_skill() verified.")


def test_user_example_extraction():
    input_text = "I have experience in ReactJS, NodeJS, JS, MongoDB and AWS."
    extracted = extract_skills(input_text)
    expected = ["AWS", "JavaScript", "MongoDB", "Node.js", "React"]
    
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    print(f"[PASS] extract_skills('{input_text}') -> {extracted}")


def test_special_character_skills():
    input_text = "Proficient in C++, C#, .NET, Express.js, Vue.js, and Docker."
    extracted = extract_skills(input_text)
    
    expected_skills = [".NET", "C#", "C++", "Docker", "Express.js", "Vue.js"]
    assert extracted == expected_skills, f"Expected {expected_skills}, but got {extracted}"
    print(f"[PASS] extract_skills special characters -> {extracted}")


def test_ats_matching_calculation():
    resume_text = "Full Stack Engineer with ReactJS, NodeJS, Python, SQL and AWS experience."
    jd_text = "Looking for Senior Developer with Python, React, Node.js, AWS, and Docker skills."
    
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(jd_text)
    
    matched_skills = sorted([s for s in job_skills if s in resume_skills])
    missing_skills = sorted([s for s in job_skills if s not in resume_skills])
    
    # job_skills: ['AWS', 'Docker', 'Node.js', 'Python', 'React'] (5 skills)
    # resume_skills: ['AWS', 'Node.js', 'Python', 'React', 'SQL']
    # matched: ['AWS', 'Node.js', 'Python', 'React'] (4 skills)
    # missing: ['Docker'] (1 skill)
    
    skill_match_percentage = round((len(matched_skills) / len(job_skills)) * 100, 2)
    assert len(job_skills) == 5, f"Expected 5 JD skills, got {len(job_skills)}"
    assert matched_skills == ["AWS", "Node.js", "Python", "React"], f"Got {matched_skills}"
    assert missing_skills == ["Docker"], f"Got {missing_skills}"
    assert skill_match_percentage == 80.0, f"Expected 80.0%, got {skill_match_percentage}%"
    
    ats_res = calculate_ats_score("clean resume", "clean jd", resume_skills, job_skills)
    assert ats_res["score"] == 80, f"Expected ATS score 80, got {ats_res['score']}"
    assert ats_res["skill_match_percentage"] == 80.0
    print("[PASS] ATS skill match calculation formula verified.")


if __name__ == "__main__":
    print("--- Running Skill Extractor Unit Tests ---")
    test_load_data()
    test_normalize_skill()
    test_user_example_extraction()
    test_special_character_skills()
    test_ats_matching_calculation()
    print("--- ALL UNIT TESTS PASSED SUCCESSFULLY! ---")
