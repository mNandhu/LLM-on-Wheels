from .state import State
from ..utils.misc import Colors
from ..llm.service import get_chat_llm
from . import interfaces
from ..llm.intent_detection import classify_intent
from ..llm.coord_detection import detect_coords
from ..llm.memory_querying import extract_label
from ..utils.audio import record_audio
from ..llm.final_response import generate_final_response
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ..config.constants import USER_INTENTS

class Nodes:
    def __init__(self):
        self._chat_llm = None

    @property
    def chat_llm(self):
        if self._chat_llm is None:
            self._chat_llm = get_chat_llm(provider="groq")
        return self._chat_llm

    def user_input_node(self, state: State) -> State:
        """
        Captures user input (text or speech) and updates the state.

        Updates "user_input_text" and "current_robot_pose" in the state.
        """
        # Stub: Simulate capturing user speech (or text) and updating pose history.
        state["user_input_text"] = interfaces.transcribe_audio(
            state.get(
                "user_input_audio",
                record_audio(duration=3),  # Record audio if not provided
            )
        )
        # Update current pose as gathered from robot sensors.
        state["current_robot_pose"] = interfaces.get_current_pose()
        print(
            f"{Colors.BLUE}[user_input_node] Captured input: {state.get('user_input_text')}{Colors.ENDC}"
        )

        state["chat_history"].append(HumanMessage(content=state["user_input_text"]))

        return state

    def intent_detection_node(self, state: State) -> State:
        """
        Detects the intent of the user input and updates the state.

        Uses the classify_intent function to determine user intent from
        conversation history and current input.

        Updates "current_intent" in the state.
        """

        # Get user input and conversation history
        user_input = state.get("user_input_text", "")
        history = state.get("chat_history", [])

        # Use the classify_intent function to determine the intent
        intent = classify_intent(user_input, history, self.chat_llm)
        state["current_intent"] = intent

        state["chat_history"].append(
            SystemMessage(content=f"Detected intent: {intent}:\"{USER_INTENTS[intent]}\" in query: {user_input}")
        )

        print(
            f"{Colors.BLUE}[intent_detection_node] Detected intent: {state.get('current_intent')}{Colors.ENDC}"
        )
        return state

    def memory_query_node(self, state: State) -> State:
        # Query structured memory for objects or area descriptions
        if state.get("current_intent") in ["FIND_OBJECT", "DESCRIBE_AREA"]:
            # Ensure 'extracted_entities' is initialized
            if "extracted_entities" not in state:
                state["extracted_entities"] = {}

            # Extract object label from user input
            label = extract_label(
                state.get("user_input_text", ""),
                state.get("chat_history", []),
                self.chat_llm,
            )
            # Store extracted entity for debugging or reuse
            state["extracted_entities"]["label"] = label
            # Query memory for matching objects
            results = interfaces.query_memory(
                "object", {"label": label} if label else {}
            )
            state["memory_query_results"] = results
            # Determine if clarification is needed
            if not results:
                state["requires_clarification"] = True
            elif len(results) > 1:
                state["requires_clarification"] = True
            else:
                state["requires_clarification"] = False
            print(
                f"{Colors.BLUE}[memory_query_node] Query label: {label}, results: {results}, needs_clarity: {state.get('requires_clarification')}{Colors.ENDC}"
            )
            # Log to history
            state["chat_history"].append(
                SystemMessage(
                    content=f"Memory query for '{label}' returned {len(results)} result(s), clarification needed: {state.get('requires_clarification')}"
                )
            )
        return state

    def prep_nav_target_coords(self, state: State) -> State:
        # Extract navigation target coordinates from user input using LLM
        user_input = state.get("user_input_text", "")
        history = state.get("chat_history", [])
        try:
            coords = detect_coords(user_input, history, self.chat_llm)
            x, y, theta = (
                coords.get("x", 0.0),
                coords.get("y", 0.0),
                coords.get("theta", 0.0),
            )
            state["navigation_target"] = (x, y, theta)
            print(
                f"{Colors.BLUE}[prep_nav_target_coords] Extracted coords -> x: {x}, y: {y}, theta: {theta}{Colors.ENDC}"
            )
            # Log to history
            state["chat_history"].append(
                SystemMessage(
                    content=f"Extracted navigation coordinates: x={x}, y={y}, theta={theta}"
                )
            )
        except Exception as e:
            print(
                f"{Colors.RED}[prep_nav_target_coords] Coordinate extraction failed: {e}{Colors.ENDC}"
            )
        return state

    def prep_nav_target_memory(self, state: State) -> State:
        # Prepare navigation target based on memory query result
        results = state.get("memory_query_results", [])
        if results and not state.get("requires_clarification"):
            # Use first unique result's map_coordinates
            entry = results[0]
            coords = entry.get("map_coordinates", {})
            x = coords.get("x", 0.0)
            y = coords.get("y", 0.0)
            theta = coords.get("theta", 0.0)
            state["navigation_target"] = (x, y, theta)
            print(
                f"{Colors.BLUE}[prep_nav_target_memory] Navigation target from memory: {state.get('navigation_target')}{Colors.ENDC}"
            )
            # Log to history
            state["chat_history"].append(
                SystemMessage(
                    content=f"Prepared navigation target from memory at {state.get('navigation_target')}"
                )
            )
        return state

    def navigation_node(self, state: State) -> State:
        # Execute navigation if a target is set.
        if state.get("navigation_target"):
            x, y, theta = state["navigation_target"]
            interfaces.send_nav_goal(x, y, theta)
            state["navigation_status"] = interfaces.get_nav_status()

            # Log to history
            state["chat_history"].append(
                SystemMessage(
                    content=f"Navigation command sent to robot with target: {state.get('navigation_target')} - IN_PROGRESS"
                )
                )

            # FIXME: This blocks execution, because the simulation is running in the same thread.
            while state["navigation_status"] == "IN_PROGRESS":
                # Poll for navigation status until completed
                state["navigation_status"] = interfaces.get_nav_status()
            print(
                f"{Colors.BLUE}[navigation_node] Navigation status: {state.get('navigation_status')}{Colors.ENDC}"
            )

            # Update current pose
            state["current_robot_pose"] = interfaces.get_current_pose()

            # Log to history
            state["chat_history"].append(
                SystemMessage(
                    content=f"Navigation action completed with status: {state.get('navigation_status')}"
                )
            )
        return state

    def action_execution_node(self, state: State) -> State:
        # Stub: Execute a direct robot action.
        state["action_status"] = interfaces.execute_robot_action(
            "rotate", {"angle": 90}
        )
        print(
            f"{Colors.BLUE}[action_execution_node] Action status: {state.get('action_status')}{Colors.ENDC}"
        )
        # Log to history
        state["chat_history"].append(
            SystemMessage(
                content=f"Action 'rotate' executed with status: {state.get('action_status')}"
            )
        )
        return state

    def llm_response_node(self, state: State) -> State:
        # Generate final LLM response based on full state context
        response = generate_final_response(state, self.chat_llm)
        state["llm_response_text"] = response
        # Append assistant message to chat history
        state["chat_history"].append(AIMessage(content=response))
        print(
            f"{Colors.BLUE}[llm_response_node] LLM response text: {response}{Colors.ENDC}"
        )
        return state

    def text_to_speech_node(self, state: State) -> State:
        # Convert the final response text to speech.
        state["final_response_text"] = state.get("llm_response_text") or "No response."
        # Synthesize speech and get audio file path
        audio_file = interfaces.synthesize_speech(state["final_response_text"])
        state["final_response_audio"] = audio_file
        # Log audio file location and response text
        print(
            f"{Colors.BLUE}[text_to_speech_node] Generated audio file: {audio_file}{Colors.ENDC}"
        )
        print(
            f"{Colors.BLUE}[text_to_speech_node] Final response text: {state.get('final_response_text')}{Colors.ENDC}"
        )
        return state
