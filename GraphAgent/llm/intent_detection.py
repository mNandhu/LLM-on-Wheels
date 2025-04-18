from GraphAgent.config.constants import USER_INTENTS
from GraphAgent.config.prompts import PROMPT_INTENT_DETECTION_WITH_HISTORY
from .service import invoke_with_retries
from langchain.output_parsers import ResponseSchema


def classify_intent(user_input: str, history: list, llm) -> str:
    """
    Classifies the user's intent based on their input and conversation history.

    Args:
        user_input (str): The current user's input to be classified.
        history (list): Previous conversation history for context.
        llm: The language model to use for classification.

    Returns:
        str: The classified intent as one of the predefined USER_INTENTS.
    """
    numbered_intents = "\n".join(
        [f"{i}. {intent}" for i, intent in enumerate(USER_INTENTS, 1)]
    )

    schema = [
        ResponseSchema(
            name="intent", description=f"One of: {', '.join(USER_INTENTS.keys())}"
        )
    ]

    # Invoke with centralized retry+parsing
    parsed = invoke_with_retries(
        prompt=PROMPT_INTENT_DETECTION_WITH_HISTORY,
        llm=llm,
        input_vars={
            "user_input": user_input,
            "history": history,
            "intents": numbered_intents,
        },
        response_schemas=schema,
    )

    return parsed["intent"]


if __name__ == "__main__":
    from GraphAgent.llm.service import get_chat_llm
    from GraphAgent.utils.misc import Colors

    # Example driver code to test classify_intent with sample inputs

    # Sample test cases based on the defined USER_INTENTS
    test_cases = [
        "Find the nearest object in sight.",
        "What's the description of my current location?",
        "Navigate to coordinates 34.05, -118.25.",
        "Rotate 90 degrees.",
    ]

    # Initialize an empty history and the LLM instance
    history = []
    llm = get_chat_llm()

    # Iterate through test cases and print the classified intent for each
    for input_text in test_cases:
        try:
            intent = classify_intent(input_text, history, llm)
            print(f"Input: {Colors.BLUE}{input_text}{Colors.ENDC}")
            print(f"Predicted Intent: {Colors.GREEN}{intent}{Colors.ENDC}\n")
        except Exception as e:
            print(f"Input: {Colors.BLUE}{input_text}{Colors.ENDC}")
            print(f"Error: {Colors.RED}{e}{Colors.ENDC}\n")
