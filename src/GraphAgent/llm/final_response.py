# filepath: g:\Projects\LLM-on-Wheels\src\GraphAgent\llm\final_response.py
from typing import Any, Dict
from ..config.prompts import PROMPT_FINAL_RESPONSE
from .service import invoke_with_retries, get_chat_llm
from langchain.output_parsers import ResponseSchema


def generate_final_response(state: Any, llm=None) -> str:
    """
    Generate a final user-friendly response based on the full state context.
    """
    llm = llm or get_chat_llm()
    # Prepare input variables for the prompt
    input_vars: Dict[str, Any] = {
        "history": state.get("chat_history", []),
        "intent": state.get("current_intent"),
        "extracted_entities": state.get("extracted_entities"),
        "memory_query_results": state.get("memory_query_results"),
        "navigation_target": state.get("navigation_target"),
        "navigation_status": state.get("navigation_status"),
        "action_status": state.get("action_status"),
        "requires_clarification": state.get("requires_clarification"),
        "error_message": state.get("error_message"),
        "user_input_text": state.get("user_input_text"),
        "current_robot_pose": state.get("current_robot_pose"),
    }
    # Invoke the LLM with structured parsing for reliability
    schema = [ResponseSchema(name="response", description="User-facing response text")]
    try:
        parsed = invoke_with_retries(
            prompt=PROMPT_FINAL_RESPONSE,
            llm=llm,
            input_vars=input_vars,
            response_schemas=schema,
        )
        response = parsed.get("response", "")
    except Exception as e:
        response = f"Error generating response: {e}"
    return response
