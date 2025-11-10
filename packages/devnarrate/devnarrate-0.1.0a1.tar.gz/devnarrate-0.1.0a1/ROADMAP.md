# DevNarrate Roadmap

## Core Features

### 1. Commit Message Generator
- Analyze git staged changes
- Support multiple styles: conventional, semantic, descriptive
- Use git diff to understand context
- Optional: Use LLM to generate smart messages

### 2. PR Description Generator
- Parse commit history between branches
- Analyze code changes (additions/deletions)
- Generate summary, changes, test plan sections
- Support templates

### 3. CI/CD Slack Notifications
- Post build status (success/failure/warning)
- Include build URL and details
- Support Slack webhooks
- Format with colors and emojis

### 4. Dev Update Slack Notifications
- Post development updates
- Support custom channels
- Flexible message formatting

## Technical Decisions

### MCP Tools vs CLI
- Start with MCP tools (work with Claude Desktop, etc.)
- Later: Add CLI interface using same logic
- Share core functionality between both

### Dependencies to Add
- `GitPython` or `pygit2` - Git operations
- `anthropic` or `openai` - LLM for smart generation
- `requests` - Slack webhooks

### Project Structure
```
devnarrate/
├── tools/           # MCP tool implementations
├── git/             # Git operations
├── slack/           # Slack integrations
├── generators/      # Message/description generators
└── cli/             # CLI interface (future)
```

## Implementation Order
1. Git diff/status reading
2. Simple commit message generation (rule-based)
3. Slack webhook posting
4. PR description generation
5. LLM-enhanced generation
6. CLI interface
