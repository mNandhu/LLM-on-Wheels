from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from ..config.constants import LLM_MAX_RETRIES, LLM_MODEL
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Load environment variables from .env file
load_dotenv()

# Get the Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")


def get_chat_llm(provider: str = "groq") -> ChatGroq:
    """
    Get the chat LLM based on the provider specified.

    Args:
        provider (str): The name of the provider. Currently only 'groq' is supported.

    Returns:
        ChatGroq: An instance of the ChatGroq class.
    """
    if provider == "groq":
        return ChatGroq(api_key=groq_api_key, model=LLM_MODEL, temperature=0.2)
    else:
        raise ValueError(f"Provider {provider} is not supported.")


def invoke_with_retries(
    prompt: ChatPromptTemplate,
    llm: Any,
    input_vars: Dict[str, Any],
    response_schemas: List[ResponseSchema],
    max_retries: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Invoke an LLM chain with structured parsing and retry logic.

    Args:
        prompt: A ChatPromptTemplate containing placeholders for variables, including
                'format_instructions' and 'errors'.
        llm: The LLM instance or chain endpoint.
        input_vars: Dictionary of variables to pass into the prompt invocation.
        response_schemas: List of ResponseSchema defining the expected output structure.
        max_retries: Number of retry attempts on parsing failure. Defaults to LLM_MAX_RETRIES.

    Returns:
        A dict representing the parsed output according to the provided schemas.

    Raises:
        ValueError: If parsing fails after all retry attempts.
    """
    # Determine number of retries
    retries = max_retries if max_retries is not None else LLM_MAX_RETRIES

    # Build structured output parser
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = parser.get_format_instructions()

    # Prepare invocation variables
    input_vars = input_vars.copy()
    input_vars["format_instructions"] = format_instructions

    # Build a wrapped prompt that includes format and error instructions in the template
    wrapped_prompt = ChatPromptTemplate.from_messages(
        prompt.messages
        + [
            (
                "system",
                "Follow these format instructions exactly:\n{format_instructions}",
            ),
            ("system", "Errors accumulated so far:\n{errors}"),
        ]
    )

    # Initialize error accumulation
    errors: List[str] = []

    # Retry loop
    for attempt in range(retries + 1):
        input_vars["errors"] = "\n".join(errors)
        chain = wrapped_prompt | llm
        result = chain.invoke(input_vars)
        try:
            return parser.parse(result.content)
        except Exception as e:
            errors.append(str(e))

    # Raise after exhausting retries
    raise ValueError(f"Parsing failed after {retries + 1} attempts. Errors: {errors}")
