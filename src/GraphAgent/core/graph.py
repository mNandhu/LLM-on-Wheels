from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import State
from .nodes import Nodes
from ..config.prompts import SYSTEM_PROMPT


class WorkFlow:
    def __init__(self):
        self._nodes = None
        self._app = None
        self.chat_history = []
        self.chat_history.append(SYSTEM_PROMPT)

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = Nodes()
        return self._nodes

    @property
    def app(self):
        if self._app is None:
            self._initialize_workflow()
        return self._app

    def _initialize_workflow(self):
        workflow = StateGraph(State)

        # Add nodes according to the flow.
        workflow.add_node("user_input_node", self.nodes.user_input_node)
        workflow.add_node("intent_detection_node", self.nodes.intent_detection_node)
        workflow.add_node("memory_query_node", self.nodes.memory_query_node)
        workflow.add_node("prep_nav_target_coords", self.nodes.prep_nav_target_coords)
        workflow.add_node("prep_nav_target_memory", self.nodes.prep_nav_target_memory)
        workflow.add_node("navigation_node", self.nodes.navigation_node)
        workflow.add_node("action_execution_node", self.nodes.action_execution_node)
        workflow.add_node("llm_response_node", self.nodes.llm_response_node)
        workflow.add_node("text_to_speech_node", self.nodes.text_to_speech_node)

        # Define entry point.
        workflow.set_entry_point("user_input_node")
        workflow.add_edge("user_input_node", "intent_detection_node")
        # Conditional edges based on current_intent.
        workflow.add_conditional_edges(
            "intent_detection_node",
            lambda state: (
                "memory_query_node"
                if state.get("current_intent", "") in ["FIND_OBJECT", "DESCRIBE_AREA"]
                else "prep_nav_target_coords"
                if state.get("current_intent", "") == "NAVIGATE_TO_COORDS"
                else "action_execution_node"
                if state.get("current_intent", "") == "DIRECT_ACTION"
                else "llm_response_node"
            ),
            {
                "memory_query_node": "memory_query_node",
                "prep_nav_target_coords": "prep_nav_target_coords",
                "action_execution_node": "action_execution_node",
                "llm_response_node": "llm_response_node",
            },
        )
        # After memory_query_node, decide based on query results.
        workflow.add_conditional_edges(
            "memory_query_node",
            lambda state: (
                "prep_nav_target_memory"
                if state.get("memory_query_results")
                and not state.get("requires_clarification")
                else "llm_response_node"
            ),
            {
                "prep_nav_target_memory": "prep_nav_target_memory",
                "llm_response_node": "llm_response_node",
            },
        )
        # Route navigation targets to navigation node.
        workflow.add_edge("prep_nav_target_coords", "navigation_node")
        workflow.add_edge("prep_nav_target_memory", "navigation_node")
        workflow.add_edge("navigation_node", "llm_response_node")
        workflow.add_edge("action_execution_node", "llm_response_node")
        workflow.add_edge("llm_response_node", "text_to_speech_node")
        workflow.add_edge("text_to_speech_node", END)

        self._app = workflow.compile(MemorySaver())

    def display_graph(self) -> str:
        # Display the LangGraph flow as Mermaid diagram.
        return self.app.get_graph().draw_mermaid()

    def invoke(self, audio, extracted_entities, debugMode=False) -> State:
        # Start with an empty AssistanceState
        result_state = self.app.invoke(
            {
                "user_input_audio": audio,
                "extracted_entities": extracted_entities,  # Pass the extracted entities to the flow
            },
            config={"configurable": {"thread_id": "1"}},
            debug=debugMode,
        )
        return result_state


if __name__ == "__main__":
    # from GraphAgent.utils.audio import record_audio

    wf = WorkFlow()
    print(wf.display_graph())
    while True:
        # For demo purposes, the user can trigger the flow by pressing enter.
        input("Press Enter to simulate a new Assistance Mode cycle...")
        # Record audio from microphone and get temporary file path
        # audio = "data/audio/rotate45.wav"  # record_audio()
        final_state = wf.invoke(None, {}, debugMode=True)
        print("\nFinal AssistanceState:")
        print(final_state)
