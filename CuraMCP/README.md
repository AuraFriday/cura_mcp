# Cura MCP - AI-Powered Slicing

**Control Ultimaker Cura with AI through natural language commands.**

[![Watch Demo Video](https://img.youtube.com/vi/U6yiY-5_0_8/maxresdefault.jpg)](https://www.youtube.com/watch?v=U6yiY-5_0_8)

*Watch the demo: "How to use your favourite AI to do Slicing and 3D prints using Model Context Protocol"*

---

## What This Plugin Does

Talk to Cura in plain English through any AI tool that supports MCP (Model Context Protocol):

- "Load this STL, rotate and center it to fit, and slice for spiral-vase mode"
- "Compare print time between solid and spiral vase mode"
- "Find the fastest settings that still give good quality"
- "Batch slice these 50 models with different orientations"

**No coding required. No manual configuration. Just natural conversation.**

---

## Key Features

### 🗣️ Natural Language Control
- Load models from any path
- Rotate and position automatically
- Configure print settings by describing what you want
- Slice and get instant feedback on time and material usage

### 🤖 Universal AI Compatibility
Works with **any AI that supports MCP**:
- Desktop AI: Cursor, VS Code, Claude Desktop, Windsurf, all JetBrains IDEs
- Web-based AI: ChatGPT, Claude, Gemini (via [browser extension](https://aurafriday.com/install/))
- CLI Tools: OpenDevin, custom MCP clients

### 🔒 Local & Private
- Everything runs on your computer
- No cloud uploads required
- Your models and settings stay private

### ⚡ Powerful Automation
- Batch process hundreds of models
- Optimize orientation automatically
- Compare settings side-by-side
- Track material costs and print times

---

## Installation

### Prerequisites

1. **Install MCP-Link Server**  
   Download from: https://github.com/AuraFriday/mcp-link-server/releases/tag/latest
   
   The server auto-configures with 15+ popular AI tools including Cursor, VS Code, Claude Desktop, and more.

2. **Have Ultimaker Cura installed**  
   Tested with Cura 5.11+ (Download from https://ultimaker.com/software/ultimaker-cura)

### Install Plugin

The plugin is already installed if you're reading this in the Cura Marketplace! 🎉

Otherwise, manually install by copying the `CuraMCP` folder to:
- **Windows**: `%APPDATA%\cura\<version>\plugins\`
- **macOS**: `~/Library/Application Support/cura/<version>/plugins/`
- **Linux**: `~/.local/share/cura/<version>/plugins/`

### Verify Connection

1. Restart Cura
2. Open **Help** → **Show Console**
3. Look for:
   ```
   [OK] Connected! Session ID: ...
   [OK] Successfully registered tool: cura
   ```

---

## Usage Examples

### Basic Operations
*"Load C:\models\bracket.stl and center it on the build plate"*

AI automatically:
- Loads the file
- Centers it perfectly
- Reports success

### Optimization
*"Which orientation uses the least material?"*

AI tests multiple angles:
- Tries 0°, 45°, 90° rotations
- Slices each
- Compares material usage
- Recommends the best option

### Batch Processing
*"Slice all STL files in this folder with high-quality settings"*

AI processes everything:
- Finds all models
- Loads each one
- Applies your settings
- Saves G-code files
- Generates a summary report

---

## Requirements

- **Cura**: 5.11 or newer
- **MCP-Link Server**: Latest version from GitHub
- **AI Tool**: Any MCP-compatible AI (see list above)

---

## Documentation

- **Full Documentation**: https://github.com/AuraFriday/cura_mcp
- **Video Tutorial**: https://www.youtube.com/watch?v=U6yiY-5_0_8
- **MCP-Link Server**: https://github.com/AuraFriday/mcp-link-server

---

## Support

**Questions or issues?**
- Open an issue: https://github.com/AuraFriday/cura_mcp/issues
- View documentation: https://github.com/AuraFriday/cura_mcp/blob/main/howto.md

---

## License

Proprietary - See LICENSE file for details

---

## About

Created by Christopher Nathan Drake  
Part of the AuraFriday MCP ecosystem

**This is the future of AI-powered slicing.** 🚀

