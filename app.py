import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from database.db import get_db_connection, close_db_connection

# Import AI modules
from ai.pdf_reader import extract_text
from ai.text_preprocessor import preprocess_text
from ai.skill_extractor import extract_skills
from ai.experience_extractor import extract_jd_experience, extract_resume_experience, calculate_experience_match
from ai.education_extractor import extract_jd_education, extract_resume_education, calculate_education_match
from ai.job_title_matcher import calculate_job_title_match
from ai.ats_calculator import calculate_ats_score
from ai.recommendation_engine import generate_recommendations

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Required for flash messages
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if the post request has the file part
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))
        
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
        
    job_title = request.form.get('jobTitle', '')
    job_description = request.form.get('jobDescription', '')
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
        file.save(file_path)
        
        # 1. Extract raw text using PDF reader
        raw_resume_text = extract_text(file_path)
        
        # 2. Clean texts using preprocessor
        clean_resume = preprocess_text(raw_resume_text)
        clean_jd = preprocess_text(job_description)
        
        # 3. Extract skills using scalable JSON taxonomy & alias matching engine
        resume_skills = extract_skills(raw_resume_text)
        job_skills = extract_skills(job_description)
        
        matched_skills = sorted([skill for skill in job_skills if skill in resume_skills])
        missing_skills = sorted([skill for skill in job_skills if skill not in resume_skills])
        
        total_required_skills = len(job_skills)
        total_matched_skills = len(matched_skills)
        
        # 4. Extract & calculate Experience match
        jd_exp = extract_jd_experience(job_description)
        resume_exp = extract_resume_experience(raw_resume_text, target_domain=jd_exp.get("domain"))
        exp_match = calculate_experience_match(jd_exp, resume_exp)
        experience_score = exp_match["score"]

        # 5. Extract & calculate Education match
        jd_edu = extract_jd_education(job_description)
        resume_edu = extract_resume_education(raw_resume_text)
        edu_match = calculate_education_match(jd_edu, resume_edu)
        education_score = edu_match["score"]

        # 6. Calculate Job Title / Role match
        title_match = calculate_job_title_match(job_title, raw_resume_text)
        title_score = title_match["score"]
            
        # 7. Calculate Multi-Component Weighted ATS Score
        ats_data = calculate_ats_score(
            clean_resume, clean_jd,
            resume_skills=resume_skills,
            job_skills=job_skills,
            exp_score=experience_score,
            edu_score=education_score,
            title_score=title_score
        )
        ats_score = ats_data['score']
        similarity_score = round(ats_data['similarity'], 2)
        skill_match_percentage = ats_data['skill_match_percentage']

        # 8. Identify Critical Warnings
        critical_warnings = []
        if exp_match["status"] == "Experience Gap" and exp_match.get("gap_years", 0) >= 1.0:
            critical_warnings.append(f"Minimum experience requirement not satisfied ({exp_match['relevant_years']} yrs vs {exp_match['required_years']}+ yrs required).")
        if edu_match["status"] == "Requirement Not Met":
            critical_warnings.append(f"Mandatory education requirement not satisfied (Required: {edu_match['required']}).")

        # Structured backend data payload
        analysis_data = {
            "ats_score": ats_score,
            "skills": {
                "score": skill_match_percentage,
                "required": total_required_skills,
                "matched": total_matched_skills,
                "missing": len(missing_skills)
            },
            "experience": exp_match,
            "education": edu_match,
            "job_title": title_match,
            "semantic": {
                "score": ats_data['semantic_score']
            },
            "critical_warnings": critical_warnings,
            "match_status": ats_data['match_status']
        }
        
        # 9. Generate Recommendations
        recommendations = generate_recommendations(missing_skills)
            
        # 10. Save into MySQL Database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Fetch existing user or create default user record
                cursor.execute("SELECT id FROM users LIMIT 1")
                user_row = cursor.fetchone()
                if user_row:
                    user_id = user_row[0]
                else:
                    cursor.execute(
                        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                        ("Prachi Agashe", "prachi@example.com", "pass123")
                    )
                    user_id = cursor.lastrowid
                
                # Insert into resumes table
                insert_resume_query = """
                    INSERT INTO resumes (file_name, file_path)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_resume_query, (filename, file_path))
                resume_id = cursor.lastrowid
                
                # Insert into analysis table
                try:
                    insert_analysis_query = """
                        INSERT INTO analysis 
                        (user_id, resume_id, job_title, ats_score, skill_match_score, 
                         experience_score, education_score, job_title_score, semantic_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_analysis_query, (
                        user_id, resume_id, job_title, float(ats_score),
                        float(skill_match_percentage), float(experience_score),
                        float(education_score), float(title_score), float(ats_data['semantic_score'])
                    ))
                except Exception as table_err:
                    # Fallback if ALTER TABLE has not been run yet
                    matched_str = ", ".join(matched_skills) if matched_skills else "None"
                    missing_str = ", ".join(missing_skills) if missing_skills else "None"
                    insert_legacy_query = """
                        INSERT INTO analysis 
                        (resume_id, ats_score, matched_skills, missing_skills, job_title)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_legacy_query, (resume_id, ats_score, matched_str, missing_str, job_title))
                
                conn.commit()
                print(f"Successfully saved analysis for user_id {user_id}, resume_id {resume_id}")
                flash(f'Resume successfully uploaded and analyzed! ID: {resume_id}', 'success')
                
            except Exception as e:
                print(f"Database error: {e}")
                conn.rollback()
                flash('An error occurred while saving to the database.', 'danger')
            finally:
                cursor.close()
                close_db_connection(conn)
        else:
            flash('Could not connect to the database.', 'danger')
            print("Could not connect to database to save results.")

        # 11. Render result page with all dynamic data
        return render_template('result.html',
                               ats_score=ats_score,
                               similarity_score=similarity_score,
                               matched_skills=matched_skills,
                               missing_skills=missing_skills,
                               recommendations=recommendations,
                               resume_skills=resume_skills,
                               job_skills=job_skills,
                               total_required_skills=total_required_skills,
                               total_matched_skills=total_matched_skills,
                               skill_match_percentage=skill_match_percentage,
                               analysis_data=analysis_data,
                               exp_match=exp_match,
                               edu_match=edu_match,
                               title_match=title_match,
                               critical_warnings=critical_warnings)
                               
    return "Invalid file format. Please upload a PDF.", 400

if __name__ == '__main__':
    app.run(debug=True)