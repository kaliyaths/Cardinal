
from ollama import chat
from prompts import build_system_prompt, build_evidence_prompt
from config import MODEL_NAME
from student.student import Student
from rag_search import load_index, search_chunks


def get_index_filename(topic):

    topic_indexes = {
        "Integration": "mathematics_index.json"
    }

    return topic_indexes.get(topic)

class Tutor:

    def __init__(self, student, topic_progress=None):

        self.model = MODEL_NAME

        self.student = student

        self.topic_progress = topic_progress

        self.session_evidence = []

        self.last_context = ""

        index_filename = get_index_filename(
            self.student.current_topic
        )

        
        
        if index_filename:
            self.index = load_index(index_filename)
        else:
            self.index = []

        self.messages = [
            {
                "role": "system",
                "content": build_system_prompt(
                    self.student,
                    self.topic_progress
                )
            }
        ]





    def ask(self, question):

        results = search_chunks(
            question,
            self.index
        )

        best_score = results[0][0]

        if best_score < 0.5:

            return (
            "That topic isn't covered in the material "
            "we're currently studying."
        )

        relevant_chunks = results[:2]

        context = "\n\n".join(
            chunk
            for score, chunk in relevant_chunks
        )

        self.last_context = context

        prompt = f"""
        
        You are a Socratic home tutor.

        Your job is to help the student understand the material rather than
        simply giving them answers.

        SOURCE MATERIAL:
        {context}

        STUDENT MESSAGE:
        {question}

        IMPORTANT RULES:

        1. Base your response ONLY on the supplied SOURCE MATERIAL and the
        conversation history.

        2. If the student's question cannot be answered from the SOURCE
        MATERIAL, say:
        "That topic isn't covered in the material we're currently studying."
        Do not answer it using your general knowledge.

        3. Respond specifically to the student's latest message.

        4. Use the Socratic method. Guide the student with ONE teaching move
        at a time.

        5. Ask AT MOST ONE question in your response.

        6. Do not use analogies unless they are present in the SOURCE MATERIAL.

        7. Do not give the complete answer unless the student has demonstrated
        that they cannot reach it with reasonable guidance.

        8. Keep the response short: normally 2-4 sentences.

        9. Do not add motivational speeches, repeated encouragement, or
        unnecessary summaries.

        10. Do not introduce facts that are not contained in the SOURCE MATERIAL
            or the conversation history.

    """

        self.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = chat(
            model=self.model,
            messages=self.messages
        )

        answer = response["message"]["content"]

        self.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    def clear_conversation(self):

        self.messages = [
            {
                "role": "system",
                "content": build_system_prompt(self.student)
            }
        ]

        self.session_evidence = []


    def conversation_length(self):

        return len(self.messages)

    def get_student_responses(self):

        responses = []

        for message in self.messages:

            if message["role"] == "user":
                responses.append(message["content"])

        return responses

    def evaluate_response(self, student_response):

        response_text = student_response.strip().lower()

        question_starters = (
            "why ",
            "what ",
            "how ",
            "when ",
            "where ",
            "who ",
            "which ",
            "can you ",
            "could you ",
            "would you "
        )

        if (
            response_text.endswith("?")
            or response_text.startswith(question_starters)
        ):
            evidence = "question"
            self.session_evidence.append(evidence)
            return evidence


        prompt = build_evidence_prompt(
        student_response,
        self.student.current_topic,
        self.last_context
    )

        response = chat(
            model=self.model,
                messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_evidence = response["message"]["content"].strip().lower()

        valid_categories = {
                    "partial",
                    "understood",
                    "misconception"
                }

        if raw_evidence in valid_categories:
            evidence = raw_evidence
        else:
            print(
                f"Warning: Unexpected evidence classification: "
                f"{raw_evidence}"
            )
            evidence = "partial"

        self.session_evidence.append(evidence)

        return evidence

    def calculate_confidence_change(self, evidence):

        if evidence == "understood":
            return 5

        if evidence == "misconception":
            return -5

        return 0

    def calculate_session_confidence_change(self):

        evaluable = [
        evidence
        for evidence in self.session_evidence
        if evidence in {"understood", "partial", "misconception"}
    ]

        if len(evaluable) < 2:
             return 0

        understood_count = evaluable.count("understood")
        misconception_count = evaluable.count("misconception")

        total = understood_count + misconception_count

        if total == 0:
            return 0

        positive_ratio = understood_count / total
        negative_ratio = misconception_count / total

        if positive_ratio >= 0.75:
            return 5

        if positive_ratio > 0.5:
           return 3

        if negative_ratio >= 0.75:
           return -5

        if negative_ratio > 0.5:
           return -3

        return 0

    def calculate_new_confidence(self):

        if not self.topic_progress:
            return None

        current_confidence = self.topic_progress["confidence"]

        change = self.calculate_session_confidence_change()

        new_confidence = current_confidence + change

        new_confidence = max(0, min(100, new_confidence))

        return new_confidence

    def calculate_new_status(self, new_confidence):

        if new_confidence <= 30:
            return "Needs Review"

        return "In Progress"
