import sys

from app.rag.engine import SamsungChatEngine


def start_chat_cli():
    print("=" * 65)
    print("  SAMSUNG GALAXY AI SPECIFICATION ASSISTANT (Groq RAG)")
    print("=" * 65)
    print("Ask any question about Samsung phones, cameras, chips, or battery.")
    print("Commands: Type 'exit' to quit | 'clear' to reset conversation memory\n")

    try:
        engine = SamsungChatEngine()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("\nAssistant: Goodbye!")
                break

            if user_input.lower() == "clear":
                engine.reset_chat()
                print("\n[Conversation memory cleared]")
                continue

            print("\nAssistant: ", end="", flush=True)
            for token in engine.answer_query_stream(user_input):
                print(token, end="", flush=True)
            print()

        except KeyboardInterrupt:
            print("\n\nSession terminated.")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    start_chat_cli()