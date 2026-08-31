from tutor.tutor import Tutor
from student.student import Student
from database.database import Database
from config import STUDENT_ID
from datetime import date


# --------------------------------------------------
# Database setup
# --------------------------------------------------

db = Database()
db.create_tables()


# --------------------------------------------------
# Load or create student
# --------------------------------------------------

student = db.load_student(STUDENT_ID)

if student is None:

    print("No student profile found.")

    student = Student()

    student.name = input("Student name: ")
    student.grade = input("Grade: ")
    student.board = input("Board: ")
    student.learning_style = input("Learning style: ")
    student.current_topic = input("Current topic: ")

    student_id = db.save_student(student)

    print(f"Student profile created. ID: {student_id}")

else:

    print(f"Welcome back, {student.name}!")


# --------------------------------------------------
# Load current topic progress
# --------------------------------------------------

progress = db.get_current_topic_progress(
    STUDENT_ID,
    "Mathematics",
    student.current_topic
)

print("\n--- Current Topic Progress ---")

if progress:

    print(f"Topic: {progress['topic']}")
    print(f"Status: {progress['status']}")
    print(f"Confidence: {progress['confidence']}")
    print(f"Last revised: {progress['last_revised']}")

else:

    print("No progress record found.")


# --------------------------------------------------
# Create Tutor
# --------------------------------------------------

tutor = Tutor(student, progress)



# --------------------------------------------------
# Display student profile
# --------------------------------------------------

print("\n--- Student Profile ---")
print(student.summary())
print("----------------\n")


# --------------------------------------------------
# Start tutoring session
# --------------------------------------------------

print("AI Tutor")
print("Type 'exit' to quit.\n")


while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    if question.lower() == "/new":

        tutor.clear_conversation()

        print("Started a new conversation.\n")
        continue

    print(f"""Messages in memory:
    {tutor.conversation_length()}""")

    answer = tutor.ask(question)

    evidence = tutor.evaluate_response(question)

    print("\nTutor:")
    print(answer)

# TEMPORARY DIAGNOSTIC



# --------------------------------------------------
# End of tutoring session
# --------------------------------------------------

evaluable_evidence = [
    evidence
    for evidence in tutor.session_evidence
    if evidence in {
        "understood",
        "partial",
        "misconception"
    }
]

if progress and evaluable_evidence:

    new_confidence = tutor.calculate_new_confidence()

    if new_confidence is not None:

        new_status = tutor.calculate_new_status(
            new_confidence
        )

        db.update_topic_confidence(
            STUDENT_ID,
            progress["topic_id"],
            new_confidence
        )

        db.update_topic_status(
            STUDENT_ID,
            progress["topic_id"],
            new_status
        )

    db.update_topic_revision(
        STUDENT_ID,
        progress["topic_id"],
        date.today().isoformat()
    )

    print("\nLearning session recorded.")