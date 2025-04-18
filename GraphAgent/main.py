from .core.graph import WorkFlow


def main():
    wf = WorkFlow()
    print(wf.display_graph())
    while True:
        user_input = input("You> ")
        if user_input.lower() == "exit":
            break
        result = wf.invoke(user_input, debugMode=False)
        print("\n\nAI>", end=" ")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
