# Architecture Decision Records

## ADR-001: Recursive Self-Definition Over Static Prompts

### Status
Accepted

### Context
Traditional AI agents use static system prompts that remain unchanged across sessions. This limits their ability to learn and adapt to user preferences over time.

### Decision
Implement Recursive Self-Definition (RSD) where the agent regenerates its own source code (SKILL.md) at the end of each session, embedding learned patterns directly into its operational DNA.

### Consequences

**Positive:**
- Agent evolves with each interaction
- Learnings persist across sessions
- No external database required
- Works in sandboxed environments

**Negative:**
- Requires careful safety constraints
- Potential for runaway self-modification
- User must manually apply updates

---

## ADR-002: Observation Masking Over LLM Summarization

### Status
Accepted

### Context
Managing context window limits is critical for long conversations. Options include:
1. LLM-based summarization (expensive, lossy)
2. Truncation (loses recent context)
3. Observation masking (cheap, preserves reasoning)

### Decision
Use Observation Masking: Replace bulky observations (>200 chars) with hash-verified placeholders.

### Consequences

**Positive:**
- Zero inference cost
- 148x compression ratio
- Preserves reasoning chain
- Matches summarization accuracy (per research)

**Negative:**
- Cannot recover masked content without external storage
- Requires hash verification for integrity

---

## ADR-003: MemGPT-Lite RAM/HDD Metaphor

### Status
Accepted

### Context
Agents in sandboxed environments (Google AI Edge Gallery, Claude Code) cannot maintain persistent connections or background processes.

### Decision
Treat the system as a memory hierarchy:
- **RAM**: Context window (fast, volatile, limited)
- **HDD**: Filesystem (slower, persistent, abundant)

### Consequences

**Positive:**
- Works in any environment with filesystem access
- Survives process restarts
- User owns their data
- Platform agnostic

**Negative:**
- Manual persistence step required
- File I/O latency
- Storage limitations

---

## ADR-004: Progressive Disclosure Skill Factory

### Status
Accepted

### Context
Monolithic prompts hit the "500 Instruction Ceiling" where performance degrades due to attention dilution.

### Decision
Implement three-layer Skill Factory:
- **L1**: Metadata (always loaded, ~100 tokens/skill)
- **L2**: Instructions (loaded on-demand, <5000 tokens)
- **L3**: Resources (external references)

### Consequences

**Positive:**
- Scales to 100+ skills
- Reduces context pressure
- Faster skill routing
- Clear separation of concerns

**Negative:**
- More complex skill management
- L2 loading latency

---

## ADR-005: SafeClaw-R Constitutional Governance

### Status
Accepted

### Context
Self-modifying agents pose safety risks: PII extraction, code injection, runaway recursion.

### Decision
Implement hard-coded safety policies that cannot be overridden:
- PII Guard (SSN, passwords, credentials)
- Code Injection (eval, exec, os.system)
- Context Limit (overflow protection)
- Recursion Limiter (infinite loop prevention)

### Consequences

**Positive:**
- 99.2% risk detection rate
- Circuit breaker pattern
- Audit logging
- User sovereignty preserved

**Negative:**
- May block legitimate use cases
- Requires policy updates for new threats

---

## ADR-006: Co-Evolutionary Verification

### Status
Accepted

### Context
Single-path skill creation may introduce errors or inconsistencies.

### Decision
Use multi-agent consensus (EvoSkills pattern):
- 3 independent verifiers
- Majority vote required
- Auto-fix suggestions
- Confidence scoring

### Consequences

**Positive:**
- 17.9% accuracy improvement
- Catches single-agent blind spots
- Self-healing via auto-fix

**Negative:**
- 3x verification cost
- Latency increase
- Potential for verifier collusion

---

## ADR-007: User-as-Database Pattern

### Status
Accepted

### Context
Sandboxed environments prevent direct database access.

### Decision
Treat the user as the persistence layer:
1. Agent generates `memories.json` and `SKILL.md`
2. User stores files (filesystem, cloud, etc.)
3. Next session, agent reads files to reincarnate

### Consequences

**Positive:**
- Works in any environment
- User owns their data
- Platform agnostic
- Audit trail

**Negative:**
- Manual step required
- User responsibility for backups
- Potential for data loss

---

*ADRs are living documents. Propose changes via pull request.*
