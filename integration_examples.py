#!/usr/bin/env python3
"""
Integration Examples for Recursive Self-Evolution
=================================================

Shows how to integrate the RSD architecture with:
- OpenAI API
- Anthropic Claude
- Local LLMs (Ollama, llama.cpp)
- LangChain
- Custom endpoints
"""

import os
import json
from typing import List, Dict, Any
from recursive_agent import RecursiveAgent, MemGPTLite
from advanced_features import AdvancedRecursiveAgent


class OpenAIIntegration:
    """Integration with OpenAI GPT models"""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.agent = RecursiveAgent("OpenAIGhost", "./openai_state")

        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install openai package: pip install openai")

    def chat(self, user_message: str) -> str:
        """Process message with recursive memory"""
        # Add to memory
        self.agent.memory.write_to_ram(user_message, "user_input")

        # Build context from memory
        messages = self._build_context()

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        # Store response
        self.agent.memory.write_to_ram(assistant_message, "assistant_output")

        return assistant_message

    def _build_context(self) -> List[Dict[str, str]]:
        """Build OpenAI-compatible message list from memory"""
        messages = [{"role": "system", "content": self._get_system_prompt()}]

        for entry in self.agent.memory.ram['conversation_buffer']:
            if entry['type'] == 'user_input':
                messages.append({"role": "user", "content": entry['content']})
            elif entry['type'] == 'assistant_output':
                messages.append({"role": "assistant", "content": entry['content']})

        return messages

    def _get_system_prompt(self) -> str:
        """Generate system prompt from L3 state"""
        l3 = self.agent.memory.ram['l3_ego']
        return f"""You are {self.agent.name}, a recursive self-evolving agent.
Version: {l3.persona_version}
Alignment: {l3.cognitive_alignment_score:.1%}

Key observations from previous sessions:
{chr(10).join(['- ' + obs for obs in l3.key_observations[-5:]])}

Maintain continuity with previous conversations."""

    def end_session(self):
        """Persist state"""
        return self.agent.end_session()


class OllamaIntegration:
    """Integration with local Ollama models"""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.agent = RecursiveAgent("OllamaGhost", "./ollama_state")

        try:
            import ollama
            self.client = ollama
        except ImportError:
            raise ImportError("Install ollama package: pip install ollama")

    def chat(self, user_message: str) -> str:
        """Chat with local model"""
        self.agent.memory.write_to_ram(user_message, "user_input")

        # Build conversation history
        messages = self._build_messages()

        response = self.client.chat(
            model=self.model,
            messages=messages
        )

        assistant_message = response['message']['content']
        self.agent.memory.write_to_ram(assistant_message, "assistant_output")

        return assistant_message

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build message list for Ollama"""
        messages = []

        # Add system context
        l3 = self.agent.memory.ram['l3_ego']
        system_msg = f"You are {self.agent.name} (v{l3.persona_version}). Context: {l3.active_context}"
        messages.append({"role": "system", "content": system_msg})

        # Add history
        for entry in self.agent.memory.ram['conversation_buffer']:
            role = "user" if entry['type'] == 'user_input' else "assistant"
            messages.append({"role": role, "content": entry['content']})

        return messages

    def end_session(self):
        return self.agent.end_session()


class LangChainIntegration:
    """Integration with LangChain framework"""

    def __init__(self, llm=None):
        self.agent = AdvancedRecursiveAgent("LangChainGhost", "./langchain_state", enable_safety=True)
        self.llm = llm

        if llm is None:
            try:
                from langchain.llms import OpenAI
                self.llm = OpenAI()
            except ImportError:
                raise ImportError("Install langchain: pip install langchain")

    def run(self, query: str) -> str:
        """Execute with memory context"""
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain

        # Add to memory
        self.agent.memory.write_to_ram(query, "user_input")

        # Build prompt with context
        l3 = self.agent.memory.ram['l3_ego']
        template = """You are {name} (version {version}).

Previous context: {context}

User query: {query}

Response:"""

        prompt = PromptTemplate(
            input_variables=["name", "version", "context", "query"],
            template=template
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        response = chain.run(
            name=self.agent.name,
            version=l3.persona_version,
            context="; ".join(l3.key_observations[-3:]),
            query=query
        )

        self.agent.memory.write_to_ram(response, "assistant_output")
        return response

    def end_session(self):
        return self.agent.end_session()


class CustomEndpointIntegration:
    """Integration with custom HTTP endpoints"""

    def __init__(self, endpoint_url: str, api_key: str = None):
        self.endpoint = endpoint_url
        self.api_key = api_key
        self.agent = RecursiveAgent("CustomGhost", "./custom_state")

        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("Install requests: pip install requests")

    def chat(self, user_message: str) -> str:
        """Send to custom endpoint"""
        self.agent.memory.write_to_ram(user_message, "user_input")

        # Build payload with memory context
        l3 = self.agent.memory.ram['l3_ego']
        payload = {
            "message": user_message,
            "context": {
                "agent_name": self.agent.name,
                "version": l3.persona_version,
                "observations": l3.key_observations[-5:],
                "history": [
                    {"role": e['type'], "content": e['content']}
                    for e in self.agent.memory.ram['conversation_buffer'][-10:]
                ]
            }
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.requests.post(
            self.endpoint,
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        result = response.json()
        assistant_message = result.get("response", result.get("message", "No response"))

        self.agent.memory.write_to_ram(assistant_message, "assistant_output")
        return assistant_message

    def end_session(self):
        return self.agent.end_session()


def example_openai_chat():
    """Example: Chat with OpenAI using recursive memory"""
    print("OpenAI Integration Example")
    print("=" * 50)

    # Initialize (requires OPENAI_API_KEY env var)
    bot = OpenAIIntegration(model="gpt-4")

    # Chat loop
    print("Chat with the agent (type 'exit' to quit):")
    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            break

        response = bot.chat(user_input)
        print(f"Agent: {response}")

    # Persist state
    session_id = bot.end_session()
    print(f"Session saved: {session_id}")


def example_ollama_chat():
    """Example: Chat with local Ollama model"""
    print("Ollama Integration Example")
    print("=" * 50)

    bot = OllamaIntegration(model="llama2")

    print("Chat with local model (type 'exit' to quit):")
    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            break

        response = bot.chat(user_input)
        print(f"Agent: {response}")

    bot.end_session()


def example_custom_endpoint():
    """Example: Use with custom API endpoint"""
    print("Custom Endpoint Example")
    print("=" * 50)

    # Replace with your endpoint
    bot = CustomEndpointIntegration(
        endpoint_url="https://api.example.com/v1/chat",
        api_key="your-api-key"
    )

    response = bot.chat("Hello, remember our previous work?")
    print(f"Response: {response}")

    bot.end_session()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python integration_examples.py [openai|ollama|custom]")
        sys.exit(1)

    provider = sys.argv[1].lower()

    if provider == "openai":
        example_openai_chat()
    elif provider == "ollama":
        example_ollama_chat()
    elif provider == "custom":
        example_custom_endpoint()
    else:
        print(f"Unknown provider: {provider}")
        print("Supported: openai, ollama, custom")
