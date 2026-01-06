from agent.agent import build_agent

def main():
    agent = build_agent()

    print("Physics Agent ready. Type 'exit' to quit.")
    session_id = "default" 

    while True:
        user_input = input("> ")
        if user_input.lower() in {"exit", "quit"}:
            break
        response = agent.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )

        print("\nRobot postdoc:\n", response.content, "\n")

if __name__ == "__main__":
    main()
