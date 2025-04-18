"""Define the state structures for the agent."""

from __future__ import annotations

from typing import List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState


class State(MessagesState):
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    for more information.
    """

    task_decision: Optional[str] = None
    database_agent_responses: List[str] = None
    invalid_decision_count: int = 0
    chat_history: List[BaseMessage] = None
