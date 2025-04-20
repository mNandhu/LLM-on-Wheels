# filepath: g:\Projects\LLM-on-Wheels\src\GraphAgent\llm\memory_querying.py
from ..config.prompts import PROMPT_EXTRACT_LABEL
from .service import invoke_with_retries, get_chat_llm
from langchain.output_parsers import ResponseSchema
from typing import Optional, List, Any


def extract_label(user_input: str, history: List[Any], llm=None) -> Optional[str]:
    """
    Extracts object label from user_input using LLM prompt.
    """
    llm = llm or get_chat_llm()
    schema = [ResponseSchema(name="label", description="Extracted object label")]
    parsed = invoke_with_retries(
        prompt=PROMPT_EXTRACT_LABEL,
        llm=llm,
        input_vars={"user_input": user_input, "history": history},
        response_schemas=schema,
    )
    return parsed.get("label")
