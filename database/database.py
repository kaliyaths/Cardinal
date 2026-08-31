from student.student import Student
import sqlite3



class Database:
    def __init__(self, db_name="database/cardinal.db"):
        self.connection = sqlite3.connect(db_name)

        self.connection.execute("PRAGMA foreign_keys = ON")


    def create_tables(self):

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS 

            students(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                board TEXT,
                learning_style TEXT,
                current_topic TEXT
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
                name TEXT NOT NULL,
                
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

    def get_topic(self, subject_id, name):

        cursor = self.connection.execute(
        """
        SELECT id, name
        FROM topics
        WHERE subject_id = ? AND name = ?
        """,
        (subject_id, name)
    )

        return cursor.fetchone()

    def get_subject_by_name(self, name):

        cursor = self.connection.execute(
        """
        SELECT id, name
        FROM subjects
        WHERE name = ?
        """,
        (name,)
    )

        return cursor.fetchone()
    
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
            name,grade,board,learning_style, current_topic)
            VALUES(?,?,?,?,?)
            """,
            (
                student.name,
                student.grade,
                student.board,
                student.learning_style,
                student.current_topic
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
        student.current_topic = row[5]

        return student

    def update_student(self, student_id, student):

        self.connection.execute(
        """
        UPDATE students
        SET name = ?,
            grade = ?,
            board = ?,
            learning_style = ?,
            current_topic = ?
        WHERE id = ?
        """,
        (
            student.name,
            student.grade,
            student.board,
            student.learning_style,
            student.current_topic,
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

    def get_current_topic_progress(self, student_id, subject_name, topic_name):

        cursor = self.connection.execute(
        """
        SELECT
            topics.id,
            topics.name,
            student_topics.status,
            student_topics.confidence,
            student_topics.last_revised
        FROM student_topics
        JOIN topics
            ON student_topics.topic_id = topics.id
        JOIN subjects
            ON topics.subject_id = subjects.id
        WHERE student_topics.student_id = ?
          AND subjects.name = ?
          AND topics.name = ?
        """,
        (
            student_id,
            subject_name,
            topic_name
        )
    )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
        "topic_id": row[0],
        "topic": row[1],
        "status": row[2],
        "confidence": row[3],
        "last_revised": row[4]
    }

    def update_topic_revision(self, student_id, topic_id, last_revised):

        self.connection.execute(
        """
        UPDATE student_topics
        SET last_revised = ?
        WHERE student_id = ?
          AND topic_id = ?
        """,
        (
            last_revised,
            student_id,
            topic_id
        )
    )

        self.connection.commit()

    def update_topic_confidence(
    self,
    student_id,
    topic_id,
    confidence
):

        self.connection.execute(
            """
            UPDATE student_topics
            SET confidence = ?
            WHERE student_id = ?
            AND topic_id = ?
            """,
            (
                confidence,
                student_id,
                topic_id
            )
        )

        self.connection.commit()

    def update_topic_status(
        self,
        student_id,
        topic_id,
        status
    ):

        self.connection.execute(
            """
            UPDATE student_topics
            SET status = ?
            WHERE student_id = ?
            AND topic_id = ?
            """,
            (
                status,
                student_id,
                topic_id
            )
        )

        self.connection.commit()


# TEMPORARY TEST
# print("update_topic_revision exists:",
#       hasattr(Database, "update_topic_revision"))