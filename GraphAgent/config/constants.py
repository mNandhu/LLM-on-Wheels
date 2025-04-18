LLM_MODEL = "llama-3.3-70b-versatile"

LLM_MAX_RETRIES = 2  # Maximum number of retries for LLM operations

# Debug configuration flags
DEBUG_CONFIG = {
    "SHOW_STATE_CHANGES": True,  # Show state changes between nodes
    "SHOW_TIMING": True,  # Show execution time for each step
    "SHOW_DECISION_PROCESS": True,  # Show the task decision process
    "SHOW_CREWAI_DETAILS": True,  # Show CrewAI interaction details
    "COLORED_OUTPUT": True,  # Use colored terminal output
}

USER_INTENTS = {
    "FIND_OBJECT": "Locate a specific object in the environment.",
    "DESCRIBE_AREA": "Provide a description of the current surroundings.",
    "NAVIGATE_TO_COORDS": "Navigate to a specific set of coordinates.",
    "DIRECT_ACTION": "Execute a direct action, such as rotating or stopping.",
    # Yet to be implemented
    # "CHITCHAT": "Engage in casual conversation.",
    # "QUESTION_ANSWERING": "Answer a question about the environment or robot status.",
    # "UNKNOWN": "The user's intent is unclear.",
    # "CONFIRMATION": "Confirm a previous action or request.",
    # "NAVIGATE_TO_NAME": "Navigate to a location known by name."
}
