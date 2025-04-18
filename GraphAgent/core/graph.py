from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from .state import State
from .nodes import Nodes
from ..config.prompts import SYSTEM_PROMPT
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


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

        # Add nodes
        workflow.add_node("respond_or_query", self.nodes.respond_or_query)
        workflow.add_node("crewai_agent_query", self.nodes.crewai_query)
        workflow.add_node("main_conversation", self.nodes.main_conversation)

        # Add edges
        workflow.set_entry_point("respond_or_query")
        workflow.add_conditional_edges(
            "respond_or_query",
            lambda x: "crewai_agent_query"
            if x["task_decision"] == "query"
            else (
                "main_conversation"
                if x["task_decision"] == "respond"
                else "respond_or_query"
            ),
            {
                "crewai_agent_query": "crewai_agent_query",
                "main_conversation": "main_conversation",
                "respond_or_query": "respond_or_query",
            },
        )
        workflow.add_edge("crewai_agent_query", "main_conversation")
        workflow.add_edge("main_conversation", END)

        self._app = workflow.compile(MemorySaver())

    def display_graph(self) -> str:
        return self.app.get_graph().draw_mermaid()

    def invoke(self, user_input: str, debugMode=False) -> dict:
        if isinstance(user_input, str):
            message = HumanMessage(content=user_input)
        else:
            message = user_input

        self.chat_history.append(message)

        result = self.app.invoke(
            {
                "messages": [message],  # Only pass the current message
                "chat_history": self.chat_history,  # Pass the full history
            },
            config={"configurable": {"thread_id": "1"}},
            debug=debugMode,
        )

        if "chat_history" in result:
            self.chat_history = result["chat_history"]

        return result

    def clear(self):
        self.chat_history = []

    def set_chat_history(self, chat_history: list) -> None:
        """Set the chat history for the workflow."""
        self.chat_history = chat_history


if __name__ == "__main__":
    wf = WorkFlow()
    print(wf.display_graph())
    while True:
        result = wf.invoke(input("You: "), debugMode=False)
        print("\n\nFinal result:")
        print(result["messages"][-1].content)
        print("\n\n")
