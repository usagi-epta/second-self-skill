# Second-Self Troubleshooting Guide

## Issue: "Filesystem bridge functions appear unavailable"

This error means the AI model cannot communicate with the WebView bridge.

### Causes & Solutions:

1. **WebView Not Loaded**
   - Ensure `scripts/index.html` exists in the skill directory
   - Verify the AI Edge Gallery harness supports JavaScript skills
   - Check that the app has WebView permissions enabled

2. **Communication Breakdown**
   - The bridge uses `window.postMessage` API
   - Some harness versions require explicit bridge initialization
   - Try restarting the conversation/session

3. **Path Issues**
   - All paths must be relative: `workspace/FILE.md` not `/workspace/FILE.md`
   - Do not use `second-self/` prefix in paths
   - Only `workspace/`, `evolution/`, and `scripts/` are accessible

4. **Skill Not Properly Installed**
   - Directory structure must be:
     ```
     skills/
     └── second-self/
         ├── SKILL.md
         ├── manifest.json
         ├── scripts/
         │   └── index.html
         ├── workspace/
         └── evolution/
     ```

### Testing the Bridge Manually

If the model consistently fails to load:

1. Check if `scripts/index.html` is valid HTML with embedded JavaScript
2. Verify no syntax errors in the JavaScript (check console if possible)
3. Ensure the bridge sends the `bridge_ready` signal on load

### Expected Behavior

When working correctly:
1. User activates skill
2. Model outputs: `{"action": "list_files", "parameters": {"path": "workspace"}, "correlationId": "1"}`
3. Harness intercepts JSON, sends to WebView
4. WebView returns file list
5. Model receives list as next input
6. Model proceeds to read files

### Fallback Mode

If the bridge truly cannot be loaded, the model should inform the user and offer to operate without the Second-Self persona, or suggest checking the AI Edge Gallery installation.