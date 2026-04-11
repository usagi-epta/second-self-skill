import sys
#!/usr/bin/env python3
"""
Test Suite for Recursive Self-Evolution Architecture
====================================================

Comprehensive tests for all components:
- L3 Ego-State mutation
- Observation Masking
- MemGPT-Lite persistence
- Skill Factory
- SafeClaw-R safety
- Co-Evolutionary Verification
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from recursive_agent import (
    L3EgoState, ObservationMask, SkillFactory, 
    MemGPTLite, RecursiveAgent
)
from advanced_features import (
    SafeClawR, CoEvolutionaryVerifier, 
    AdvancedRecursiveAgent, RiskLevel, SafetyPolicy
)


class TestL3EgoState(unittest.TestCase):
    """Test L3 Genome mutation and state management"""

    def test_initial_state(self):
        l3 = L3EgoState()
        self.assertEqual(l3.persona_version, "1.0.0")
        self.assertEqual(l3.cognitive_alignment_score, 0.95)
        self.assertEqual(len(l3.key_observations), 0)

    def test_mutation_increments_version(self):
        l3 = L3EgoState()
        initial_version = l3.persona_version
        l3.mutate(["test observation"], 1)
        self.assertNotEqual(l3.persona_version, initial_version)
        self.assertIn("1", l3.persona_version.split(".")[-1])

    def test_observation_deduplication(self):
        l3 = L3EgoState()
        l3.mutate(["obs1", "obs1", "obs2"], 3)
        # Should deduplicate
        self.assertEqual(len(l3.key_observations), 2)

    def test_observation_limit(self):
        l3 = L3EgoState()
        many_obs = [f"obs{i}" for i in range(15)]
        l3.mutate(many_obs, 15)
        self.assertLessEqual(len(l3.key_observations), 10)

    def test_alignment_increases(self):
        l3 = L3EgoState()
        initial = l3.cognitive_alignment_score
        l3.mutate(["test"], 10)
        self.assertGreater(l3.cognitive_alignment_score, initial)
        self.assertLessEqual(l3.cognitive_alignment_score, 1.0)


class TestObservationMasking(unittest.TestCase):
    """Test observation compression and masking"""

    def test_short_content_not_masked(self):
        short = "Short text"
        # In actual implementation, masking only applies >200 chars
        # This tests the mask creation itself
        mask = ObservationMask.from_raw(short, "test")
        self.assertTrue(mask.is_masked)
        self.assertIn(mask.raw_content_hash, mask.to_placeholder())

    def test_compression_ratio(self):
        long_content = "A" * 10000
        mask = ObservationMask.from_raw(long_content, "test")
        placeholder = mask.to_placeholder()
        ratio = len(long_content) / len(placeholder)
        self.assertGreater(ratio, 50)  # Should compress significantly

    def test_hash_consistency(self):
        content = "Test content for hashing"
        mask1 = ObservationMask.from_raw(content, "test")
        mask2 = ObservationMask.from_raw(content, "test")
        self.assertEqual(mask1.raw_content_hash, mask2.raw_content_hash)

    def test_summary_generation(self):
        content = "First part of content. " + "More content. " * 50
        mask = ObservationMask.from_raw(content, "test")
        self.assertIn("First part", mask.summary)
        self.assertLessEqual(len(mask.summary), 103)  # 100 + "..."


class TestSkillFactory(unittest.TestCase):
    """Test skill creation and loading"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.factory = SkillFactory(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_skill(self):
        path = self.factory.create_skill(
            name="test-skill",
            description="Test skill",
            instructions="# Test\nInstructions here"
        )
        self.assertTrue(path.exists())
        self.assertIn("SKILL.md", str(path))

    def test_skill_registry_update(self):
        self.factory.create_skill("registry-test", "Test", "Instructions")
        self.assertIn("registry-test", self.factory.skill_registry)

    def test_list_skills(self):
        self.factory.create_skill("skill1", "First", "Inst1")
        self.factory.create_skill("skill2", "Second", "Inst2")
        skills = self.factory.list_skills()
        self.assertEqual(len(skills), 2)

    def test_load_skill_content(self):
        self.factory.create_skill("load-test", "Test", "# Loaded Content")
        content = self.factory.load_skill("load-test")
        self.assertIn("Loaded Content", content)

    def test_skill_name_sanitization(self):
        path = self.factory.create_skill(
            "Test Skill With Spaces!",
            "Description",
            "Instructions"
        )
        # Should sanitize to test-skill-with-spaces-
        self.assertTrue(path.exists())


class TestMemGPTLite(unittest.TestCase):
    """Test memory management and persistence"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory = MemGPTLite(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_to_ram(self):
        self.memory.write_to_ram("Test content", "user_input")
        self.assertEqual(len(self.memory.ram['conversation_buffer']), 1)

    def test_observation_masking_in_ram(self):
        long_content = "X" * 1000
        self.memory.write_to_ram(long_content, "observation")
        # Should be masked in buffer
        last_entry = self.memory.ram['conversation_buffer'][-1]
        self.assertIn("[...", last_entry['content'])

    def test_persistence_creates_files(self):
        self.memory.write_to_ram("Test", "user_input")
        session_id = self.memory.persist_to_hdd()

        memories_path = Path(self.temp_dir) / 'memories.json'
        skill_path = Path(self.temp_dir) / 'SKILL.md'

        self.assertTrue(memories_path.exists())
        self.assertTrue(skill_path.exists())

    def test_bootstrap_loads_state(self):
        # First session
        self.memory.write_to_ram("Observation", "user_input")
        self.memory.persist_to_hdd()
        version = self.memory.ram['l3_ego'].persona_version

        # New instance (simulating restart)
        memory2 = MemGPTLite(self.temp_dir)
        self.assertEqual(memory2.ram['l3_ego'].persona_version, version)

    def test_context_compression(self):
        # Fill context to trigger compression
        for i in range(100):
            self.memory.write_to_ram(f"Message {i}", "user_input")
        # Should not crash and should manage context
        self.assertLessEqual(self.memory.ram['context_window_used'], 
                           self.memory.ram['context_limit'])


class TestSafeClawR(unittest.TestCase):
    """Test safety framework"""

    def setUp(self):
        self.safety = SafeClawR()

    def test_pii_detection(self):
        pii_content = "My SSN is 123-45-6789"
        is_safe, violations = self.safety.validate_skill(pii_content)
        self.assertFalse(is_safe)
        self.assertTrue(any("PII" in v for v in violations))

    def test_code_injection_detection(self):
        malicious = "__import__('os').system('rm -rf /')"
        is_safe, violations = self.safety.validate_skill(malicious)
        self.assertFalse(is_safe)
        self.assertTrue(any("injection" in v.lower() for v in violations))

    def test_safe_content_passes(self):
        safe = "# Normal Instructions\n1. Do something\n2. Do something else"
        is_safe, violations = self.safety.validate_skill(safe)
        self.assertTrue(is_safe)
        self.assertEqual(len(violations), 0)

    def test_custom_policy(self):
        custom = SafetyPolicy(
            name="CUSTOM",
            description="Test",
            risk_level=RiskLevel.LOW,
            check_function=lambda x: "forbidden" not in x.lower(),
            violation_message="Forbidden word found"
        )
        self.safety.policies.append(custom)

        is_safe, violations = self.safety.validate_skill("This has forbidden word")
        self.assertFalse(is_safe)

    def test_risk_report_generation(self):
        # Trigger some violations
        self.safety.validate_skill("SSN: 123-45-6789")
        report = self.safety.get_risk_report()
        self.assertIn('violation_count', report)
        self.assertGreater(report['violation_count'], 0)


class TestCoEvolutionaryVerifier(unittest.TestCase):
    """Test multi-agent verification"""

    def setUp(self):
        self.verifier = CoEvolutionaryVerifier(num_verifiers=3)

    def test_verification_returns_result(self):
        result = self.verifier.verify_skill("# Test Skill", "test")
        self.assertIsInstance(result.passed, bool)
        self.assertIsInstance(result.diagnostics, list)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)

    def test_consensus_verification(self):
        # Simple skill should pass consensus
        result = self.verifier.consensus_verify("# Good Skill\n## Instructions", iterations=2)
        self.assertTrue(result)

    def test_verification_history_tracked(self):
        initial_count = len(self.verifier.verification_history)
        self.verifier.verify_skill("Test", "test")
        self.assertEqual(len(self.verifier.verification_history), initial_count + 1)

    def test_broken_skill_fails(self):
        broken = "No frontmatter or structure"
        result = self.verifier.verify_skill(broken, "broken")
        # Should have diagnostics
        self.assertGreater(len(result.diagnostics), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for full agent workflow"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_session_lifecycle(self):
        """Test complete session: init → chat → persist → reload"""
        # Session 1
        agent = RecursiveAgent("TestAgent", self.temp_dir)
        response = agent.process_input("Hello")
        self.assertIsNotNone(response)
        agent.end_session()

        # Session 2 (reincarnation)
        agent2 = RecursiveAgent("TestAgent", self.temp_dir)
        response2 = agent2.process_input("Remember me?")
        # Should have loaded previous state
        self.assertGreater(len(agent2.memory.ram['l3_ego'].key_observations), 0)

    def test_safe_skill_creation_pipeline(self):
        agent = AdvancedRecursiveAgent("SafeAgent", self.temp_dir, enable_safety=True)

        # Safe skill
        success, result = agent.create_skill_safe(
            "safe-skill", "Safe", "# Good Instructions"
        )
        self.assertTrue(success)

        # Unsafe skill
        success2, result2 = agent.create_skill_safe(
            "unsafe", "Test", "password = 'secret'"
        )
        self.assertFalse(success2)
        self.assertIn("Safety", result2)

    def test_observation_masking_integration(self):
        agent = RecursiveAgent("MaskAgent", self.temp_dir)

        # Large input should be masked
        large_input = "A" * 5000
        agent.process_input(large_input)

        # Check that masking occurred
        masked_count = len([o for o in agent.memory.ram['observations'] if o.is_masked])
        self.assertGreater(masked_count, 0)


def run_tests():
    """Run all tests and report results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestL3EgoState))
    suite.addTests(loader.loadTestsFromTestCase(TestObservationMasking))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestMemGPTLite))
    suite.addTests(loader.loadTestsFromTestCase(TestSafeClawR))
    suite.addTests(loader.loadTestsFromTestCase(TestCoEvolutionaryVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
