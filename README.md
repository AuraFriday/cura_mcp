# Cura MCP Server

**Control Ultimaker Cura with AI - Complete Slicing API Access + Python Execution**

Works with **any AI that supports MCP** - from desktop apps to web-based AI (via [browser extension](https://aurafriday.com/install/))

[![Cura Version](https://img.shields.io/badge/Cura-5.11%2B-blue)](https://ultimaker.com/software/ultimaker-cura)
[![Python](https://img.shields.io/badge/Python-3.7%2B-green)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange)](https://modelcontextprotocol.io)

---

## 🎥 Watch This In Action

See AI control Cura in real-time - loading models, rotating, configuring settings, and slicing with natural language commands:

[![Watch Demo Video](https://img.youtube.com/vi/U6yiY-5_0_8/maxresdefault.jpg)](https://www.youtube.com/watch?v=U6yiY-5_0_8)

*Click above to watch: "How to use your favourite AI to do Slicing and 3D prints using Model Context Protocol"*

---

## 🚀 What This Is

A Cura plugin that lets you **talk to your slicer in plain English**.

Tell AI what you want, and it handles all the technical details:
- "Load this STL, rotate and center it to fit, and slice for spiral-vase mode, no base, 5-line brim, on my Ender3"
- "Compare print time between solid and spiral vase mode"
- "Find the fastest settings that still give good quality"
- "Batch slice these 50 models with different orientations"

**No coding required. No manual configuration. Just natural conversation.**

---

## 🌐 Universal AI Compatibility

**Works with ANY AI that supports MCP** - no vendor lock-in!

- **Desktop AI**: Cursor, VS Code, Claude Desktop, Windsurf, Zed, Visual Studio, all JetBrains IDEs
- **Web-based AI**: ChatGPT.com, Claude.ai, Gemini, and any AI website via [browser extension](https://aurafriday.com/install/)
- **AI Assistants**: Cline, Continue, Amazon Q, Copilot Workspace, Sourcegraph Cody, BoltAI
- **CLI Tools**: OpenDevin, custom MCP clients

The MCP-Link server **automatically configures** itself with 15+ popular AI tools on installation!

---

## 💡 Three Powerful Benefits

### 1. **Talk to Your Slicer Like a Human**
No more hunting through menus or remembering setting names:
- "Make this print as strong as possible"
- "What's the fastest I can print this without losing quality?"
- "Try 10 different orientations and tell me which uses least material"

### 2. **Learn from Every Print**
AI remembers what worked and suggests improvements:
- "What settings worked best for my last PLA bracket?"
- "Show me all prints that finished under 2 hours"
- "Compare this design to similar parts I've printed before"

### 3. **Automate Repetitive Tasks**
Let AI handle the boring stuff:
- Batch process dozens of models while you sleep
- Automatically optimize orientation for every model
- Download models from the web, slice, and report results
- Track material costs and print times across all your projects

---

## 🎯 Real-World Examples

### "I need this bracket to be as strong as possible"
AI automatically:
- Sets 100% infill
- Increases wall count to 5
- Adjusts layer height for strength
- Slices and shows estimated print time

### "Which orientation uses the least material?"
AI tries multiple angles:
- Rotates model at 0°, 45°, 90°
- Slices each orientation
- Compares material usage
- Recommends the best option with time/cost breakdown

### "Batch process these 50 models overnight"
AI handles everything:
- Loads each model
- Checks if it fits the build plate
- Rotates if needed
- Slices with your preferred settings
- Saves all G-code files
- Generates a summary report in the morning

---

## 🛠️ What Makes This Possible

Behind the scenes, AI can access powerful tools to help you:

- **🌐 Web Browser** - Download models from Thingiverse, Printables, etc.
- **🧠 Database** - Remember settings that worked well for past prints
- **💬 Popups** - Show you results, charts, and summaries
- **🖥️ Desktop Control** - Interact with Cura's interface when needed
- **📚 Documentation** - Look up Cura features and settings on the fly

**All of this works locally on your computer. No cloud required.**

---

## 📦 Installation

### Prerequisites

1. **Download MCP-Link Server**  
   Get the latest release: https://github.com/AuraFriday/mcp-link-server/releases/tag/latest
   
   The server **automatically configures** itself with these AI tools:
   - **IDEs**: Cursor, VS Code, Windsurf, Zed, Visual Studio
   - **JetBrains**: IntelliJ, PyCharm, Android Studio (all JetBrains IDEs)
   - **AI Assistants**: Claude Desktop, Cline, Continue, Amazon Q, Copilot Workspace, Sourcegraph Cody
   - **Mac-only**: BoltAI
   - **CLI Tools**: OpenDevin, Windmill.dev
   - **Web-based AI**: Any AI website (ChatGPT, Claude, etc.) via [browser extension](https://aurafriday.com/install/)

2. **Install Ultimaker Cura**  
   Download from: https://ultimaker.com/software/ultimaker-cura  
   (Tested with Cura 5.11+)

3. **Clone This Repository**  
   ```bash
   git clone https://github.com/AuraFriday/Cura-MCP-Server.git
   ```

### Installation Steps

#### Windows
1. Open File Explorer and navigate to:
   ```
   %APPDATA%\cura\5.11\plugins\
   ```
   (Replace `5.11` with your Cura version)

2. Copy the `CuraMCP` folder from this repository into the `plugins` folder

3. Restart Cura

4. Check `Help` → `Show Console` to verify the plugin connected to MCP-Link server

#### macOS
1. Open Finder and navigate to:
   ```
   ~/Library/Application Support/cura/<version>/plugins/
   ```

2. Copy the `CuraMCP` folder into the `plugins` folder

3. Restart Cura

#### Linux
1. Navigate to:
   ```
   ~/.local/share/cura/<version>/plugins/
   ```

2. Copy the `CuraMCP` folder into the `plugins` folder

3. Restart Cura

### Verification

The plugin auto-connects to the MCP server on startup. Check the **TEXT COMMANDS** window in Cura to see connection logs:

```
[OK] Connected! Session ID: ...
[OK] Successfully registered tool: cura
```

---

## 🏗️ How It Works

1. **Install the plugin** - Copy files to Cura's plugin folder
2. **Start Cura** - Plugin automatically connects to MCP-Link server
3. **Talk to AI** - Use any supported AI tool (Cursor, Claude, ChatGPT, etc.)
4. **AI controls Cura** - Handles all the technical details for you
5. **Get results** - AI reports back with print times, material usage, and more

**Everything runs locally on your computer. Your models and settings stay private.**

---

## 💡 Who This Is For

### 🏭 **Production Shops**
- Batch process orders overnight
- Optimize material costs automatically
- Track print history and settings that work
- Reduce manual slicing time by 90%

### 🎓 **Educators & Students**
- Learn 3D printing through conversation
- Experiment with settings without fear
- Understand how parameters affect results
- Get instant feedback and explanations

### 🔬 **Makers & Hobbyists**
- Spend less time in menus, more time creating
- Let AI handle the tedious optimization
- Remember what worked for past projects
- Discover new techniques through AI suggestions

### 🚀 **Power Users**
- Automate complex workflows
- Integrate with other tools and databases
- Build custom slicing pipelines
- Push Cura beyond its UI limitations

---

## 📚 Learn More

- **[Development Guide](howto.md)** - Technical documentation for developers
- **[Plugin Source](CuraMCP/)** - View the code
- **[Cura Repository](https://github.com/Ultimaker/Cura)** - Official Cura project

---

## 🚀 Coming Soon

- Visual status indicator in Cura's interface
- Automatic slice preview generation
- G-code analysis and optimization suggestions
- Library of common slicing workflows
- Integration with more 3D printing services

---

## 🤝 Contributing

**Want to help?** We'd love your contributions!

- Share your use cases and workflows
- Report bugs or suggest features
- Create tutorial videos
- Test with different Cura versions
- Help improve documentation

---

## 📄 License

Proprietary - See LICENSE file for details

---

## 👤 Author

Created by [Christopher Nathan Drake](https://github.com/AuraFriday)

---

## 🔗 Links

- **MCP-Link Server**: https://github.com/AuraFriday/mcp-link-server
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Ultimaker Cura**: https://github.com/Ultimaker/Cura
- **Cura Marketplace**: https://marketplace.ultimaker.com/app/cura/plugins

---

## ❓ FAQ

**Q: Does this work with my Cura version?**  
A: Tested with Cura 5.11+. Should work with any recent version that supports plugins.

**Q: Do I need to know how to code?**  
A: No! You just talk to AI in plain English. AI handles all the technical details.

**Q: Is my data private?**  
A: Yes! Everything runs locally on your computer. No cloud uploads required.

**Q: Does this work offline?**  
A: Yes! All operations are local. You can even use local AI models if you prefer.

**Q: Can I use this with ChatGPT/Claude/etc?**  
A: Yes! Works with any AI that supports MCP. For web-based AI, install the [browser extension](https://aurafriday.com/install/).

**Q: What AI tools work with this?**  
A: 15+ tools auto-configure including Cursor, VS Code, Claude Desktop, all JetBrains IDEs, and more. See Installation for the full list.

**Q: Can AI use my other Cura plugins?**  
A: Yes! AI can discover and work with any plugins you have installed.

**Q: Is this safe?**  
A: AI can control Cura fully, so only use trusted AI tools. MCP-Link includes approval workflows for safety.

---

## 🌟 Star This Project!

If you find this useful, please star the repository and share with the 3D printing community!

**Questions?** Open an issue or check the documentation in [`howto.md`](howto.md)

---

**This is the future of AI-powered slicing.** 🚀
