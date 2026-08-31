class Student:

    def __init__(self):

        self.name = ""

        self.grade = ""

        self.board = ""

        self.subjects = []

        self.current_topic = ""

        self.learning_style = ""

        self.goals = []

        self.strong_topics = []

        self.weak_topics = []


    def summary(self):

        return f"""
     Name: {self.name}
     Grade: {self.grade}
     Board: {self.board}
     Subjects: {", ".join(self.subjects)}
     Current Topic: {self.current_topic}
     Learning Style: {self.learning_style}
     Goals: {", ".join(self.goals)}
     Weak Topics: {", ".join(self.weak_topics)}
     Strong Topics: {", ".join(self.strong_topics)}
     """