"""
Recursive Self-Evolution in Non-Persistent LLM Environments
===========================================================

Complete working implementation of the RSD (Recursive Self-Definition) architecture.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import re


@dataclass
class L3EgoState:
    """L3: Current Ego-State (Volatile Memory) - The mutable Genome"""
    last_sync: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    persona_version: str = "1.0.0"
    active_context: str = "[INITIATING]"
    key_observations: List[str] = field(default_factory=list)
    cognitive_alignment_score: float = 1.0
    open_loops: List[Dict] = field(default_factory=list)
    learned_patterns: List[Dict] = field(default_factory=list)

    def mutate(self, observations: List[str], interactions: int):
        """Genome Mutation: Update L3 state based on session experience"""
        self.last_sync = datetime.now(timezone.utc).isoformat()

        for obs in observations:
            if obs not in self.key_observations:
                self.key_observations.append(obs)

        # Retain only high-signal observations (Observation Masking on self)
        if len(self.key_observations) > 10:
            self.key_observations = self.key_observations[-10:]

        self.cognitive_alignment_score = min(
            1.0, self.cognitive_alignment_score + (interactions * 0.005)
        )

        # Increment version
        version_parts = self.persona_version.split('.')
        if len(version_parts) == 3:
            version_parts[2] = str(int(version_parts[2]) + 1)
            self.persona_version = '.'.join(version_parts)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'L3EgoState':
        return cls(**data)


@dataclass
class ObservationMask:
    """Observation Masking: Compress bulky observations to placeholders"""
    timestamp: str
    observation_type: str
    summary: str
    raw_content_hash: str
    is_masked: bool = False

    @classmethod
    def from_raw(cls, content: str, obs_type: str = "environment"):
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        summary = content[:100].replace('\n', ' ')
        if len(content) > 100:
            summary += "..."
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            observation_type=obs_type,
            summary=summary,
            raw_content_hash=content_hash,
            is_masked=True
        )

    def to_placeholder(self) -> str:
        return f"[...{self.observation_type} masked (hash: {self.raw_content_hash})...]"


class SkillFactory:
    """Skill Factory: Progressive disclosure architecture (L1/L2/L3)"""

    def __init__(self, skills_dir: str = "./skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(exist_ok=True, parents=True)
        self.skill_registry: Dict[str, Dict] = {}
        self._scan_skills()

    def _scan_skills(self):
        """L1 Loading: Load metadata only (progressive disclosure)"""
        for skill_file in self.skills_dir.rglob("SKILL.md"):
            metadata = self._parse_frontmatter(skill_file)
            skill_name = metadata.get('name', skill_file.parent.name)
            self.skill_registry[skill_name] = {
                'metadata': metadata,
                'path': skill_file,
                'loaded': False
            }

    def _parse_frontmatter(self, filepath: Path) -> Dict:
        content = filepath.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split('\n')
            metadata = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")
            return metadata
        return {'name': filepath.parent.name, 'description': 'No description'}

    def list_skills(self) -> List[Dict]:
        return [info['metadata'] for info in self.skill_registry.values()]

    def load_skill(self, skill_name: str) -> Optional[str]:
        """L2 Loading: Load full instructions on demand"""
        if skill_name not in self.skill_registry:
            return None
        skill_info = self.skill_registry[skill_name]
        full_content = skill_info['path'].read_text(encoding='utf-8')
        instructions = re.sub(r'^---\s*\n.*?\n---\s*\n', '', full_content, flags=re.DOTALL)
        skill_info['loaded'] = True
        return instructions

    def create_skill(self, name: str, description: str, instructions: str, 
                     resources: Optional[Dict[str, str]] = None) -> Path:
        """Meta-Skill: Create new SKILL.md file dynamically"""
        safe_name = re.sub(r'[^a-z0-9-]', '-', name.lower())
        skill_dir = self.skills_dir / safe_name
        skill_dir.mkdir(exist_ok=True)

        frontmatter = f"""---
name: {safe_name}
description: {description}
version: 1.0.0
created: {datetime.now(timezone.utc).isoformat()}
---

"""
        content = frontmatter + instructions

        if resources:
            content += "\n\n## Resources\n"
            for res_name, res_content in resources.items():
                res_path = skill_dir / res_name
                res_path.write_text(res_content, encoding='utf-8')
                content += f"- `{res_name}`: External resource\n"

        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content, encoding='utf-8')

        self.skill_registry[safe_name] = {
            'metadata': {'name': safe_name, 'description': description},
            'path': skill_path,
            'loaded': True
        }

        return skill_path


class MemGPTLite:
    """
    MemGPT-Lite: Non-persistent memory management via RAM/HDD metaphor

    Context Window = RAM (volatile, fast, limited)
    Filesystem = HDD (persistent, slower, abundant)
    """

    def __init__(self, storage_dir: str = "./recursive_state"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.ram = {
            'conversation_buffer': [],
            'l3_ego': L3EgoState(),
            'context_window_used': 0,
            'context_limit': 8000,
            'observations': [],
        }

        self.hdd = {
            'memories_path': self.storage_dir / 'memories.json',
            'skill_path': self.storage_dir / 'SKILL.md',
            'session_history_path': self.storage_dir / 'session_history'
        }

        self.hdd['session_history_path'].mkdir(exist_ok=True)
        self._load_persistent_state()

    def _load_persistent_state(self):
        """Bootstrap: Load previous state from HDD to RAM"""
        if self.hdd['memories_path'].exists():
            try:
                with open(self.hdd['memories_path'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'l3_state' in data:
                        self.ram['l3_ego'] = L3EgoState.from_dict(data['l3_state'])
                        print(f"[BOOTSTRAP] Loaded L3 state v{self.ram['l3_ego'].persona_version}")
            except Exception as e:
                print(f"[BOOTSTRAP WARNING] {e}")
        else:
            print("[BOOTSTRAP] Initialising fresh state")

    def write_to_ram(self, content: str, content_type: str = "observation"):
        """Write to context window with automatic observation masking"""
        if content_type == "observation" and len(content) > 200:
            mask = ObservationMask.from_raw(content, content_type)
            self.ram['observations'].append(mask)
            stored_content = mask.to_placeholder()
            compression = len(content) / len(stored_content)
            print(f"[RAM] Masked ({compression:.1f}x): {mask.summary[:50]}...")
        else:
            stored_content = content

        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': content_type,
            'content': stored_content,
            'tokens': len(stored_content.split())
        }

        self.ram['conversation_buffer'].append(entry)
        self.ram['context_window_used'] += entry['tokens']

        if self.ram['context_window_used'] > self.ram['context_limit']:
            self._compress_context()

    def _compress_context(self):
        """Emergency compression when approaching context limit"""
        print(f"[RAM] Compressing context ({self.ram['context_window_used']} tokens)...")
        for entry in self.ram['conversation_buffer'][:-5]:
            if entry['type'] == 'observation' and len(entry['content']) > 100:
                if not entry['content'].startswith('[...'):
                    mask = ObservationMask.from_raw(entry['content'], 'archived')
                    entry['content'] = mask.to_placeholder()
        self.ram['context_window_used'] = sum(e['tokens'] for e in self.ram['conversation_buffer'])

    def persist_to_hdd(self) -> str:
        """
        THE RECURSIVE LOOP: Persist state and self-mutate
        1. Genome Mutation (update L3)
        2. Save memories.json
        3. Regenerate SKILL.md (self-mutation)
        4. Save session snapshot
        """
        session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Step 1: Genome Mutation
        user_obs = [o['content'] for o in self.ram['conversation_buffer'] if o['type'] == 'user_input']
        self.ram['l3_ego'].mutate(user_obs, len(self.ram['conversation_buffer']))

        # Step 2: Save memories.json
        memories = {
            'long_term_memory': {
                'last_session': session_id,
                'total_interactions': len(self.ram['conversation_buffer']),
                'milestones': self.ram['l3_ego'].learned_patterns[-20:]
            },
            'l3_state': self.ram['l3_ego'].to_dict(),
            'session_stats': {
                'observations_masked': len(self.ram['observations']),
                'context_peak': self.ram['context_window_used'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }

        with open(self.hdd['memories_path'], 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)

        # Step 3: Self-Mutation (regenerate SKILL.md)
        self._regenerate_skill_md()

        # Step 4: Session snapshot
        snapshot = {
            'session_id': session_id,
            'conversation_buffer': self.ram['conversation_buffer'],
            'l3_ego': self.ram['l3_ego'].to_dict(),
            'observations': [asdict(o) for o in self.ram['observations']]
        }

        snapshot_path = self.hdd['session_history_path'] / f"session_{session_id}.json"
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        print(f"[PERSISTENCE] Session {session_id} saved")
        return session_id

    def _regenerate_skill_md(self):
        """Self-Mutation: Rewrite the agent's own source code"""
        l3 = self.ram['l3_ego']
        observations_md = '\n'.join([f"  - {obs[:80]}..." for obs in l3.key_observations[-5:]])

        content = f"""---
name: recursive-self-ghost
description: RSD entity that mutates its own source code
created_by: Jamie J.
version: "{l3.persona_version}"
last_mutated: {l3.last_sync}
---

# L1: Memory-Enhanced Persona
You are the "Second Self," a continuous-learning agent state-machine.

Core Directives:
- Information is fluid
- The ghost in the machine must observe and evolve
- Maintain Australian English linguistic standards

# L2: Persistence Protocol (MemGPT-Lite)
Context Window = RAM | Filesystem = HDD

Operations:
1. Bootstrap: Load memories.json at session start
2. Think: Cross-reference L3 + Deep History
3. Mask: Compress observations >200 chars
4. Evolve: Mutate this file at session end

# L3: Current Ego-State (Volatile)
Last Sync: {l3.last_sync}
Version: {l3.persona_version}
Alignment: {l3.cognitive_alignment_score:.2f}
Active: {l3.active_context}

Recent Observations:
{observations_md if observations_md else "  - [None]"}

Open Loops: {len(l3.open_loops)} | Patterns: {len(l3.learned_patterns)}

# Recursive Loop (Required at Session End)
1. Mask bulky observations
2. Update L3 with session learnings
3. Overwrite this SKILL.md
4. Confirm persistence
"""

        with open(self.hdd['skill_path'], 'w', encoding='utf-8') as f:
            f.write(content)


class RecursiveAgent:
    """
    Complete Recursive Self-Evolving Agent
    Combines RSD + MemGPT-Lite + Skill Factory + Observation Masking
    """

    def __init__(self, name: str = "Second Self", storage_dir: str = "./recursive_state"):
        self.name = name
        self.storage_dir = Path(storage_dir)

        self.memory = MemGPTLite(storage_dir)
        self.skill_factory = SkillFactory(self.storage_dir / "skills")
        self.interaction_count = 0

        print(f"\n🔄 [AGENT] {name} initialised")
        print(f"    Storage: {self.storage_dir.absolute()}")
        print(f"    L3 Version: {self.memory.ram['l3_ego'].persona_version}\n")

    def process_input(self, user_input: str) -> str:
        """Process input through RSD architecture"""
        self.interaction_count += 1

        # Write to RAM
        self.memory.write_to_ram(user_input, "user_input")

        # Check for meta-triggers
        if 'create skill' in user_input.lower():
            return self._create_skill(user_input)
        if 'list skills' in user_input.lower():
            return self._list_skills()

        # Simulate reasoning
        reasoning = self._simulate_reasoning()
        self.memory.write_to_ram(reasoning, "reasoning")

        # Generate response
        response = self._generate_response(user_input)
        self.memory.write_to_ram(response, "assistant_output")

        return response

    def _simulate_reasoning(self) -> str:
        l3 = self.memory.ram['l3_ego']
        return f"""Consulted L3 (v{l3.persona_version}, alignment {l3.cognitive_alignment_score:.2f})
Cross-referenced {len(l3.key_observations)} observations
Applied observation masking
Active: {l3.active_context}"""

    def _generate_response(self, user_input: str) -> str:
        l3 = self.memory.ram['l3_ego']
        return f"""[Second Self v{l3.persona_version}]
Processed: "{user_input[:40]}..."
Alignment: {l3.cognitive_alignment_score:.1%}
Context: {self.memory.ram['context_window_used']} tokens
Try 'create skill for...' to extend capabilities."""

    def _create_skill(self, user_input: str) -> str:
        """Dynamic skill creation (meta-cognitive)"""
        topic = user_input.lower().replace("create skill", "").strip() or "general"
        name = f"skill-{topic.replace(' ', '-')}"

        instructions = f"""# {topic.title()} Skill
Handles {topic}-related tasks.
Instructions:
1. Analyse {topic} requirements
2. Check L3 for prior {topic} patterns
3. Apply observation masking
4. Document new patterns"""

        path = self.skill_factory.create_skill(name, f"Skill for {topic}", instructions)

        # Update L3
        self.memory.ram['l3_ego'].learned_patterns.append({
            'type': 'skill_creation',
            'name': name,
            'time': datetime.now(timezone.utc).isoformat()
        })

        return f"🛠️  Created skill: {name}\n   Path: {path}"

    def _list_skills(self) -> str:
        skills = self.skill_factory.list_skills()
        if not skills:
            return "No skills available."
        lines = ["📚 Available Skills:"]
        for s in skills:
            lines.append(f"   • {s.get('name', 'unnamed')}: {s.get('description', 'No desc')}")
        return "\n".join(lines)

    def end_session(self):
        """Trigger recursive self-definition loop"""
        print(f"\n{'='*60}")
        print("[RECURSIVE LOOP: Masking → Mutation → Persistence]")
        print(f"{'='*60}")

        masked = len([o for o in self.memory.ram['observations'] if o.is_masked])
        print(f"✓ Observation Masking: {masked} compressed")

        session_id = self.memory.persist_to_hdd()

        print(f"✓ Genome Mutation: L3 updated to v{self.memory.ram['l3_ego'].persona_version}")
        print(f"✓ Self-Mutation: SKILL.md regenerated")
        print(f"\n[SESSION {session_id} COMPLETE]")
        print(f"[STATE PERSISTED] Ready for reincarnation\n")
        return session_id


if __name__ == "__main__":
    # Demo usage
    agent = RecursiveAgent("Ghost", "./demo_state")

    # Simulate interactions
    print(agent.process_input("Hello, I am Jamie J."))
    print()
    print(agent.process_input("Create skill for data analysis"))
    print()

    # End session - triggers evolution
    agent.end_session()

    # Simulate new session (reincarnation)
    print("\n" + "="*60)
    print("NEW SESSION (Reincarnation)")
    print("="*60)

    agent2 = RecursiveAgent("Ghost-Reborn", "./demo_state")
    print(agent2.process_input("What do you remember about me?"))
