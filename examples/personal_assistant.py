#!/usr/bin/env python3
"""Personal Assistant Example - remembers preferences across sessions"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from advanced_features import AdvancedRecursiveAgent

class PersonalAssistant:
    def __init__(self):
        self.agent = AdvancedRecursiveAgent(
            name="PersonalAssistant",
            storage_dir="./pa_state",
            enable_safety=True
        )

    def chat(self):
        print("\n🤖 Personal Assistant (type 'exit' to quit)\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                print("\nSaving state...")
                self.agent.end_session()
                print("Goodbye!")
                break

            response = self.agent.process_input(user_input)
            print(f"\nAssistant: {response}\n")

if __name__ == "__main__":
    assistant = PersonalAssistant()
    assistant.chat()
