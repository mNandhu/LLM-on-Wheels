from .state import State
from ..config.constants import DEBUG_CONFIG, LLM_MODEL, RESPOND_OR_QUERY_MAX_INVALIDS
from ..config.prompts import (
    decision_prompt_with_history,
    main_conversation_with_history,
    crewai_query_prompt,
)
from ..utils.misc import Colors
from langchain_core.messages import AIMessage
from datetime import datetime


def log_state(state: dict, step: str) -> None:
    """Log the current state of the workflow"""
    if DEBUG_CONFIG["SHOW_STATE_CHANGES"]:
        print(f"\n{Colors.HEADER}=== State at {step} ==={Colors.ENDC}")
        for key, value in state.items():
            print(f"{Colors.BLUE}{key}:{Colors.ENDC} {value}")


def get_chat_groq():
    """Initialize the ChatGroq model"""
    from langchain_groq import ChatGroq

    if DEBUG_CONFIG["SHOW_TIMING"]:
        print(f"{Colors.YELLOW}Initializing ChatGroq...{Colors.ENDC}")
    return ChatGroq(model=LLM_MODEL)


def get_crew():
    class Crew:
        def __init__(self):
            if DEBUG_CONFIG["SHOW_TIMING"]:
                print(f"{Colors.YELLOW}Initializing CrewAI...{Colors.ENDC}")

        def process_query(self, query: str) -> str:
            # Dummy implementation for CrewAI query processing
            print(f"{Colors.BLUE}Processing CrewAI query...{Colors.ENDC}")
            return f"Processed CrewAI query: {query}"

    return Crew()


def crewai_query(query: str) -> str:
    try:
        if DEBUG_CONFIG["SHOW_CREWAI_DETAILS"]:
            print(f"{Colors.BLUE}CrewAI Query:{Colors.ENDC} {query}")
        crew = get_crew()
        response = crew.process_query(query)
        if DEBUG_CONFIG["SHOW_CREWAI_DETAILS"]:
            print(f"{Colors.GREEN}CrewAI Response:{Colors.ENDC} {response}")
        return response
    except Exception as e:
        print(f"{Colors.RED}Error querying CrewAI: {str(e)}{Colors.ENDC}")
        return f"Error querying CrewAI: {str(e)}"


class Nodes:
    def __init__(self):
        self._chat_llm = None
        if DEBUG_CONFIG["SHOW_TIMING"]:
            print(f"{Colors.YELLOW}Initializing Nodes...{Colors.ENDC}")

    @property
    def chat(self):
        if self._chat_llm is None:
            self._chat_llm = get_chat_groq()
        return self._chat_llm

    def respond_or_query(self, state: State) -> State:
        if DEBUG_CONFIG["SHOW_STATE_CHANGES"]:
            print(f"\n{Colors.HEADER}=== Entering respond_or_query ==={Colors.ENDC}")

        start_time = datetime.now()

        previous_responses = state.get("database_agent_responses", [])
        formatted_responses = "\n".join(
            [f"{i + 1}. {resp}" for i, resp in enumerate(previous_responses)]
        )

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prompt = decision_prompt_with_history

        chain = prompt | self.chat

        history = state.get("chat_history", [])

        decision = chain.invoke(
            {
                "input": state["messages"][-1].content,
                "invalid_count": state.get("invalid_decision_count", 0),
                "database_agent_responses": formatted_responses
                if previous_responses
                else "None.",
                "history": history,
                "current_time": current_time,
                "RESPOND_OR_QUERY_MAX_INVALIDS": RESPOND_OR_QUERY_MAX_INVALIDS,
            }  # Add current_time to the template variables
        )

        decision_content = decision.content.strip(" \n\t'.\"\\{}()/").lower()

        invalid_decision_count = 0
        print(
            decision_content,
            f"\\Invalid Count: {state.get('invalid_decision_count', 0)}",
        )

        if decision_content.startswith("query") or "query" in decision_content[:20]:
            decision_content = "query"
        elif (
            decision_content.startswith("respond")
            or "respond" in decision_content[:20]
            or state.get("invalid_decision_count", 0) > RESPOND_OR_QUERY_MAX_INVALIDS
        ):
            decision_content = "respond"
        else:
            decision_content = "invalid"
            invalid_decision_count = state.get("invalid_decision_count", 0) + 1

        print("Task Decision: ", decision_content)

        if DEBUG_CONFIG["SHOW_TIMING"]:
            duration = (datetime.now() - start_time).total_seconds()
            print(
                f"{Colors.YELLOW}respond_or_query duration: {duration:.2f}s{Colors.ENDC}"
            )

        if DEBUG_CONFIG["SHOW_DECISION_PROCESS"]:
            print(f"{Colors.GREEN}Decision:{Colors.ENDC} {decision_content}")

        return {
            "task_decision": decision_content,
            "invalid_decision_count": invalid_decision_count,
        }

    def crewai_query(self, state: State) -> State:
        if DEBUG_CONFIG["SHOW_STATE_CHANGES"]:
            print(f"\n{Colors.HEADER}=== Entering crewai_query ==={Colors.ENDC}")

        start_time = datetime.now()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("CrewAI Query")
        try:
            prompt = crewai_query_prompt
            chain = prompt | self.chat
            result = chain.invoke(
                {
                    "input": state["messages"][-1].content,
                    "database_agent_responses": state.get(
                        "database_agent_responses", ["No previous context"]
                    ),
                    "current_time": current_time,
                }
            )

            responses = state.get("database_agent_responses", [])
            crew_response = crewai_query(result.content)
            responses.append(crew_response)
            if DEBUG_CONFIG["SHOW_TIMING"]:
                duration = (datetime.now() - start_time).total_seconds()
                print(
                    f"{Colors.YELLOW}crewai_query duration: {duration:.2f}s{Colors.ENDC}"
                )

            return {"database_agent_responses": responses}
        except Exception as e:
            print(f"Error querying CrewAI: {str(e)}")
            return {"database_agent_responses": [f"Error: {str(e)}"]}

    def main_conversation(self, state: State) -> State:
        if DEBUG_CONFIG["SHOW_STATE_CHANGES"]:
            print(f"\n{Colors.HEADER}=== Entering main_conversation ==={Colors.ENDC}")

        start_time = datetime.now()
        # Format all responses as a numbered list
        responses = state.get("database_agent_responses", [])
        formatted_responses = "\n".join(
            [f"{i + 1}. {resp}" for i, resp in enumerate(responses)]
        )
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = main_conversation_with_history

        history = state.get("chat_history", [])
        current_message = state["messages"][-1]

        chain = prompt | self.chat
        response = chain.invoke(
            {
                "input": current_message.content,
                "database_agent_responses": formatted_responses
                if responses
                else "No additional information available.",
                "history": history,
                "current_time": current_time,
            }
        )

        ai_message = AIMessage(content=response.content)
        updated_history = history + [ai_message]

        if DEBUG_CONFIG["SHOW_TIMING"]:
            duration = (datetime.now() - start_time).total_seconds()
            print(
                f"{Colors.YELLOW}main_conversation duration: {duration:.2f}s{Colors.ENDC}"
            )

        return {"messages": [ai_message], "chat_history": updated_history}
