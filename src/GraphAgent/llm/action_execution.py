# filepath: g:\Projects\LLM-on-Wheels\src\GraphAgent\llm\action_execution.py
from typing import Dict, Any, List
from ..config.prompts import PROMPT_EXTRACT_ACTION
from .service import invoke_with_retries, get_chat_llm
from langchain.output_parsers import ResponseSchema


def extract_action_params(
    user_input: str, history: List[Any], llm=None
) -> Dict[str, Any]:
    """
    Extract robot action and parameters from user input using LLM.
    """
    llm = llm or get_chat_llm()
    schema = [
        ResponseSchema(name="action", description="One of: rotate, move_forward"),
        ResponseSchema(
            name="angle",
            description="Rotation angle in degrees, or null if not applicable",
        ),
        ResponseSchema(
            name="duration",
            description="Duration in seconds for move_forward, or null if not applicable",
        ),
    ]
    parsed = invoke_with_retries(
        prompt=PROMPT_EXTRACT_ACTION,
        llm=llm,
        input_vars={"user_input": user_input, "history": history},
        response_schemas=schema,
    )
    # Ensure correct types
    try:
        if parsed.get("angle") is not None:
            parsed["angle"] = float(parsed["angle"])
    except:
        parsed["angle"] = None
    try:
        if parsed.get("duration") is not None:
            parsed["duration"] = float(parsed["duration"])
    except:
        parsed["duration"] = None
    return parsed
