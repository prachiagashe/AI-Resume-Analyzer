import os
import json
import re

# Base paths for dynamic JSON files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SKILLS_PATH = os.path.join(BASE_DIR, 'data', 'skills.json')
DEFAULT_ALIASES_PATH = os.path.join(BASE_DIR, 'data', 'skill_aliases.json')

_skills_cache = None
_aliases_cache = None
_norm_map_cache = None
_search_patterns_cache = None


def load_skills(file_path=None):
    """
    Load skills dynamically from skills.json.
    """
    if file_path is None:
        file_path = DEFAULT_SKILLS_PATH
        
    if not os.path.exists(file_path):
        return {}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_aliases(file_path=None):
    """
    Load skill aliases dynamically from skill_aliases.json.
    """
    if file_path is None:
        file_path = DEFAULT_ALIASES_PATH
        
    if not os.path.exists(file_path):
        return {}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _init_caches():
    """
    Build cached lookup tables and compiled regex patterns for ultra-fast matching.
    """
    global _skills_cache, _aliases_cache, _norm_map_cache, _search_patterns_cache
    
    skills_data = load_skills()
    aliases_data = load_aliases()
    
    # Map lowercase lookup term -> Standardized display name
    norm_map = {}
    
    # 1. Register all canonical skills from skills.json
    for category, skill_list in skills_data.items():
        for skill in skill_list:
            norm_map[skill.strip().lower()] = skill.strip()
            
    # 2. Register aliases from skill_aliases.json
    for canonical_key, alias_list in aliases_data.items():
        canonical_key_lower = canonical_key.strip().lower()
        standard_name = norm_map.get(canonical_key_lower, canonical_key.title())
        
        for alias in alias_list:
            alias_lower = alias.strip().lower()
            norm_map[alias_lower] = standard_name

    # 3. Create search terms sorted by length descending (longer terms matched first)
    search_terms = sorted(norm_map.keys(), key=lambda x: len(x), reverse=True)
    
    compiled_patterns = []
    for term in search_terms:
        # Prefix boundary
        if term.startswith('.'):
            prefix = r'(?<![a-zA-Z0-9_\-#+])'
        elif term in ['js', 'ts', 'c']:
            prefix = r'(?<![a-zA-Z0-9_.\-#+])'
        else:
            prefix = r'(?<![a-zA-Z0-9_\-#+])'
            
        # Suffix boundary
        if term.endswith('+') or term.endswith('#'):
            suffix = r'(?![a-zA-Z0-9_])'
        else:
            suffix = r'(?![a-zA-Z0-9_\-#+])'
            
        pattern_str = prefix + re.escape(term) + suffix
        pattern = re.compile(pattern_str, re.IGNORECASE)
        compiled_patterns.append((term, pattern, norm_map[term]))

    _skills_cache = skills_data
    _aliases_cache = aliases_data
    _norm_map_cache = norm_map
    _search_patterns_cache = compiled_patterns


def normalize_skill(skill):
    """
    Normalize an extracted skill or alias string to its standard display name.
    Examples:
    - "ReactJS", "react.js" -> "React"
    - "NodeJS", "Node JS" -> "Node.js"
    - "JS" -> "JavaScript"
    - "ML" -> "Machine Learning"
    """
    if not skill or not isinstance(skill, str):
        return ""
        
    if _norm_map_cache is None:
        _init_caches()
        
    skill_lower = skill.strip().lower()
    return _norm_map_cache.get(skill_lower, skill.strip())


def extract_skills(text):
    """
    Scan input text (resume or JD), detect all matching skills and aliases,
    normalize them to standard names, and return unique sorted list.
    
    Args:
        text (str): Resume or Job Description text.
        
    Returns:
        list: Sorted list of unique standardized skill names.
    """
    if not text or not isinstance(text, str):
        return []
        
    if _search_patterns_cache is None:
        _init_caches()
        
    found_skills = set()
    
    for term, pattern, standard_name in _search_patterns_cache:
        if pattern.search(text):
            found_skills.add(standard_name)
            
    return sorted(list(found_skills))
