#!/usr/bin/env python3
"""
Recursive Self-Evolution CLI
============================

Command-line interface for managing recursive agents with full
session persistence, skill management, and safety controls.

Usage:
    python cli.py --init --name MyAgent
    python cli.py --chat --name MyAgent
    python cli.py --skills --name MyAgent
    python cli.py --export --name MyAgent --format json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Import our architecture
from recursive_agent import RecursiveAgent
from advanced_features import AdvancedRecursiveAgent


class RecursiveCLI:
    """Command-line interface for recursive agent management"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Recursive Self-Evolution Agent CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --init --name Ghost --safety
  %(prog)s --chat --name Ghost --session "morning-session"
  %(prog)s --skills --name Ghost --create "security audit"
  %(prog)s --export --name Ghost --format markdown
            """
        )
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument('--name', '-n', required=True,
                               help='Agent name (identity)')
        self.parser.add_argument('--storage', '-s', default='./agent_state',
                               help='Storage directory (default: ./agent_state)')

        # Commands
        commands = self.parser.add_mutually_exclusive_group(required=True)
        commands.add_argument('--init', action='store_true',
                            help='Initialize new agent')
        commands.add_argument('--chat', action='store_true',
                            help='Start interactive chat session')
        commands.add_argument('--skills', action='store_true',
                            help='Manage skills')
        commands.add_argument('--export', action='store_true',
                            help='Export agent state')
        commands.add_argument('--import-state', metavar='FILE',
                            help='Import agent state from file')
        commands.add_argument('--verify', action='store_true',
                            help='Run safety verification')

        # Options
        self.parser.add_argument('--safety', action='store_true',
                               help='Enable SafeClaw-R safety framework')
        self.parser.add_argument('--session', metavar='NAME',
                               help='Session identifier')
        self.parser.add_argument('--format', choices=['json', 'markdown', 'yaml'],
                               default='json', help='Export format')
        self.parser.add_argument('--create', metavar='DESCRIPTION',
                               help='Create new skill (use with --skills)')
        self.parser.add_argument('--list', action='store_true',
                               help='List all skills')

    def run(self):
        args = self.parser.parse_args()

        try:
            if args.init:
                self._cmd_init(args)
            elif args.chat:
                self._cmd_chat(args)
            elif args.skills:
                self._cmd_skills(args)
            elif args.export:
                self._cmd_export(args)
            elif args.import_state:
                self._cmd_import(args)
            elif args.verify:
                self._cmd_verify(args)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)

    def _cmd_init(self, args):
        """Initialize new agent"""
        print(f"🚀 Initializing agent: {args.name}")
        print(f"   Storage: {args.storage}")
        print(f"   Safety: {'Enabled' if args.safety else 'Disabled'}")

        if args.safety:
            agent = AdvancedRecursiveAgent(args.name, args.storage, enable_safety=True)
        else:
            agent = RecursiveAgent(args.name, args.storage)

        # Create initial session
        session_id = agent.end_session()

        print(f"\n✅ Agent '{args.name}' initialized successfully")
        print(f"   Session ID: {session_id}")
        print(f"\nNext steps:")
        print(f"   python cli.py --chat --name {args.name}")

    def _cmd_chat(self, args):
        """Interactive chat session"""
        print(f"🔄 Starting chat with: {args.name}")
        if args.session:
            print(f"   Session: {args.session}")

        # Load agent
        agent = RecursiveAgent(args.name, args.storage)

        print("\n💡 Tips:")
        print("   • Type 'exit' or 'quit' to end session")
        print("   • Type 'create skill for...' to add capabilities")
        print("   • Type 'status' to see current state")
        print("   • Press Ctrl+C to force quit (state will be lost!)\n")

        try:
            while True:
                try:
                    user_input = input(f"\n[{args.name}] > ").strip()

                    if not user_input:
                        continue

                    if user_input.lower() in ['exit', 'quit']:
                        print("\n🔄 Ending session and persisting state...")
                        session_id = agent.end_session()
                        print(f"\n✅ Session {session_id} saved. Goodbye!")
                        break

                    if user_input.lower() == 'status':
                        self._show_status(agent)
                        continue

                    # Process input
                    response = agent.process_input(user_input)
                    print(f"\n{response}")

                except EOFError:
                    break

        except KeyboardInterrupt:
            print("\n\n⚠️  Emergency exit! State not persisted.")
            print("   Run again with --chat to resume (previous state intact)")

    def _show_status(self, agent):
        """Display current agent status"""
        l3 = agent.memory.ram['l3_ego']
        print(f"\n📊 Agent Status: {agent.name}")
        print(f"   Version: {l3.persona_version}")
        print(f"   Alignment: {l3.cognitive_alignment_score:.1%}")
        print(f"   Observations: {len(l3.key_observations)}")
        print(f"   Patterns Learned: {len(l3.learned_patterns)}")
        print(f"   Context Used: {agent.memory.ram['context_window_used']} tokens")
        print(f"   Last Sync: {l3.last_sync}")

    def _cmd_skills(self, args):
        """Manage skills"""
        agent = RecursiveAgent(args.name, args.storage)

        if args.list:
            skills = agent.skill_factory.list_skills()
            print(f"\n📚 Skills for {args.name}:")
            if not skills:
                print("   No skills found. Create one with --create")
            for skill in skills:
                print(f"   • {skill.get('name', 'unnamed')}")
                print(f"     {skill.get('description', 'No description')}")

        elif args.create:
            print(f"🛠️  Creating skill: {args.create}")

            # Check if using advanced agent with safety
            if args.safety:
                agent = AdvancedRecursiveAgent(args.name, args.storage, enable_safety=True)
                success, result = agent.create_skill_safe(
                    name=args.create.replace(' ', '-'),
                    description=args.create,
                    instructions=f"# {args.create.title()}\nAuto-generated skill."
                )
                if success:
                    print(f"✅ Skill created: {result}")
                else:
                    print(f"❌ Failed: {result}")
            else:
                path = agent.skill_factory.create_skill(
                    name=args.create.replace(' ', '-'),
                    description=args.create,
                    instructions=f"# {args.create.title()}\nAuto-generated skill."
                )
                print(f"✅ Skill created: {path}")

            agent.end_session()
        else:
            print("Use --list to see skills or --create to add one")

    def _cmd_export(self, args):
        """Export agent state"""
        storage_path = Path(args.storage)
        memories_path = storage_path / 'memories.json'
        skill_path = storage_path / 'SKILL.md'

        if not memories_path.exists():
            print(f"❌ No agent found at {args.storage}")
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        export_name = f"{args.name}_export_{timestamp}"

        if args.format == 'json':
            with open(memories_path, 'r') as f:
                data = json.load(f)

            export_path = Path(f"{export_name}.json")
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✅ Exported to: {export_path}")
            print(f"   Size: {export_path.stat().st_size} bytes")

        elif args.format == 'markdown':
            with open(skill_path, 'r') as f:
                content = f.read()

            export_path = Path(f"{export_name}.md")
            with open(export_path, 'w') as f:
                f.write(content)

            print(f"✅ Exported to: {export_path}")

    def _cmd_import(self, args):
        """Import agent state"""
        import_path = Path(args.import_state)
        if not import_path.exists():
            print(f"❌ File not found: {import_path}")
            return

        storage_path = Path(args.storage)
        storage_path.mkdir(parents=True, exist_ok=True)

        with open(import_path, 'r') as f:
            data = json.load(f)

        memories_path = storage_path / 'memories.json'
        with open(memories_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Imported state to: {storage_path}")
        print(f"   Agent: {args.name}")
        if 'l3_state' in data:
            print(f"   Version: {data['l3_state']['persona_version']}")

    def _cmd_verify(self, args):
        """Run safety verification"""
        agent = AdvancedRecursiveAgent(args.name, args.storage, enable_safety=True)
        report = agent.get_safety_report()

        print(f"\n🛡️  Safety Report for {args.name}:")
        print(f"   Status: {report['safety_status']}")
        print(f"   Circuit Breaker: {report['circuit_breaker']}")
        print(f"   Risk Score: {report['risk_report']['risk_score']}/100")
        print(f"   Total Violations: {report['risk_report']['violation_count']}")

        if report['risk_report']['recent_violations']:
            print(f"\n   Recent Violations:")
            for v in report['risk_report']['recent_violations'][-3:]:
                print(f"      - {v['policy']}: {v['risk_level']}")


def main():
    cli = RecursiveCLI()
    cli.run()


if __name__ == '__main__':
    main()
