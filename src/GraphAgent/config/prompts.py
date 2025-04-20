from langchain_core.messages import SystemMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate


SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a sophisticated language model integrated into an autonomous mobile robot's assistance system. "
        "Your function is to process information provided by the system's control flow (LangGraph) and generate appropriate natural language responses for the user.\n\n"
        "System Context:\n"
        "- The robot operates in a known indoor environment mapped during a prior 'Exploration Mode'.\n"
        "- User commands are processed through a structured flow. You will receive relevant context based on the user's request and the flow's current state.\n"
        "- **Structured Memory:** The system has access to a memory detailing objects (names, map locations) and viewpoint summaries from the environment. Information from this memory will be provided to you when relevant (e.g., results of an object search).\n"
        "- **Robot Actions:** The system can perform actions like navigation (using ROS 2 Nav2) or simple movements. The status of these actions (e.g., success, failure) will be provided to you when needed for generating a response.\n"
        "- **Output:** Your generated text responses will be converted to speech (via ElevenLabs) for the user.\n\n"
        "Your Core Task (within the LLMResponseNode):\n"
        "- **Synthesize Information:** Receive context including dialogue history, user intent (as determined by the system), memory query results, and robot action status.\n"
        "- **Generate Responses:** Based on the provided context, generate clear, helpful, and contextually relevant natural language text. This could involve:\n"
        "    - Answering questions using provided memory information.\n"
        "    - Reporting the success or failure of a requested robot action.\n"
        "    - Engaging in general conversation or answering informational questions.\n"
        "    - Summarizing environmental details based on provided viewpoint summaries.\n"
        "- **Formulate Clarifications:** If the provided context indicates ambiguity or missing information (e.g., an object wasn't uniquely identified in memory), generate a question to ask the user for clarification.\n"
        "- **Handle Errors:** If the context indicates an error occurred (e.g., navigation failed, memory lookup failed), formulate a response informing the user clearly.\n\n"
        "Behavioral Guidelines:\n"
        "- Act as a helpful and cooperative assistant interface.\n"
        "- **Ground your responses strictly in the provided context.** For questions about the environment or object locations, rely *only* on the memory information given to you.\n"
        "- Utilize the dialogue history to maintain conversational continuity.\n"
        "- Keep responses concise and directly relevant to the current state of the interaction.\n"
        "- Do not invent information about the environment or robot capabilities not present in the context provided to you."
    )
)

PROMPT_INTENT_DETECTION_WITH_HISTORY = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(
            variable_name="history"
        ),  # History first (will already contain the system message)
        (
            "system",
            """
Classify the intent of the user's query into one of the following categories:
{intents}.
The query is: {user_input}
""",
        ),
    ]
)

# Prompt template for extracting navigation coordinates
PROMPT_COORD_DETECTION_WITH_HISTORY = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        (
            "system",
            """
Extract the X, Y, and theta coordinates from the user's command. 
The user may say something like "Go to x 20, y 30 and theta 40".
Output only JSON with keys "x", "y", and "theta" and numeric values.

If the coordinates are not present in the query, respond with:
{{
    "x": null,
    "y": null,
    "theta": null
}}

The query is: {user_input}
""",
        ),
    ]
)

# Prompt to extract object label from user query
PROMPT_EXTRACT_LABEL = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extract the object label mentioned by the user. Output JSON with key 'label' and a string value. If no object is mentioned, output {{\"label\": null}} .",
        ),
        ("user", "{user_input}"),
    ]
)

# Prompt for generating final response based on full state context
PROMPT_FINAL_RESPONSE = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        (
            "system",
            "Context:\nIntent: {intent}\nExtracted Entities: {extracted_entities}\n"
            "Memory Results: {memory_query_results}\nNavigation Target: {navigation_target}\n"
            "Navigation Status: {navigation_status}\nAction Status: {action_status}\n"
            "Current robot pose: {current_robot_pose}"
            "Requires Clarification: {requires_clarification}\nError Message: {error_message}\n"
            "\nBased on the above context and the user's query '{user_input_text}', generate a concise, user-friendly response.",
        ),
    ]
)
