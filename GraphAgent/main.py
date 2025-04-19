from .core.graph import WorkFlow
from GraphAgent.utils.audio import record_audio

def main():
    wf = WorkFlow()
    print(wf.display_graph())
    while True:
        user_input = record_audio()
        excracted_entities = {}
        result = wf.invoke(user_input,excracted_entities, debugMode=False)
        print("\n\nAI>", end=" ")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
