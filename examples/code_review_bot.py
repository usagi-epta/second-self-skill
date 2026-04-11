#!/usr/bin/env python3
"""Code Review Bot - learns team standards"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from advanced_features import AdvancedRecursiveAgent
from pathlib import Path as PathLib

class CodeReviewBot:
    def __init__(self, repo_path="."):
        self.repo_path = PathLib(repo_path)
        self.agent = AdvancedRecursiveAgent(
            name="CodeReviewBot",
            storage_dir="./review_state",
            enable_safety=True
        )

    def review_file(self, file_path):
        if not file_path.exists():
            return
        content = file_path.read_text()
        print(f"\n📄 Reviewing: {file_path}")
        review_prompt = f"Review this code:\n\n```\n{content[:1000]}\n```"
        response = self.agent.process_input(review_prompt)
        print(f"{response}\n")

    def review_repo(self):
        py_files = list(self.repo_path.rglob("*.py"))[:5]
        for file_path in py_files:
            self.review_file(file_path)
        self.agent.end_session()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    bot = CodeReviewBot(args.repo)
    bot.review_repo()
