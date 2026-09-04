-- ========================================================
-- AI Resume Analyzer - Database Schema Script v3.0
-- Database Name: ai_resume_analyzer
-- Target Environment: MySQL Workbench
-- ========================================================

CREATE DATABASE IF NOT EXISTS ai_resume_analyzer;
USE ai_resume_analyzer;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) DEFAULT 'pass123',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Analysis Table
CREATE TABLE IF NOT EXISTS analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_id INT NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    ats_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    skill_match_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    experience_score DECIMAL(5, 2) NOT NULL DEFAULT 100.00,
    required_experience_years DECIMAL(4, 1) DEFAULT 0.0,
    candidate_experience_years DECIMAL(4, 1) DEFAULT 0.0,
    relevant_experience_years DECIMAL(4, 1) DEFAULT 0.0,
    experience_status VARCHAR(100) DEFAULT 'Not specified',
    education_score DECIMAL(5, 2) NOT NULL DEFAULT 100.00,
    required_education VARCHAR(255) DEFAULT 'Not specified',
    candidate_education VARCHAR(255) DEFAULT 'Not specified',
    education_status VARCHAR(100) DEFAULT 'Not specified',
    job_title_score DECIMAL(5, 2) NOT NULL DEFAULT 90.00,
    target_job_title VARCHAR(255) DEFAULT 'Not specified',
    candidate_job_title VARCHAR(255) DEFAULT 'Candidate Role',
    semantic_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

-- Insert Default User Record
INSERT INTO users (id, name, email, password)
VALUES (1, 'Prachi Agashe', 'prachi@example.com', 'pass123')
ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email);

-- ========================================================
-- ALTER TABLE Queries (Use if 'analysis' table already exists)
-- ========================================================
/*
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS user_id INT AFTER id;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS skill_match_score DECIMAL(5,2) DEFAULT 0.00 AFTER ats_score;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS experience_score DECIMAL(5,2) DEFAULT 100.00 AFTER skill_match_score;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS required_experience_years DECIMAL(4,1) DEFAULT 0.0 AFTER experience_score;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS candidate_experience_years DECIMAL(4,1) DEFAULT 0.0 AFTER required_experience_years;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS relevant_experience_years DECIMAL(4,1) DEFAULT 0.0 AFTER candidate_experience_years;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS experience_status VARCHAR(100) DEFAULT 'Not specified' AFTER relevant_experience_years;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS education_score DECIMAL(5,2) DEFAULT 100.00 AFTER experience_status;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS required_education VARCHAR(255) DEFAULT 'Not specified' AFTER education_score;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS candidate_education VARCHAR(255) DEFAULT 'Not specified' AFTER required_education;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS education_status VARCHAR(100) DEFAULT 'Not specified' AFTER candidate_education;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS job_title_score DECIMAL(5,2) DEFAULT 90.00 AFTER education_status;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS target_job_title VARCHAR(255) DEFAULT 'Not specified' AFTER job_title_score;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS candidate_job_title VARCHAR(255) DEFAULT 'Candidate Role' AFTER target_job_title;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS semantic_score DECIMAL(5,2) DEFAULT 0.00 AFTER candidate_job_title;
*/

-- Verification Queries
SELECT * FROM users;
SELECT * FROM resumes;
SELECT * FROM analysis;
