from .core.graph import WorkFlow
from src.GraphAgent.utils.audio import record_audio


def main():
    wf = WorkFlow()
    print(wf.display_graph())
    while True:
        user_input = record_audio()
        excracted_entities = {}
        result = wf.invoke(user_input, excracted_entities, debugMode=False)
        resp = result.get("llm_response_text") or result.get("final_response_text")
        print(f"\nAI> {resp}")


if __name__ == "__main__":
    main()
