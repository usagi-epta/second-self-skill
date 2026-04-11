#!/usr/bin/env python3
"""
Final Verification Script
=========================

Verifies all components of the Recursive Self-Evolution implementation.
"""

import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if file exists and report"""
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"✅ {description:<40} ({size:>6} bytes)")
        return True
    else:
        print(f"❌ {description:<40} MISSING")
        return False

def check_syntax(filepath):
    """Check Python syntax"""
    import ast
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"   ⚠️  Syntax error: {e}")
        return False

def main():
    base_dir = Path(__file__).parent

    print("="*70)
    print("RECURSIVE SELF-EVOLUTION - FINAL VERIFICATION")
    print("="*70)
    print()

    # Check core files
    print("📦 Core Components:")
    all_good = True

    files_to_check = [
        (base_dir / "recursive_agent.py", "Core RSD Architecture"),
        (base_dir / "advanced_features.py", "Safety & Verification"),
        (base_dir / "cli.py", "Command Line Interface"),
        (base_dir / "test_suite.py", "Test Suite"),
        (base_dir / "integration_examples.py", "Integration Examples"),
        (base_dir / "demo.html", "Web Demonstration"),
        (base_dir / "README_IMPLEMENTATION.md", "Documentation"),
        (base_dir / "setup.py", "Package Setup"),
    ]

    for filepath, desc in files_to_check:
        if check_file(filepath, desc):
            if filepath.suffix == '.py':
                if not check_syntax(filepath):
                    all_good = False
        else:
            all_good = False

    print()
    print("📊 Testing Core Functionality:")

    try:
        from recursive_agent import RecursiveAgent, L3EgoState, MemGPTLite
        print("✅ Core imports successful")

        # Test L3 state
        l3 = L3EgoState()
        l3.mutate(["test"], 1)
        assert l3.persona_version != "1.0.0"
        print("✅ L3 Ego-State mutation working")

        # Test observation masking
        from recursive_agent import ObservationMask
        mask = ObservationMask.from_raw("A" * 1000, "test")
        assert mask.is_masked
        print("✅ Observation masking working")

        # Test agent initialization
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            agent = RecursiveAgent("TestAgent", temp_dir)
            response = agent.process_input("Hello")
            assert response is not None
            print("✅ Agent initialization working")

            agent.end_session()
            assert (Path(temp_dir) / "memories.json").exists()
            print("✅ Persistence working")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Test advanced features
        from advanced_features import SafeClawR, CoEvolutionaryVerifier
        safety = SafeClawR()
        is_safe, violations = safety.validate_skill("safe content")
        assert is_safe
        print("✅ SafeClaw-R safety framework working")

        verifier = CoEvolutionaryVerifier()
        result = verifier.verify_skill("# Test", "test")
        assert result.confidence_score >= 0
        print("✅ Co-Evolutionary Verification working")

    except Exception as e:
        print(f"❌ Functional test failed: {e}")
        import traceback
        traceback.print_exc()
        all_good = False

    print()
    print("="*70)
    if all_good:
        print("✅ ALL VERIFICATION CHECKS PASSED")
        print("="*70)
        print()
        print("The Recursive Self-Evolution implementation is complete and functional!")
        print()
        print("Quick start:")
        print("  python recursive_agent.py")
        print("  python cli.py --help")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
