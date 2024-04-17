import sqlite3
from faker import Faker
import random

fake = Faker()

# Connect to the database
conn = sqlite3.connect('university.db')
c = conn.cursor()

# Function to create tables if they don't exist
def create_tables():
    try:
         # Drop the existing subjects table if it exists
        c.execute('''DROP TABLE IF EXISTS subjects''')
        
        # Table with students
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        group_id INTEGER
                     )''')

        # Table with groups
        c.execute('''CREATE TABLE IF NOT EXISTS groups (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                     )''')

        # Table with lecturers
        c.execute('''CREATE TABLE IF NOT EXISTS lecturers (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                     )''')

        # Table with subjects
        c.execute('''CREATE TABLE IF NOT EXISTS subjects (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        lecturer_id INTEGER,
                        FOREIGN KEY (lecturer_id) REFERENCES lecturers(id)
                     )''')

        # Table with grades
        c.execute('''CREATE TABLE IF NOT EXISTS grades (
                        id INTEGER PRIMARY KEY,
                        student_id INTEGER,
                        subject_id INTEGER,
                        grade INTEGER,
                        date TEXT,
                        FOREIGN KEY (student_id) REFERENCES students(id),
                        FOREIGN KEY (subject_id) REFERENCES subjects(id)
                     )''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()

# Function to fill tables with random data
def fill_tables():
    try:
        # Fill students table
        for _ in range(30):
            c.execute("INSERT INTO students (name, group_id) VALUES (?, ?)", (fake.name(), random.randint(1, 3)))

        # Fill groups table
        for group_id in range(1, 4):
            c.execute("INSERT INTO groups (name) VALUES (?)", (f'Group {group_id}',))

        # Fill lecturers table
        for _ in range(3):
            c.execute("INSERT INTO lecturers (name) VALUES (?)", (fake.name(),))

        # Fill subjects table
        for lecturer_id in range(1, 4):
            for _ in range(random.randint(5, 8)):
                c.execute("INSERT INTO subjects (name, lecturer_id) VALUES (?, ?)", (fake.word(), lecturer_id))

        # Fill grades table
        for student_id in range(1, 31):
            for subject_id in range(1, random.randint(5, 9)):
                c.execute("INSERT INTO grades (student_id, subject_id, grade, date) VALUES (?, ?, ?, ?)",
                          (student_id, subject_id, random.randint(2, 5), fake.date()))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error filling tables with data: {e}")
        conn.rollback()

# Function to close the connection
def close_connection():
    conn.close()

# Main function to create tables, fill them with data, and close the connection
def main():
    create_tables()
    fill_tables()
    save_queries()
    close_connection()

# Function to save SQL queries to files
def save_queries():
    queries = [
        # SQL queries
        """
        -- 5 students with the highest average grades across all subjects
        SELECT s.name, AVG(g.grade) AS avg_grade
        FROM students s
        JOIN grades g ON s.id = g.student_id
        GROUP BY s.id
        ORDER BY avg_grade DESC
        LIMIT 5;
        """,
        # Student with the highest average grade in a selected subject
        """
        -- Student with the highest average grade in a selected subject
        SELECT gr.name, AVG(g.grade) AS avg_grade
        FROM groups gr
        JOIN students s ON gr.id = s.group_id
        JOIN grades g ON s.id = g.student_id
        WHERE g.subject_id = ?
        GROUP BY s.id
        LIMIT 1;
        """,
        # Average grades in group for a selected subject
        """
        -- Average grades in group for a selected subject
        SELECT gr.name, AVG(g.grade) AS avg_grade
        FROM groups gr
        JOIN students s ON gr.id = s.group_id
        JOIN grades g ON s.id = g.student_id
        WHERE g.subject_id = ?
        GROUP BY gr.id;
        """,
        # Average grades for all groups, considering all grades
        """
        -- Average grades for all groups, considering all grades
        SELECT AVG(g.grade) AS avg_grade
        FROM grades g;
        """,
        # Subject taught by a selected lecturer
        """
        -- Subject taught by a selected lecturer
        SELECT s.name
        FROM subjects s
        JOIN lecturers l ON s.lecturer_id = l.id
        WHERE l.id = ?;
        """,
        # List of students in a selected group
        """
        -- List of students in a selected group
        SELECT s.name
        FROM students s
        JOIN groups gr ON s.group_id = gr.id
        WHERE gr.id = ?;
        """,
        # Grades of students in a selected group for a specific subject
        """
        -- Grades of students in a selected group for a specific subject
        SELECT s.name, g.grade
        FROM students s
        JOIN grades g ON s.id = g.student_id
        WHERE s.group_id = ? AND g.subject_id = ?;
        """,
        # Average grades given by lecturer for a specific subject
        """
        -- Average grades given by lecturer for a specific subject
        SELECT AVG(g.grade) AS avg_grade
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        WHERE s.lecturer_id = ? AND g.subject_id = ?;
        """,
        # List of courses attended by a student
        """
        -- List of courses attended by a student
        SELECT s.name
        FROM subjects s
        JOIN grades g ON s.id = g.subject_id
        WHERE g.student_id = ?;
        """,
        # List of courses taught by a selected lecturer for a specific student
        """
        -- List of courses taught by a selected lecturer for a specific student
        SELECT s.name
        FROM subjects s
        JOIN lecturers l ON s.lecturer_id = l.id
        JOIN grades g ON s.id = g.subject_id
        WHERE l.id = ? AND g.student_id = ?;
        """,
        # Additional queries
        # Average grades of a selected student given by a specific lecturer
        """
        -- Average grades of a selected student given by a specific lecturer
        SELECT AVG(g.grade) AS avg_grade
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        WHERE g.student_id = ? AND s.lecturer_id = ?;
        """,
        # Grades of students in a selected group for a specific subject on the last class
        """
        -- Grades of students in a selected group for a specific subject on the last class
        SELECT s.name AS student_name, g.grade, g.date
        FROM students s
        JOIN grades g ON s.id = g.student_id
        JOIN subjects sub ON g.subject_id = sub.id
        JOIN groups gr ON s.group_id = gr.id
        WHERE gr.id = ? AND sub.id = ?
        ORDER BY g.date DESC
        LIMIT 10;
        """
    ]

    for i, query in enumerate(queries, start=1):
        with open(f'query_{i}.sql', 'w') as f:
            f.write(query)

if __name__ == "__main__":
    main()