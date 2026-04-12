# Recursive Self-Ghost
**Recursive Self-Ghost** is a specialised orchestration skill designed for autonomous agent evolution and persistent memory management. This repository focuses on the core skill logic, mutation algorithms, and session history required to maintain a recursive agentic loop.
## Project Overview
The project facilitates a "ghost-in-the-shell" style recursive architecture where the agent can mutate its own operational parameters based on session history and long-term memory. It is built to be modular, allowing for various bot implementations such as personal assistants or code review tools.
### Key Features
 * **Recursive Agent Logic**: Implements a self-referential loop that allows the agent to process its own output as new input.
 * **Mutation Algorithm**: Utilises a dedicated algorithm to evolve agent behaviour over time, preventing logic stagnation.
 * **Persistent Memory**: Manages state through a structured JSON memory system, ensuring the agent "remembers" across different sessions.
 * **Architecture Decision Records (ADRs)**: Includes a full history of design choices to track the evolution of the system's logic.
## Repository Structure
This repository is organised into functional modules for easy navigation and extension:
 * **examples/**: Ready-to-use implementations of the ghost skill.
   * personal_assistant.py: A foundational implementation for a general-purpose AI assistant.
   * code_review_bot.py: A specialised bot designed to analyse and suggest improvements for codebases.
 * **references/**: Technical documentation and schemas.
   * mutation_algorithm.md: Detailed breakdown of how the self-evolution logic functions.
   * memories_schema.md: The structural definition for the memories.json file.
 * **session_history/**: Historical logs of previous agent executions used for recursive training and context.
 * **SKILL.md**: The primary skill definition and entry point for the orchestration engine.
 * **memories.json**: The current global state and long-term memory storage for the agent.
 * **ADRs.md**: Documentation of significant architectural decisions made during development.

## Getting Started
### Prerequisites
As this is an advanced agentic system, you will need a basic Python environment and an orchestration engine (such as a local LLM cluster) to run the .skill definitions.
### Installation
 1. **Clone the Repository**:
   ```bash
   git clone https://github.com/usagi-epta/recursive-self-ghost.git
   ```
 2. **Initialise Memory**:
   Ensure memories.json is present in the root directory. If it is empty, the agent will begin its first "incarnation" from a blank state.
## Usage
To see the Recursive Self-Ghost in action, you can run one of the provided examples:
 * **Personal Assistant**: Navigate to the examples folder and run the assistant script to start a session that saves to your local memory.
 * **Code Review**: Point the code_review_bot.py at a target directory to receive autonomous feedback based on the ghost's evolving logic.
> [!NOTE]
> All session data is automatically recorded in the session_history/ directory to facilitate recursive improvement in future runs.
> 
## Documentation
For a deep dive into the mechanics of this project, please refer to the following:
 * **Evolution Logic**: See references/mutation_algorithm.md.
 * **Data Structure**: See references/memories_schema.md.
 * **Design History**: See ADRs.md for why certain architectural paths were chosen.
