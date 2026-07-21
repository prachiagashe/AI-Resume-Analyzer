import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Update the host, user, password, and database name with your actual credentials.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',  
            database='ai_resume_analyzer' # Add your target database name here
        )
        
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def close_db_connection(connection):
    """
    Closes the provided database connection.
    """
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed")

# Example usage/testing:
if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        close_db_connection(conn)
