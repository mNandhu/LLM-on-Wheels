"""Define the state structures for the agent."""

from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any
from langgraph.graph import MessagesState


class State(MessagesState):
    """
    Defines the input state for the agent, representing a narrower interface to the outside world.
    """

    user_input_text: str = ""
    dialogue_history: List[Tuple[str, str]] = []  # (speaker, text)
    current_intent: Optional[str] = None
    extracted_entities: Dict[str, Any] = {}
    memory_query_results: List[Dict[str, Any]] = []
    navigation_target: Optional[Tuple[float, float, float]] = None  # (x, y, theta)
    navigation_status: Optional[str] = None
    action_status: Optional[str] = None
    llm_response_text: Optional[str] = None
    final_response_text: Optional[str] = None
    requires_clarification: bool = False
    error_message: Optional[str] = None
    current_robot_pose: Optional[Tuple[float, float, float]] = None
