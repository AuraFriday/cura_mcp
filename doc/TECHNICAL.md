# Cura MCP Plugin Development Guide

## Overview

This guide documents everything needed to create a Cura plugin that exposes the full Cura API to AI agents via the MCP (Model Context Protocol) server architecture.

**Goal**: Create a plugin that gives AI agents 100% access to Cura's slicing capabilities, similar to how MCP-Link-fusion-new provides complete access to Fusion 360's API.

---

## Table of Contents

1. [Understanding Cura Plugins](#understanding-cura-plugins)
2. [Development Environment Setup](#development-environment-setup)
3. [Cura Plugin Architecture](#cura-plugin-architecture)
4. [Cura Python API](#cura-python-api)
5. [Installation & Testing](#installation--testing)
6. [Generic API Implementation Strategy](#generic-api-implementation-strategy)
7. [Marketplace Submission](#marketplace-submission)
8. [Resources & References](#resources--references)

---

## Understanding Cura Plugins

### Plugin Types

Cura supports several plugin types, each serving different purposes:

1. **Extension Plugin** - Adds new functionality to Cura (menus, dialogs, background services)
   - **This is what we need** for MCP integration
   - Runs as a background service
   - Can access the full Cura API
   - No UI required (though we can add one for status)

2. **Tool Plugin** - Adds new tools to the Cura interface
3. **FileReader Plugin** - Adds support for custom file formats
4. **OutputDevice Plugin** - Integrates with external hardware/services

### Extension Plugin Structure

```
CuraMCP/
├── __init__.py              # Plugin entry point
├── plugin.json              # Plugin metadata
├── mcp_integration.py       # Core MCP connection logic
├── lib/
│   └── mcp_client.py        # MCP client library (from template)
└── README.md                # User documentation
```

---

## Development Environment Setup

### Prerequisites

- **Python 3.7+** (Cura uses Python 3.10+ in recent versions)
- **Cura installed** (download from https://ultimaker.com/software/ultimaker-cura)
- **Text editor** (VS Code, PyCharm, etc.)
- **MCP-Link server running** (from https://github.com/aurafriday/mcp-link-server/releases)

### Finding Cura's Plugin Directory

**Windows:**
```
%APPDATA%\cura\<version>\plugins\
# Example: C:\Users\YourName\AppData\Roaming\cura\5.8\plugins\
```

**macOS:**
```
~/Library/Application Support/cura/<version>/plugins/
```

**Linux:**
```
~/.local/share/cura/<version>/plugins/
```

**Quick Method:**
1. Open Cura
2. Go to `Help` → `Show Configuration Folder`
3. Navigate to the `plugins` subfolder

### Development Workflow

1. Create your plugin folder in the plugins directory
2. Edit code in your favorite editor
3. Restart Cura to reload the plugin
4. Check `Help` → `Show Console` for debug output
5. Repeat

---

## Cura Plugin Architecture

### Plugin Entry Point: `plugin.json`

```json
{
  "name": "Cura MCP",
  "author": "Your Name",
  "version": "1.0.0",
  "description": "Connects Cura to MCP-Link server for AI-driven slicing",
  "api": 8,
  "supported_sdk_versions": ["8.0.0", "8.1.0", "8.2.0"],
  "i18n-catalog": "cura"
}
```

**Key Fields:**
- `api`: Cura API version (8 for Cura 5.x)
- `supported_sdk_versions`: Which Cura versions this plugin supports

### Plugin Initialization: `__init__.py`

```python
from . import mcp_integration

def getMetaData():
    """Return plugin metadata."""
    return {}

def register(app):
    """
    Register the plugin with Cura.
    Called once when Cura loads the plugin.
    
    Args:
        app: CuraApplication instance
    """
    return {
        "extension": mcp_integration.CuraMCPExtension(app)
    }
```

---

## Cura Python API

### Core Objects

Cura's Python API is built on top of Uranium (the framework Cura uses). Here are the key objects:

#### 1. CuraApplication

```python
from cura.CuraApplication import CuraApplication

app = CuraApplication.getInstance()

# Access key components
api = app.getCuraAPI()
machine_manager = app.getMachineManager()
controller = app.getController()
backend = app.getBackend()
```

#### 2. CuraAPI (High-Level Interface)

The `CuraAPI` class provides a simplified interface to common operations:

```python
api = app.getCuraAPI()

# Scene management
api.scene.getRoot()  # Get root scene node
api.scene.getSceneNodes()  # Get all scene nodes

# Machine management
machines = api.getMachineManager().getAllMachines()
active_machine = api.getMachineManager().activeMachine

# Settings
api.getGlobalContainerStack()  # Global settings
api.getExtruderStack(0)  # Extruder-specific settings

# File operations
api.addModelFile(file_path)  # Load a model
api.removeAllModels()  # Clear the build plate

# Slicing
api.slice()  # Start slicing
api.getSliceInfo()  # Get slice results
```

#### 3. Scene Management

```python
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection

# Get scene root
scene = app.getController().getScene()
root = scene.getRoot()

# Iterate through models
for node in DepthFirstIterator(root):
    if isinstance(node, SceneNode):
        print(f"Node: {node.getName()}")
        print(f"Position: {node.getPosition()}")
        print(f"Scale: {node.getScale()}")
```

#### 4. Settings Access

```python
# Global settings
global_stack = app.getGlobalContainerStack()
layer_height = global_stack.getProperty("layer_height", "value")

# Change settings
global_stack.setProperty("layer_height", "value", 0.2)

# Extruder settings
extruder_stack = app.getExtruderManager().getActiveExtruderStack()
nozzle_size = extruder_stack.getProperty("machine_nozzle_size", "value")
```

#### 5. Backend (Slicing Engine)

```python
backend = app.getBackend()

# Start slicing
backend.slice()

# Check slice status
backend.getState()  # Returns BackendState enum

# Get G-code
backend.getGCode()
```

### Common API Patterns

#### Loading a Model

```python
from cura.CuraApplication import CuraApplication

app = CuraApplication.getInstance()

# Load STL/3MF file
app.readLocalFile(QUrl.fromLocalFile("/path/to/model.stl"))
```

#### Slicing and Exporting

```python
# Slice the current scene
app.getBackend().slice()

# Wait for slicing to complete (listen to backend state changes)
# Then export G-code
app.getBackend().saveToFile("/path/to/output.gcode")
```

#### Modifying Scene Objects

```python
from UM.Scene.Selection import Selection
from UM.Math.Vector import Vector

# Select an object
Selection.add(scene_node)

# Move it
scene_node.setPosition(Vector(10, 0, 10))

# Scale it
scene_node.setScale(Vector(2, 2, 2))

# Rotate it (in degrees)
scene_node.setRotation(Quaternion.fromAngleAxis(math.radians(45), Vector.Unit_Y))
```

---

## Installation & Testing

### For Development

1. **Create plugin folder:**
   ```bash
   cd %APPDATA%\cura\5.8\plugins\
   mkdir CuraMCP
   ```

2. **Copy your plugin files:**
   ```
   CuraMCP/
   ├── __init__.py
   ├── plugin.json
   ├── mcp_integration.py
   └── lib/
       └── mcp_client.py
   ```

3. **Restart Cura:**
   - Close Cura completely
   - Reopen Cura
   - Check `Help` → `Show Console` for any errors

4. **Verify plugin loaded:**
   - Go to `Extensions` → `Manage Plugins`
   - Look for "Cura MCP" in the list
   - Enable it if disabled

### Debugging

**Console Output:**
- `Help` → `Show Console` shows Python print() output and errors

**Log Files:**
- Windows: `%APPDATA%\cura\<version>\cura.log`
- macOS: `~/Library/Application Support/cura/<version>/cura.log`
- Linux: `~/.local/share/cura/<version>/cura.log`

**Common Issues:**

1. **Plugin not showing up:**
   - Check `plugin.json` syntax (must be valid JSON)
   - Verify API version matches your Cura version
   - Check for Python syntax errors in `__init__.py`

2. **Import errors:**
   - Ensure all required modules are available
   - Cura uses its own Python environment (can't pip install)
   - Bundle any external dependencies with your plugin

3. **Plugin crashes Cura:**
   - Add try/except blocks around initialization code
   - Log errors to console for debugging
   - Test incrementally

---

## Generic API Implementation Strategy

### Lessons from MCP-Link-Fusion

The Fusion 360 MCP integration uses a **generic API executor** that provides 100% API coverage without hardcoding specific methods. We'll apply the same pattern to Cura:

#### 1. Generic API Path Resolution

```python
def _resolve_api_path(path, context):
    """
    Resolve an API path to an actual Cura object/method.
    
    Supports:
    - Direct API paths: "app.getMachineManager().activeMachine"
    - Stored references: "$my_machine.name"
    - Special keywords: "app", "api", "backend", "scene"
    """
    if path.startswith('$'):
        # Stored object reference
        parts = path[1:].split('.', 1)
        obj = context.get(parts[0])
        if len(parts) > 1:
            return _navigate_path(obj, parts[1])
        return obj
    
    # Start from known roots
    if path.startswith('app.'):
        root = CuraApplication.getInstance()
        remaining = path[4:]
    elif path.startswith('api.'):
        root = CuraApplication.getInstance().getCuraAPI()
        remaining = path[4:]
    elif path.startswith('backend.'):
        root = CuraApplication.getInstance().getBackend()
        remaining = path[8:]
    elif path.startswith('scene.'):
        root = CuraApplication.getInstance().getController().getScene()
        remaining = path[6:]
    else:
        root = CuraApplication.getInstance()
        remaining = path
    
    return _navigate_path(root, remaining)
```

#### 2. Command Format

AI agents send commands in this format:

```json
{
  "api_path": "getMachineManager().activeMachine",
  "args": [],
  "kwargs": {},
  "store_as": "current_machine",
  "return_properties": ["name", "definition.id"]
}
```

**Examples:**

**Load a model:**
```json
{
  "api_path": "readLocalFile",
  "args": ["file:///C:/models/cube.stl"]
}
```

**Start slicing:**
```json
{
  "api_path": "getBackend().slice"
}
```

**Get slice info:**
```json
{
  "api_path": "getBackend().getGCode",
  "store_as": "gcode_result"
}
```

**Query settings:**
```json
{
  "api_path": "getGlobalContainerStack().getProperty",
  "args": ["layer_height", "value"],
  "return_properties": []
}
```

**Change settings:**
```json
{
  "api_path": "getGlobalContainerStack().setProperty",
  "args": ["layer_height", "value", 0.15]
}
```

#### 3. Python Execution Mode (Advanced)

For complex workflows, support arbitrary Python execution:

```json
{
  "operation": "execute_python",
  "code": "from cura.CuraApplication import CuraApplication\napp = CuraApplication.getInstance()\nprint(f'Cura version: {app.getVersion()}')",
  "session_id": "my_session",
  "persistent": false
}
```

This gives AI agents the ability to:
- Write multi-step workflows
- Use Python control flow (loops, conditionals)
- Call other MCP tools (sqlite, browser, etc.)
- Discover API dynamically using `dir()`, `help()`, `type()`, etc.

**Note**: Session persistence is disabled by default. AI agents should use the `sqlite` MCP tool for persistent storage.

#### 4. API Discovery and Introspection

Python's introspection capabilities allow AI to discover the API dynamically:

```json
{
  "operation": "execute_python",
  "code": "from cura.CuraApplication import CuraApplication\napp = CuraApplication.getInstance()\napi = app.getCuraAPI()\nprint('Available methods:', dir(api))"
}
```

**Discovery Examples:**

```python
# List all methods on an object
dir(app.getMachineManager())

# Get detailed help
help(app.getBackend().slice)

# Check object type
type(app.getGlobalContainerStack())

# Inspect attributes
vars(some_object)

# Get method signature
import inspect
inspect.signature(some_method)
```

This means AI agents can:
- Explore the API without documentation
- Discover undocumented methods
- Understand method signatures
- Find available properties
- Navigate the object hierarchy

---

## Marketplace Submission

### Preparation

1. **Package your plugin:**
   ```
   CuraMCP.zip
   ├── CuraMCP/
   │   ├── __init__.py
   │   ├── plugin.json
   │   ├── mcp_integration.py
   │   ├── lib/
   │   │   └── mcp_client.py
   │   ├── README.md
   │   └── LICENSE
   ```

2. **Required files:**
   - `plugin.json` - Metadata
   - `README.md` - User documentation
   - `LICENSE` - License file (MIT, GPL, etc.)
   - Icon (optional): `icon.png` (256x256 recommended)

3. **Testing checklist:**
   - [ ] Plugin loads without errors
   - [ ] MCP connection establishes successfully
   - [ ] Basic API calls work (load model, slice, export)
   - [ ] Error handling works (graceful failures)
   - [ ] Tested on multiple Cura versions
   - [ ] No conflicts with other plugins

### Submission Process

1. **Create Ultimaker account:**
   - Go to https://marketplace.ultimaker.com/
   - Sign up or log in

2. **Submit plugin:**
   - Navigate to "Submit Plugin"
   - Upload your .zip file
   - Fill in description, screenshots, etc.
   - Submit for review

3. **Review process:**
   - Ultimaker reviews for security and quality
   - May take 1-2 weeks
   - Address any feedback from reviewers

4. **Publication:**
   - Once approved, plugin appears in marketplace
   - Users can install via Cura's plugin manager

### Marketplace Requirements

- **Security:** No malicious code, no data exfiltration
- **Quality:** Well-documented, no crashes
- **Compatibility:** Works with current Cura versions
- **License:** Clear licensing terms
- **Support:** Contact info for bug reports

---

## Resources & References

### Official Documentation

- **Cura GitHub Wiki:** https://github.com/Ultimaker/Cura/wiki/Plugins-And-Packages
- **Example Plugins:** https://github.com/Ultimaker/Cura/tree/main/plugins
- **Uranium Framework:** https://github.com/Ultimaker/Uranium (Cura's underlying framework)
- **Marketplace:** https://marketplace.ultimaker.com/app/cura/plugins

### Cura Source Code

The best API documentation is the source code itself:

- **CuraApplication:** https://github.com/Ultimaker/Cura/blob/main/cura/CuraApplication.py
- **CuraAPI:** https://github.com/Ultimaker/Cura/blob/main/cura/API/CuraAPI.py
- **Backend:** https://github.com/Ultimaker/Cura/blob/main/cura/CuraEngineBackend.py
- **Scene:** https://github.com/Ultimaker/Uranium/tree/main/UM/Scene

### Community Resources

- **Cura Forums:** https://community.ultimaker.com/
- **GitHub Issues:** https://github.com/Ultimaker/Cura/issues
- **Discord:** Ultimaker Community Discord server

### MCP Resources

- **MCP-Link Server:** https://github.com/aurafriday/mcp-link-server
- **MCP-Link-Fusion (reference):** Your existing Fusion 360 integration
- **Reverse MCP Template:** `cura_mcp.py` in this project

---

## Implementation Roadmap

### Phase 1: Basic Plugin Structure ✓
- [ ] Create plugin skeleton (`__init__.py`, `plugin.json`)
- [ ] Test plugin loads in Cura
- [ ] Add console logging

### Phase 2: MCP Connection
- [ ] Copy MCP client library from template
- [ ] Implement auto-connect on plugin load
- [ ] Register "cura" tool with MCP server
- [ ] Test bidirectional communication

### Phase 3: Generic API Executor
- [ ] Implement `_resolve_api_path()`
- [ ] Implement `_resolve_argument()`
- [ ] Add context storage for multi-step operations
- [ ] Test basic API calls (load model, slice, export)

### Phase 4: Python Execution Mode
- [ ] Add `execute_python` operation
- [ ] Implement session management
- [ ] Add MCP bridge for tool-to-tool calls
- [ ] Test complex workflows

### Phase 5: Polish & Documentation
- [ ] Add error handling and user-friendly messages
- [ ] Write comprehensive README
- [ ] Create example scripts for AI agents
- [ ] Add optional UI for connection status

### Phase 6: Marketplace Submission
- [ ] Package plugin as .zip
- [ ] Test on multiple Cura versions
- [ ] Submit to Ultimaker Marketplace
- [ ] Address reviewer feedback

---

## Key Differences from Fusion 360

| Aspect | Fusion 360 | Cura |
|--------|-----------|------|
| **Plugin Type** | Add-in | Extension |
| **API Style** | Object-oriented, COM-like | Python native, Qt-based |
| **Threading** | Must use UI thread for API calls | Qt event loop, signals/slots |
| **Reload** | Stop/Start in Scripts dialog | Restart Cura |
| **Distribution** | Autodesk App Store | Ultimaker Marketplace |
| **Debugging** | Text Commands console | Help → Show Console |

---

## Security Considerations

⚠️ **Important:** This plugin provides **full code execution** capabilities to AI agents. Only use with:

1. **Trusted AI agents** - Don't expose to untrusted models
2. **Local MCP server** - Never expose over the internet
3. **Unlock tokens** - Require authentication for sensitive operations
4. **User consent** - Make it clear what the plugin does

Consider adding:
- Confirmation dialogs for destructive operations
- Audit logging of all API calls
- Sandboxing options for Python execution
- Rate limiting to prevent abuse

---

## Next Steps

1. **Read the Cura source code** - Familiarize yourself with CuraApplication and CuraAPI
2. **Create a minimal plugin** - Test that it loads and logs to console
3. **Add MCP connection** - Copy from `cura_mcp.py` template
4. **Implement generic API** - Start with simple calls (get version, list machines)
5. **Test with AI** - Use Claude/GPT to control Cura via MCP
6. **Iterate and expand** - Add more capabilities based on testing

---

## Questions & Troubleshooting

### Q: Can I use pip to install dependencies?

**A:** No, Cura uses its own bundled Python environment. You must bundle any dependencies with your plugin or use only standard library modules.

### Q: How do I debug if the plugin won't load?

**A:** 
1. Check `cura.log` for error messages
2. Verify `plugin.json` is valid JSON
3. Test `__init__.py` syntax with `python -m py_compile __init__.py`
4. Start with minimal code and add incrementally

### Q: Can I access the G-code before it's saved?

**A:** Yes, use `app.getBackend().getGCode()` after slicing completes. You can modify it before saving.

### Q: How do I know when slicing is complete?

**A:** Connect to the backend's `slicingFinished` signal:

```python
backend = app.getBackend()
backend.slicingFinished.connect(self._on_slicing_finished)

def _on_slicing_finished(self):
    print("Slicing complete!")
```

### Q: Can I add custom UI elements?

**A:** Yes, Cura uses Qt/QML for UI. You can add dialogs, buttons, or even full panels. See the example plugins for patterns.

---

## Conclusion

This guide provides everything needed to create a Cura MCP plugin that gives AI agents complete access to Cura's slicing capabilities. By following the generic API pattern from MCP-Link-Fusion, we can achieve 100% API coverage without hardcoding specific methods.

The key insight: **Let the AI tell us what to call, then dynamically resolve and execute those calls.** This "eval-style" approach is powerful and flexible, enabling AI agents to discover and use the full API surface.

Good luck with your plugin development! 🚀

