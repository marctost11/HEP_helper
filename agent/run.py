import sys
from pathlib import Path
import os
import argparse

# Add project root to path to allow imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    parser = argparse.ArgumentParser(description="HEP_helper agent")
    parser.add_argument(
        "--no-examples",
        action="store_true",
        help="Disable loading markdown example context files into the system prompt.",
    )
    parser.add_argument(
        "--examples-dir",
        default="examples/hep-programming-hints",
        help="Directory (relative to project root) containing markdown examples.",
    )
    parser.add_argument(
        "--examples-max-chars",
        type=int,
        default=20000,
        help="Maximum characters of examples to inject into the system prompt.",
    )
    args = parser.parse_args()

    # Expose to prompt builder / graph via env vars
    os.environ["HEP_USE_EXAMPLES"] = "0" if args.no_examples else "1"
    os.environ["HEP_EXAMPLES_DIR"] = args.examples_dir
    os.environ["HEP_EXAMPLES_MAX_CHARS"] = str(args.examples_max_chars)

    # Import after args/env are set so prompt defaults reflect CLI.
    from agent.agent import build_agent
    from langchain_core.messages import HumanMessage

    # Optional: print exactly which example files are being injected into the system prompt.
    # Enable via: HEP_DEBUG_CONTEXT=1 python -m agent.run
    if os.getenv("HEP_DEBUG_CONTEXT") == "1":
        try:
            from agent.context_debug import get_examples_manifest, format_examples_manifest
            from agent.prompts import get_system_prompt

            # Mirror current default behavior
            examples_dir = args.examples_dir
            max_chars = args.examples_max_chars

            if args.no_examples:
                print("Examples injection: DISABLED (--no-examples)")
            else:
                print("Examples injection: ENABLED")
                manifest = get_examples_manifest(examples_dir=examples_dir, max_chars=max_chars)
                print(format_examples_manifest(manifest))
            print("")
            print(
                "System prompt chars: "
                + str(
                    len(
                        get_system_prompt(
                            examples_dir=examples_dir,
                            max_chars=max_chars,
                            include_examples=not args.no_examples,
                        )
                    )
                )
            )
            print("-" * 60)
        except Exception as e:
            print(f"Warning: could not print context manifest: {e}")

    agent = build_agent(use_graph=True)

    print("=" * 60)
    print("Physics Agent with LangGraph Workflow")
    print("=" * 60)
    print("\nWorkflow phases:")
    print("  1. Planning - Gather requirements")
    print("  2. Code Generation - Create executable code")
    print("  3. Import Check - Verify required modules exist")
    print("  4. Testing - Syntax check (no execution)")
    print("  5. Complete - Deliver ready-to-run code")
    print("\nType 'exit' to quit.\n")
    
    thread_id = "default"

    while True:
        user_input = input("> ")
        if user_input.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            # Invoke the graph with a human message
            config = {"configurable": {"thread_id": thread_id}}
            
            # Get current state to check phase
            try:
                state = agent.get_state(config)
                current_phase = state.values.get("phase", "planning") if state.values else "planning"
                if current_phase:
                    print(f"\n[Phase: {current_phase.upper().replace('_', ' ')}]")
            except (AttributeError, Exception):
                # get_state might not be available
                pass
            
            # Invoke with the user's input
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # Extract the last AI message for display
            if result and "messages" in result:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"\n{last_message.content}\n")
                else:
                    print(f"\n{last_message}\n")
            
            # Check if we're complete
            try:
                final_state = agent.get_state(config)
                if final_state.values and final_state.values.get("phase") == "complete":
                    print("\n" + "=" * 60)
                    print("✅ CODE GENERATION COMPLETE")
                    print("=" * 60)
                    if final_state.values.get("generated_code"):
                        print("\nFinal Code:")
                        print("-" * 60)
                        print(final_state.values["generated_code"])
                        print("-" * 60)
                    print("\nReady for next task. Type your request or 'exit' to quit.\n")
            except AttributeError:
                # get_state might not be available in all graph implementations
                pass
                
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
