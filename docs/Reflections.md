Lesson 8

	Concept learned: An LLM only knows information explicitly provided in its context.
	Design decision: Separate permanent tutor instructions from dynamic student information.
	Architecture learned: Dependency injection — create the Student outside Tutor and pass it in.
	Important future problem: As memory and knowledge grow, we need a Context Builder to decide what information Gemma needs for each interaction.