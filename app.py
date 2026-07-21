import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from database.db import get_db_connection, close_db_connection

# Import the new AI modules
from ai.pdf_reader import extract_text
from ai.text_preprocessor import preprocess_text
from ai.skill_extractor import extract_skills
from ai.ats_calculator import calculate_ats_score
from ai.recommendation_engine import generate_recommendations

app = Flask(__name__)
app.secret_key = 'super_secret_key' # Required for flash messages
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
        
        # 1. Extract text using AI pdf reader
        raw_resume_text = extract_text(file_path)
        
        # 2. Clean texts using NLTK preprocessor
        clean_resume = preprocess_text(raw_resume_text)
        clean_jd = preprocess_text(job_description)
        
        # 3. Extract skills using spaCy
        resume_skills = extract_skills(clean_resume)
        job_skills = extract_skills(clean_jd)
        
        # 4. Calculate ATS Score using Scikit-Learn TF-IDF Cosine Similarity
        ats_data = calculate_ats_score(clean_resume, clean_jd)
        ats_score = ats_data['score']
        similarity_score = round(ats_data['similarity'], 2)
        
        # 5. Identify missing skills
        matched_skills = [skill for skill in job_skills if skill in resume_skills]
        missing_skills = [skill for skill in job_skills if skill not in resume_skills]
        
        # 6. Generate Recommendations
        recommendations = generate_recommendations(missing_skills)
            
        # 7. Save into MySQL Database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Insert into resumes table
                insert_resume_query = """
                    INSERT INTO resumes (file_name, file_path)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_resume_query, (filename, file_path))
                resume_id = cursor.lastrowid
                
                # Insert into analysis table
                matched_str = ", ".join(matched_skills) if matched_skills else "None"
                missing_str = ", ".join(missing_skills) if missing_skills else "None"
                
                insert_analysis_query = """
                    INSERT INTO analysis 
                    (resume_id, ats_score, matched_skills, missing_skills, job_title)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_analysis_query, (resume_id, ats_score, matched_str, missing_str, job_title))
                
                # Commit the transaction
                conn.commit()
                print(f"Successfully saved analysis for resume_id {resume_id}")
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

        # 8. Render result page with all dynamic data
        return render_template('result.html',
                               ats_score=ats_score,
                               similarity_score=similarity_score,
                               matched_skills=matched_skills,
                               missing_skills=missing_skills,
                               recommendations=recommendations,
                               resume_skills=resume_skills,
                               job_skills=job_skills)
                               
    return "Invalid file format. Please upload a PDF.", 400

if __name__ == '__main__':
    app.run(debug=True)