# Implementation Notes: AI Edge Gallery Integration

## Changes Made

### 1. Created scripts/index.html (NEW)
- **Purpose**: JavaScript WebView bridge enabling filesystem operations
- **Features**:
  - Implements 4 core tools: read_file, write_file, list_files, search
  - Security prefix validation (`FS_CMD:`)
  - Correlation ID tracking for async operations
  - Dual communication protocol (Android WebView + fallback postMessage)
  - Operation timeouts (30s) and error handling
  - Real-time status logging UI

### 2. Updated SKILL.md (MODIFIED)
Added to YAML frontmatter:
- `tools` declaration listing available filesystem operations

Added sections:
- **Tool Schema Reference**: Complete JSON schemas for all 4 filesystem operations
- **Context Management Guidelines**: Tiered retrieval strategy for large archives
- **Security Constraints**: Workspace scoping rules
- **ReAct Loop Integration**: Explicit reasoning workflow

Preserved:
- Original 4-step execution flow (Initialise → Process → Respond → Evolve)
- All file paths and references to workspace/evolution directories
- Australian English requirement
- Obsidian markdown formatting

### 3. File Organization
Fixed file extensions as per README.md Layout:
- `evolution_history.jsonl` (was .jsonl.json)
- `events.jsonl` (was .jsonl.json)

## Technical Compliance

✓ **Progressive Disclosure**: 
  - Level 1 (Discovery): YAML frontmatter (~100 tokens)
  - Level 2 (Activation): SKILL.md body with instructions (~4000 tokens)
  - Level 3 (Execution): scripts/index.html loaded on-demand

✓ **Agent Skills Standard**:
  - Kebab-case directory naming
  - SKILL.md mandatory entry point
  - scripts/ directory for executable logic
  - references/ and assets/ available for future expansion

✓ **Gemma 4 Compatibility**:
  - Structured JSON tool call format
  - Correlation ID tracking for multi-turn operations
  - Context window optimization via filesystem offloading

## Bridge Communication Protocol

### Model → Bridge (Request)
```json
{
  "action": "read_file",
  "parameters": {"path": "second-self/workspace/IDENTITY.md"},
  "correlationId": "uuid"
}
```

### Bridge → Host (Native)
```
FS_CMD:read_file:{"path":"...","id":"uuid","action":"read_file"}
```

### Host → Bridge (Response)
```json
{
  "type": "tool_result",
  "id": "uuid",
  "status": "success",
  "data": "file content",
  "timestamp": "2026-04-10T..."
}
```

## Security Architecture

1. **Directory Scoping**: Bridge validates paths stay within `second-self/` workspace
2. **Command Prefix**: `FS_CMD:` prefix required for privileged operations
3. **Origin Validation**: Ready for production harness origin validation
4. **Approval Gates**: Write operations trigger HITL (Human-in-the-Loop) in harness
5. **No Network**: WebView operates 100% offline, no fetch() to external hosts

## Next Steps for Deployment

1. Install skill in AI Edge Gallery `skills/` directory
2. Harness will auto-detect SKILL.md and load Level 1 metadata
3. On activation, index.html initializes in hidden WebView
4. Model follows 4-step workflow using JSON tool calls
5. Evolution files update persistently across sessions
