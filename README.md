# Second-Self 

#agent-skill #persona #digital-entity

## Overview
This directory contains the architecture for a persistent, evolving digital entity compatible with Google AI Edge Gallery Agent Skills. 

It is divided into two primary nodes:

* **Workspace:** The static framework dictating the entity's personality, ethics, and voice.
* **Evolution:** The dynamic memory banks where the entity records interactions, updates preferences, and tracks its own growth over time.
* **Scripts:** The file implementing the Level 3 execution logic, acting as the nexus between the Gemma 4 reasoning engine and the device's native storage.

## Layout

```
second-self/
├── SKILL.md
├── README.md
├── scripts/
│   └── index.html
├── workspace/
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── BOOTSTRAP.md
│   └── VOICE.md
└── evolution/
    ├── hooks.json
    ├── evolution_history.jsonl
    ├── capsules.json
    ├── goals.json
    ├── events.jsonl
    ├── genes.json
    ├── identity_overrides.json
    └── preferences.json
```
## Credits

Initial inspiration credit goes to the following skill repos:

[AIEdgeGallerySkill:persona](https://github.com/khimaros/eai-skills/tree/master/persona)
[AIEdgeGallerySkill:second-brain](https://github.com/uussnn/second-brain)

### LLM Workhorse

Kimi K2.5 Thinking | Claude Sonnet 4.6 Thinking | DeepSeek-V3.2-Exp-Think | Gemini 3 Thinking & Pro | ChatGPT 5.4 Thinking & Codex
