from student.student import Student
import sqlite3



class Database:
    def __init__(self, db_name="database/cardinal.db"):
        self.connection = sqlite3.connect(db_name)

        self.connection.execute("PRAGMA foreign_keys =ON")


    def create_tables(self):

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS 

            students(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                board TEXT,
                learning_style TEXT
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS
            
            subjects(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
              )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS
            
            student_subjects(
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,

                PRIMARY KEY(student_id, subject_id),
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
               
              )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS
            
            topics(
                id INTEGER PRIMARY KEY,
                subject_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                
                FOREIGN KEY (subject_id) REFERENCES subjects(id),

                UNIQUE (subject_id, name)

              )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS
            
            student_topics(
                student_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,

                status TEXT,
                confidence INTEGER,
                last_revised TEXT,

                PRIMARY KEY (student_id, topic_id),
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id)
              )
        """)
        self.connection.commit()

    def show_tables(self):

        cursor = self.connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type ='table'
            
          """)
        return cursor.fetchall()
    def add_subject(self, name):

        self.connection.execute(
        """
        INSERT OR IGNORE INTO subjects (name)
        VALUES (?)
        """,
        (name,)
    )

        self.connection.commit()

        cursor = self.connection.execute(
        """
        SELECT id
        FROM subjects
        WHERE name = ?
        """,
        (name,)
    )

        return cursor.fetchone()[0]

    def get_subject(self, subject_id):

        cursor = self.connection.execute("""
            SELECT id, name
            FROM subjects
            WHERE id =?
            """,
            (subject_id,)
            )
        return cursor.fetchone()

    def get_subjects(self):

        cursor = self.connection.execute("""
            SELECT id, name
            FROM subjects
            ORDER BY name
            """
            
            )
        return cursor.fetchall()
    
    def add_topic(self, subject_id, name):

        cursor = self.connection.execute(
        """
        INSERT OR IGNORE INTO topics
        (subject_id, name)
        VALUES (?, ?)
        """,
        (subject_id, name)
    )

        self.connection.commit()

        cursor = self.connection.execute(
        """
        SELECT id
        FROM topics
        WHERE subject_id = ? AND name = ?
        """,
        (subject_id, name)
    )

        return cursor.fetchone()[0]

    def assign_subject(self, student_id, subject_id):

        self.connection.execute(
        """
        INSERT OR IGNORE INTO student_subjects
        (student_id, subject_id)
        VALUES (?, ?)
        """,
        (student_id, subject_id)
           )

        self.connection.commit()

    def get_student_subjects(self, student_id):

        cursor = self.connection.execute(
        """
        SELECT subjects.id, subjects.name
        FROM subjects
        JOIN student_subjects
            ON subjects.id = student_subjects.subject_id
        WHERE student_subjects.student_id = ?
        ORDER BY subjects.name
        """,
        (student_id,)
        )

        return cursor.fetchall()

    def save_student(self, student):

        cursor = self.connection.execute(
            """
            INSERT INTO students(
            name,grade,board,learning_style)
            VALUES(?,?,?,?)
            """,
            (
                student.name,
                student.grade,
                student.board,
                student.learning_style
            )
        )


        self.connection.commit()

        return cursor.lastrowid

    def get_student(self, student_id):

        cursor = self.connection.execute(
            "SELECT * FROM students WHERE id =?",
            (student_id,)
        )
        return cursor.fetchone()

    def load_student(self, student_id):

        row = self.get_student(student_id)

        if row is None:
            return None

        student = Student()

        student.name = row[1]
        student.grade = row[2]
        student.board = row[3]
        student.learning_style = row[4]

        return student

    def update_student(self, student_id, student):

        self.connection.execute(
        """
        UPDATE students
        SET name = ?,
            grade = ?,
            board = ?,
            learning_style = ?
        WHERE id = ?
        """,
        (
            student.name,
            student.grade,
            student.board,
            student.learning_style,
            student_id
        )
    )

        self.connection.commit()

    def set_student_topic(
    self,
    student_id,
    topic_id,
    status,
    confidence,
    last_revised
):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO student_topics
        (student_id, topic_id, status, confidence, last_revised)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            student_id,
            topic_id,
            status,
            confidence,
            last_revised
        )
    )

        self.connection.commit()


    def get_student_topic(self, student_id, topic_id):

        cursor = self.connection.execute(
        """
        SELECT
            student_topics.topic_id,
            topics.name,
            student_topics.status,
            student_topics.confidence,
            student_topics.last_revised
        FROM student_topics
        JOIN topics
            ON student_topics.topic_id = topics.id
        WHERE student_topics.student_id = ?
          AND student_topics.topic_id = ?
        """,
        (student_id, topic_id)
    )

        return cursor.fetchone()
    
    def get_student_topics(self, student_id):

        cursor = self.connection.execute(
        """
        SELECT
            student_topics.topic_id,
            topics.name,
            student_topics.status,
            student_topics.confidence,
            student_topics.last_revised
        FROM student_topics
        JOIN topics
            ON student_topics.topic_id = topics.id
        WHERE student_topics.student_id = ?
        ORDER BY topics.name
        """,
        (student_id,)
    )

        return cursor.fetchall()


# Temp lines of code

# db = Database()

# student_id = 1

# math_id = db.add_subject("Mathematics")

# integration_id = db.add_topic(
#     math_id,
#     "Integration"
# )

# db.set_student_topic(
#     student_id,
#     integration_id,
#     "weak",
#     2,
#     "2026-08-13"
# )

# print(
#     db.get_student_topic(
#         student_id,
#         integration_id
#     )
# )

db = Database()

db.create_tables()

math_id = db.add_subject("Mathematics")

print("math_id =", math_id)
print("subjects =", db.get_subjects())

integration_id = db.add_topic(
    math_id,
    "Integration"
)

print("integration_id =", integration_id)


