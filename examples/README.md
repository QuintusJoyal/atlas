# Atlas Integration Examples

Concrete configuration files for integrating Atlas with different AI IDEs.

## Files

| File | IDE | Description |
|------|-----|-------------|
| `.cursorrules` | Cursor | Cursor rules configuration |
| `.opencode.json` | OpenCode | OpenCode project configuration |
| `CLAUDE.md` | Claude Code | Claude Code project instructions |
| `.github/copilot-instructions.md` | VS Code Copilot | Copilot custom instructions |

## Usage

1. Copy the relevant file to your project root
2. Adjust the `ATLAS_DATA_DIR` path if needed
3. The IDE will automatically load Atlas rules and agents

## How It Works

Each IDE has its own mechanism for loading project-level instructions:
- **Cursor:** reads `.cursorrules` from project root
- **OpenCode:** reads `.opencode.json` for project config
- **Claude Code:** reads `CLAUDE.md` from project root
- **VS Code Copilot:** reads `.github/copilot-instructions.md`

Atlas provides the same knowledge base to all IDEs. The configuration files simply tell each IDE where to find Atlas rules and knowledge.
