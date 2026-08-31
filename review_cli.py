import sys
from app.agents.workflow import SamsungReviewOrchestrator


def main():
    print("=" * 70)
    print("  SAMSUNG MULTI-AGENT SPECIFICATION & REVIEW SYSTEM (LangChain + Groq)")
    print("=" * 70)
    print("Agents Active:")
    print("  1. [SpecRetrievalAgent]   -> Queries DB/Vector store")
    print("  2. [ReviewGenerationAgent] -> Streams real-time editorial reviews\n")

    orchestrator = SamsungReviewOrchestrator()

    while True:
        try:
            phone_input = input("Enter Samsung Phone Model (e.g. 'Galaxy S23 Ultra' or 'exit'): ").strip()

            if not phone_input or phone_input.lower() in ("exit", "quit"):
                print("Exiting review system.")
                break

            focus_input = input("Custom Review Focus (press Enter for default): ").strip()

            if not focus_input:
                focus_input = "General Consumer & Performance Review"

            print("\n[1/2] Spec Agent querying database and building dossier...")

            spec_dossier, review_stream = orchestrator.stream_phone_review(phone_name=phone_input, review_focus=focus_input)

            print("\n" + "=" * 30 + " TECHNICAL DOSSIER " + "=" * 30)
            print(spec_dossier)

            print("\n" + "=" * 30 + " EDITORIAL REVIEW (LIVE) " + "=" * 30 + "\n")

            # Stream each generated token directly to terminal
            for token in review_stream:
                sys.stdout.write(token)
                sys.stdout.flush()

            print("\n\n" + "=" * 78 + "\n")

        except KeyboardInterrupt:
            print("\nSession aborted.")
            break
        except Exception as e:
            print(f"\nPipeline Error: {e}\n")


if __name__ == "__main__":
    main()