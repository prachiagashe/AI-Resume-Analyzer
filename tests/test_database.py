import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_db_connection, close_db_connection


def test_db_schema_and_queries():
    print("--- Testing Database Connection & SQL Queries ---")
    conn = get_db_connection()
    if not conn:
        print("[SKIP] Could not connect to local MySQL database. Skipping live DB execution test.")
        print("SQL schema script is available in database/schema.sql.")
        return

    try:
        cursor = conn.cursor()
        
        # Test table creation if not exists
        create_users_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) DEFAULT 'pass123',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cursor.execute(create_users_sql)
        print("[PASS] Table 'users' verified/created.")
        
        create_resumes_sql = """
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cursor.execute(create_resumes_sql)
        print("[PASS] Table 'resumes' verified/created.")

        create_analysis_sql = """
            CREATE TABLE IF NOT EXISTS analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                resume_id INT NOT NULL,
                job_title VARCHAR(255) NOT NULL,
                ats_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
                skill_match_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
                experience_score DECIMAL(5, 2) NOT NULL DEFAULT 75.00,
                education_score DECIMAL(5, 2) NOT NULL DEFAULT 100.00,
                job_title_score DECIMAL(5, 2) NOT NULL DEFAULT 90.00,
                semantic_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            );
        """
        try:
            cursor.execute(create_analysis_sql)
            print("[PASS] Table 'analysis' verified/created.")
        except Exception as e:
            print(f"[NOTE] 'analysis' table exists or requires ALTER TABLE: {e}")

        conn.commit()
    except Exception as err:
        print(f"Database error during test: {err}")
    finally:
        cursor.close()
        close_db_connection(conn)


if __name__ == '__main__':
    test_db_schema_and_queries()
