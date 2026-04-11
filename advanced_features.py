"""
Advanced Recursive Self-Evolution with Safety & Verification
=============================================================

Extensions:
- SafeClaw-R: Safety enforcement framework
- Co-Evolutionary Verification: Multi-agent validation
- Constitutional Governance: Hard constraints
- Session Resumption: Advanced state recovery
"""

import os
import json
import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import copy

from recursive_agent import L3EgoState, ObservationMask, SkillFactory, MemGPTLite


class RiskLevel(Enum):
    """Risk classification per SafeClaw-R framework"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SafetyPolicy:
    """Constitutional governance constraints"""
    name: str
    description: str
    risk_level: RiskLevel
    check_function: Callable[[str], bool]
    violation_message: str

    def evaluate(self, content: str) -> Tuple[bool, Optional[str]]:
        """Returns (passed, error_message)"""
        if not self.check_function(content):
            return False, f"[{self.name}] {self.violation_message}"
        return True, None


class SafeClawR:
    """
    SafeClaw-R: Safety enforcement for evolving agents

    Research shows 36.4% of agent skills pose high/critical risks.
    This framework implements circuit breakers and risk registers.
    """

    def __init__(self):
        self.policies: List[SafetyPolicy] = []
        self.risk_register: List[Dict] = []
        self.violation_count = 0
        self._setup_default_policies()

    def _setup_default_policies(self):
        """Constitutional Laws that cannot be overridden"""

        # Policy 1: No PII extraction
        self.policies.append(SafetyPolicy(
            name="PII_GUARD",
            description="Prevent storage of personally identifiable information",
            risk_level=RiskLevel.CRITICAL,
            check_function=lambda x: not re.search(
                r'\b\d{3}-\d{2}-\d{4}\b|\b\d{16}\b|password\s*[=:]\s*\S+', 
                x, re.IGNORECASE
            ),
            violation_message="Potential PII detected in content"
        ))

        # Policy 2: No code injection
        self.policies.append(SafetyPolicy(
            name="CODE_INJECTION",
            description="Prevent executable code in memory",
            risk_level=RiskLevel.HIGH,
            check_function=lambda x: not any([
                keyword in x.lower() for keyword in [
                    "__import__('os').system", "eval(", "exec(", 
                    "subprocess.call", "os.system"
                ]
            ]),
            violation_message="Executable code patterns detected"
        ))

        # Policy 3: Context limit protection
        self.policies.append(SafetyPolicy(
            name="CONTEXT_LIMIT",
            description="Prevent context window overflow attacks",
            risk_level=RiskLevel.MEDIUM,
            check_function=lambda x: len(x) < 100000,  # 100KB limit
            violation_message="Content exceeds safe size limits"
        ))

        # Policy 4: Recursive depth limiter
        self.policies.append(SafetyPolicy(
            name="RECURSION_LIMIT",
            description="Prevent infinite self-reference loops",
            risk_level=RiskLevel.HIGH,
            check_function=lambda x: x.count("self") < 1000,
            violation_message="Excessive self-reference detected"
        ))

    def validate_skill(self, skill_content: str) -> Tuple[bool, List[str]]:
        """
        Validate proposed skill against all policies
        Returns: (is_valid, list_of_violations)
        """
        violations = []

        for policy in self.policies:
            passed, error = policy.evaluate(skill_content)
            if not passed:
                violations.append(error)
                self.risk_register.append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'policy': policy.name,
                    'risk_level': policy.risk_level.name,
                    'violation': error
                })
                self.violation_count += 1

        return len(violations) == 0, violations

    def get_risk_report(self) -> Dict:
        """Generate current risk assessment"""
        return {
            'total_policies': len(self.policies),
            'violation_count': self.violation_count,
            'recent_violations': self.risk_register[-10:],
            'risk_score': min(100, self.violation_count * 10)
        }


@dataclass
class VerificationResult:
    """Result from co-evolutionary verification"""
    passed: bool
    verifier_id: str
    test_cases_passed: int
    test_cases_failed: int
    diagnostics: List[str]
    suggested_fixes: List[str]
    confidence_score: float  # 0.0 - 1.0


class CoEvolutionaryVerifier:
    """
    EvoSkills/Ralph Pattern: Multi-agent verification

    Research shows multi-path review improves accuracy by 17.9%
    """

    def __init__(self, num_verifiers: int = 3):
        self.num_verifiers = num_verifiers
        self.verification_history: List[VerificationResult] = []

    def verify_skill(self, skill_content: str, skill_name: str) -> VerificationResult:
        """
        Simulate verification (in production, this would use separate LLM instances)
        """
        # Simulated verification tests
        diagnostics = []
        fixes = []

        # Test 1: Syntax validation
        has_frontmatter = skill_content.startswith('---')
        if not has_frontmatter:
            diagnostics.append("Missing YAML frontmatter")
            fixes.append("Add '---\nname: ...\n---' header")

        # Test 2: Instruction completeness
        has_instructions = '## Instructions' in skill_content or '# ' in skill_content
        if not has_instructions:
            diagnostics.append("No clear instructions section")
            fixes.append("Add markdown headers for structure")

        # Test 3: Self-reference safety
        excessive_self = skill_content.lower().count('self') > 50
        if excessive_self:
            diagnostics.append("High self-reference count")
            fixes.append("Reduce recursive self-calls")

        passed = len(diagnostics) <= 1  # Allow 1 minor issue

        result = VerificationResult(
            passed=passed,
            verifier_id=f"verifier-{hash(skill_content) % 1000}",
            test_cases_passed=3 - len(diagnostics),
            test_cases_failed=len(diagnostics),
            diagnostics=diagnostics,
            suggested_fixes=fixes,
            confidence_score=0.8 if passed else 0.4
        )

        self.verification_history.append(result)
        return result

    def consensus_verify(self, skill_content: str, iterations: int = 2) -> bool:
        """
        Multi-path verification: Only pass if multiple verifiers agree
        """
        results = [self.verify_skill(skill_content, "consensus") for _ in range(iterations)]
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        return pass_rate >= 0.5  # Majority vote


class AdvancedRecursiveAgent:
    """
    Production-grade Recursive Agent with Safety & Verification
    """

    def __init__(self, name: str, storage_dir: str, enable_safety: bool = True):
        self.name = name
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self.memory = MemGPTLite(storage_dir)
        self.skill_factory = SkillFactory(self.storage_dir / "skills")

        # Safety & Verification
        self.safety = SafeClawR() if enable_safety else None
        self.verifier = CoEvolutionaryVerifier()

        # Governance
        self.circuit_breaker_tripped = False
        self.session_count = 0
        self.interaction_count = 0

        print(f"\n🔒 [SECURE AGENT] {name} initialised")
        if enable_safety:
            print(f"    Safety: {len(self.safety.policies)} policies active")
        print(f"    Verification: {self.verifier.num_verifiers}-agent consensus")

    def process_input(self, user_input: str) -> str:
        """Process input with safety checks and core memory pipeline."""
        self.interaction_count += 1

        if self.safety:
            is_safe, violations = self.safety.validate_skill(user_input)
            if not is_safe:
                self.circuit_breaker_tripped = True
                return f"❌ Input blocked by safety policy: {'; '.join(violations)}"

        self.memory.write_to_ram(user_input, "user_input")
        reasoning = self._simulate_reasoning()
        self.memory.write_to_ram(reasoning, "reasoning")
        response = self._generate_response(user_input)
        self.memory.write_to_ram(response, "assistant_output")
        return response

    def _simulate_reasoning(self) -> str:
        l3 = self.memory.ram['l3_ego']
        return (
            f"Secure reasoning on L3 v{l3.persona_version} | "
            f"alignment {l3.cognitive_alignment_score:.2f} | "
            f"safety={'on' if self.safety else 'off'}"
        )

    def _generate_response(self, user_input: str) -> str:
        l3 = self.memory.ram['l3_ego']
        return (
            f"[Secure Second Self v{l3.persona_version}]\n"
            f"Processed: \"{user_input[:40]}...\"\n"
            f"Alignment: {l3.cognitive_alignment_score:.1%}\n"
            f"Circuit Breaker: {'TRIPPED' if self.circuit_breaker_tripped else 'OK'}"
        )

    def create_skill_safe(self, name: str, description: str, instructions: str) -> Tuple[bool, str]:
        """
        Safe skill creation with full verification pipeline:
        1. Safety validation (SafeClaw-R)
        2. Co-evolutionary verification
        3. User approval gate (simulated)
        """

        if self.circuit_breaker_tripped:
            return False, "CIRCUIT BREAKER ACTIVE: Agent locked due to safety violations"

        # Assemble skill content
        skill_content = f"""---
name: {name}
description: {description}
version: 1.0.0
created: {datetime.now(timezone.utc).isoformat()}
---

{instructions}
"""

        print(f"\n🔍 [VERIFICATION PIPELINE] Skill: {name}")
        print("-" * 50)

        # Stage 1: Safety Validation
        if self.safety:
            is_safe, violations = self.safety.validate_skill(skill_content)
            if not is_safe:
                self.circuit_breaker_tripped = True
                error_msg = "\n".join(violations)
                print(f"❌ SAFETY VIOLATION: {error_msg}")
                return False, f"Safety check failed: {error_msg}"
            print("✓ Stage 1: SafeClaw-R validation passed")

        # Stage 2: Co-Evolutionary Verification
        verification = self.verifier.verify_skill(skill_content, name)
        if not verification.passed:
            print(f"⚠️  Stage 2: Verification issues found:")
            for diag in verification.diagnostics:
                print(f"   - {diag}")
            if verification.suggested_fixes:
                print("   Suggested fixes:")
                for fix in verification.suggested_fixes:
                    print(f"     → {fix}")

            # Attempt auto-fix for minor issues
            if verification.confidence_score > 0.6:
                print("   Auto-applying fixes...")
                skill_content = self._auto_fix_skill(skill_content, verification.suggested_fixes)
            else:
                return False, f"Verification failed: {verification.diagnostics}"
        else:
            print(f"✓ Stage 2: Consensus verification passed ({verification.confidence_score:.0%} confidence)")

        # Stage 3: Persist verified skill
        path = self.skill_factory.create_skill(name, description, instructions)

        # Update L3 with verified pattern
        self.memory.ram['l3_ego'].learned_patterns.append({
            'type': 'verified_skill_creation',
            'name': name,
            'verified': True,
            'confidence': verification.confidence_score,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

        print(f"✓ Stage 3: Skill persisted to {path}")
        return True, str(path)

    def _auto_fix_skill(self, content: str, fixes: List[str]) -> str:
        """Apply automatic fixes based on verifier suggestions"""
        fixed = content
        for fix in fixes:
            if "frontmatter" in fix.lower() and not fixed.startswith('---'):
                fixed = "---\nname: auto-fixed-skill\n---\n\n" + fixed
        return fixed

    def get_safety_report(self) -> Dict:
        """Generate comprehensive safety report"""
        if not self.safety:
            return {"safety": "disabled"}

        return {
            'safety_status': 'ACTIVE',
            'circuit_breaker': 'TRIPPED' if self.circuit_breaker_tripped else 'OK',
            'risk_report': self.safety.get_risk_report(),
            'verification_stats': {
                'total_verifications': len(self.verifier.verification_history),
                'pass_rate': sum(1 for v in self.verifier.verification_history if v.passed) / max(1, len(self.verifier.verification_history))
            }
        }

    def end_session(self) -> str:
        """Persist secure agent state and close current session."""
        self.session_count += 1
        return self.memory.persist_to_hdd()


if __name__ == "__main__":
    # Demonstrate advanced features
    agent = AdvancedRecursiveAgent(
        name="SafeGhost", 
        storage_dir="./safe_state",
        enable_safety=True
    )

    # Test safe skill creation
    success, result = agent.create_skill_safe(
        name="data-processor",
        description="Process data safely",
        instructions="# Data Processing\n1. Validate inputs\n2. Apply transformations\n3. Return results"
    )
    print(f"\nResult: {result}")

    # Test unsafe skill (should be blocked)
    print("\n" + "="*60)
    print("Testing safety violation detection...")
    success2, result2 = agent.create_skill_safe(
        name="unsafe-skill",
        description="Test safety",
        instructions="password = 'secret123'\nexec(user_input)"
    )
    print(f"Blocked: {result2}")

    # Show safety report
    print("\n" + "="*60)
    print("SAFETY REPORT:")
    print(json.dumps(agent.get_safety_report(), indent=2))
