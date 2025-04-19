from .state import State
from GraphAgent.utils.misc import Colors
from GraphAgent.llm.service import get_chat_llm
from . import interfaces
from GraphAgent.llm.intent_detection import classify_intent
from GraphAgent.llm.coord_detection import detect_coords


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
                "data/audio/goto_20_40_75.wav",
            )
        )
        # Update current pose as gathered from robot sensors.
        state["current_robot_pose"] = interfaces.get_current_pose()
        print(
            f"{Colors.BLUE}[user_input_node] Captured input: {state.get('user_input_text')}{Colors.ENDC}"
        )

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

        print(
            f"{Colors.BLUE}[intent_detection_node] Detected intent: {state.get('current_intent')}{Colors.ENDC}"
        )
        return state

    def memory_query_node(self, state: State) -> State:
        # Stub: Query structured memory if intent requires it.
        # Here we use a placeholder query; criteria could be based on extracted_entities.
        if state.get("current_intent") in ["FIND_OBJECT", "DESCRIBE_AREA"]:
            state["memory_query_results"] = interfaces.query_memory(
                "object", state.get("extracted_entities")
            )
            print(
                f"{Colors.BLUE}[memory_query_node] Memory query results: {state.get('memory_query_results')}{Colors.ENDC}"
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
        except Exception as e:
            print(
                f"{Colors.RED}[prep_nav_target_coords] Coordinate extraction failed: {e}{Colors.ENDC}"
            )
        return state

    def prep_nav_target_memory(self, state: State) -> State:
        # Stub: Prepare navigation target based on memory query result.
        if state.get("memory_query_results"):
            # Simplest example: using first result's location.
            result = state["memory_query_results"][0]
            state["navigation_target"] = result.get("location", (0.0, 0.0, 0.0))
            print(
                f"{Colors.BLUE}[prep_nav_target_memory] Navigation target (from memory): {state.get('navigation_target')}{Colors.ENDC}"
            )
        return state

    def navigation_node(self, state: State) -> State:
        # Stub: Execute navigation if a target is set.
        if state.get("navigation_target"):
            x, y, theta = state["navigation_target"]
            interfaces.send_nav_goal(x, y, theta)
            state["navigation_status"] = interfaces.get_nav_status()
            print(
                f"{Colors.BLUE}[navigation_node] Navigation status: {state.get('navigation_status')}{Colors.ENDC}"
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
        return state

    def llm_response_node(self, state: State) -> State:
        # Stub: Generate LLM response, for clarifications or general Q&A.
        state["llm_response_text"] = state.get("user_input_text")  # Mirror input (stub)
        print(
            f"{Colors.BLUE}[llm_response_node] LLM response text: {state.get('llm_response_text')}{Colors.ENDC}"
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
