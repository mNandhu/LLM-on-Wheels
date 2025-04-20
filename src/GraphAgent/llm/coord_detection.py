from ..config.prompts import PROMPT_COORD_DETECTION_WITH_HISTORY
from .service import invoke_with_retries
from langchain.output_parsers import ResponseSchema


def detect_coords(user_input: str, history: list, llm) -> dict:
    """
    Extracts navigation coordinates (x, y, theta) from user input using the LLM.

    Args:
        user_input (str): The user's navigation command.
        history (list): Conversation history context.
        llm: The language model for extraction.

    Returns:
        dict: Parsed coordinates with float values for 'x', 'y', and 'theta'.
    """
    schema = [
        ResponseSchema(name="x", description="X coordinate as float"),
        ResponseSchema(name="y", description="Y coordinate as float"),
        ResponseSchema(name="theta", description="Theta orientation as float"),
    ]
    parsed = invoke_with_retries(
        prompt=PROMPT_COORD_DETECTION_WITH_HISTORY,
        llm=llm,
        input_vars={"user_input": user_input, "history": history},
        response_schemas=schema,
    )

    # Convert extracted values to float, handling None values
    return {
        "x": float(parsed.get("x", 0.0)) if parsed.get("x") is not None else None,
        "y": float(parsed.get("y", 0.0)) if parsed.get("y") is not None else None,
        "theta": float(parsed.get("theta", 0.0))
        if parsed.get("theta") is not None
        else None,
    }


if __name__ == "__main__":
    from src.GraphAgent.llm.service import get_chat_llm
    from src.GraphAgent.utils.misc import Colors

    # Example driver code to test detect_coords with sample inputs

    # Sample test cases with various coordinate formats
    test_cases = [
        "Go to coordinates x=10, y=20, theta=45",
        "Navigate to position 5.5, 7.8 with orientation 90 degrees",
        "Move to x 3.2 y -4.1 and face theta 180",
        "Can you help me get to coordinates (15, 25) facing 270 degrees?",
        "What's the weather like today?",  # No coordinates case
    ]

    # Initialize an empty history and the LLM instance
    history = []
    llm = get_chat_llm()

    # Iterate through test cases and print the extracted coordinates for each
    for input_text in test_cases:
        # try:
        coords = detect_coords(input_text, history, llm)
        print(f"Input: {Colors.BLUE}{input_text}{Colors.ENDC}")
        print(
            f"Extracted Coordinates: {Colors.GREEN}x={coords['x']}, y={coords['y']}, theta={coords['theta']}{Colors.ENDC}\n"
        )
        # except Exception as e:
        #     print(f"Input: {Colors.BLUE}{input_text}{Colors.ENDC}")
        #     print(f"Error: {Colors.RED}{e}{Colors.ENDC}\n")
