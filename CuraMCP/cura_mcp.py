#!/usr/bin/env python3
"""
File: reverse_mcp.py
Project: Aura Friday MCP-Link Server - Remote Tool Provider Demo
Component: Registers a demo tool with the MCP server and handles reverse calls
Author: Christopher Nathan Drake (cnd)
Created: 2025-11-03
Last Modified: 2025-11-03 by cnd (Implemented remote tool provider)
SPDX-License-Identifier: Proprietary
Copyright: (c) 2025 Christopher Nathan Drake. All rights reserved.
"signature": "sig",
"signdate": "2025-11-05T02:10:08.326Z",

VERSION: 2025.11.03.001 - Remote Tool Provider Demo

BUILD/RUN INSTRUCTIONS:
  ** NOTE ** This file needs to be copied into the Cura extension folder, which is located at: %USERPROFILE%/AppData/Roaming/cura/5.11/plugins/CuraMCP/
  
  Requirements:
    - Python 3.7+ (tested with 3.11+)
    - Standard library only (no pip install needed)
  
  Run:
    python reverse_mcp.py [--background]
    python reverse_mcp.py --help

HOW TO USE THIS CODE:
  This code is a complete, self-contained reference template for integrating MCP (Model Context Protocol) 
  tool support into other applications like Fusion 360, Blender, Ghidra, and similar products.
  
  HOW THIS WORKS:
  ---------------
  1. You create a new add-on or extension or plugin or similar for the application you want to let an AI control on your behalf. (hereafter addIn)
  2. This template gives your new addIn the facility to discover the correct endpoint where a local controller MCP server is running, and then:
  3. lets your addIn register itself with that server as a new tool, which any AI using that MCP server can then discover and access and use.
  4. and finally, this template processes incoming tool requests form the AI, which you implement in your addIn, and this template sends the results of those tool-calls back to the AI.
  5. BONUS: Your addIn can also CALL OTHER MCP tools on the server (sqlite, browser, user, etc.) - making it possible to orchestrate complex workflows!
  *. The server installer can be found at https://github.com/aurafriday/mcp-link-server/releases
  
  ARCHITECTURE OVERVIEW:
  ----------------------
  1. Native Messaging Discovery: Locates the MCP server by finding the Chrome native messaging manifest
     (com.aurafriday.shim.json) which is installed by the Aura Friday MCP-Link server.
  
  2. Server Configuration: Executes the native messaging binary to get the server's SSE endpoint URL
     and authentication token. The binary is a long-running stdio service, so we terminate it after
     reading the initial JSON config.
  
  3. SSE Connection: Establishes a persistent Server-Sent Events (SSE) connection to receive messages
     from the server. This runs in a background thread and routes incoming messages to the appropriate
     handlers.
  
  4. Dual-Channel Communication:
     - POST requests (via HTTP/HTTPS) to send JSON-RPC commands to the server
     - SSE stream (long-lived GET connection) to receive JSON-RPC responses and reverse tool calls
  
  5. Tool Registration: Uses the server's "remote" tool to register your custom tool with these components:
     - tool_name: Unique identifier for your tool
     - readme: Minimal summary for the AI (when to use this tool)
     - description: Comprehensive documentation for the AI (what it does, how to use it, examples)
     - parameters: JSON Schema defining the tool's input parameters
     - callback_endpoint: Identifier for routing reverse calls back to your client
     - TOOL_API_KEY: Authentication key for your tool
  
  6. Reverse Call Handling: After registration, your tool appears in the server's tool list. When an
     AI agent calls your tool, the server sends a "reverse" message via the SSE stream containing:
     - tool: Your tool's name
     - call_id: Unique ID for this invocation (used to send the reply)
     - input: The parameters passed by the AI
  
  7. Reply Mechanism: Your code processes the request and sends a "tools/reply" message back to the
     server with the call_id and result. The server forwards this to the AI.
  
  INTEGRATION STEPS:
  ------------------
  1. Copy this file to your project
  2. Modify the tool registration section (search for "demo_tool_python"):
     - Change tool_name to your tool's unique identifier
     - Update description and readme to explain your tool's purpose
     - Define your tool's parameters schema
     - Set a unique callback_endpoint and TOOL_API_KEY
  
  3. Replace the handle_echo_request() function with your tool's actual logic:
     - Extract parameters from the input_data
     - Perform your tool's operations (file I/O, API calls, computations, etc.)
     - OPTIONALLY: Call other MCP tools using call_mcp_tool() function
     - Return a result dictionary with "content" array and "isError" boolean
  
  4. (Optional) Use call_mcp_tool() to orchestrate other MCP tools:
     - Your handler receives sse_connection, server_url, and auth_header parameters
     - Use call_mcp_tool() to call sqlite, browser, user, or any other MCP tool
     - Example: sqlite_result = call_mcp_tool(sse_connection, server_url, auth_header,
                                              "sqlite", {"input": {"sql": ".tables", "tool_unlock_token": "..."}})
     - This enables complex workflows like: read data from app → query database → show results to user
  
  5. Run your tool provider script:
     - It will auto-discover the server, register your tool, and listen for calls
     - The tool remains registered as long as the script is running
     - Press Ctrl+C to cleanly shut down
  
  RESULT FORMAT:
  --------------
  All tool results must follow this structure:
  {
    "content": [
      {"type": "text", "text": "Your response text here"},
      {"type": "image", "data": "base64...", "mimeType": "image/png"}  # optional
    ],
    "isError": false  # or true if an error occurred
  }
  
  THREADING MODEL:
  ----------------
  - Main thread: Handles tool registration and processes reverse calls from the queue
  - SSE reader thread: Continuously reads the SSE stream and routes messages to queues
  - Each JSON-RPC request gets its own response queue for thread-safe blocking waits
  
  DEPENDENCIES:
  -------------
  Python 3.7+ with standard library only (no pip install required):
  - json, ssl, http.client: Network communication
  - threading, queue: Concurrent message handling
  - subprocess: Execute native messaging binary
  - pathlib, platform: Cross-platform file system operations
  
  ERROR HANDLING & RECONNECTION:
  -------------------------------
  - SSL certificate verification is disabled (self-signed certs are common in local servers)
  - Native binary timeout is 5 seconds (increase if needed)
  - SSE response timeout is 10 seconds per request (configurable)
  - All errors are logged to stderr for debugging
  - Automatic reconnection with exponential backoff if SSE connection drops:
    * Retry delays: 2s, 4s, 8s, 16s, 32s, 60s (max), 60s, 60s...
    * After successful reconnection, retry counter resets
    * Tool is automatically re-registered after reconnection
    * Retries forever until manually stopped (Ctrl+C)

"""

DOCO=""" 
This script demonstrates how to register a tool with the MCP server using the remote tool system.
It acts as a tool provider that:
1. Connects to the MCP server via native messaging discovery
2. Registers a "demo_tool_python" with the server
3. Listens for reverse tool calls from the server
4. Processes "echo" requests and sends back replies
5. Demonstrates calling OTHER MCP tools (sqlite, browser, etc.) from within the handler
6. Runs continuously until stopped with Ctrl+C

The demo tool responds to these message patterns:
- "list databases" or "list db" - Calls sqlite to list all databases (START HERE to discover what's available)
- "list tables" - Calls sqlite to list tables in :memory: database
- "list tables in <database>" - Calls sqlite to list tables in specific database (e.g., "list tables in test.db")
- Any other message - Simple echo response

Usage: python reverse_mcp.py [--background]
"""

import os
import sys
import json
import platform
import struct
import ssl
import uuid
import threading
import time
import queue
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse, parse_qs
import http.client

# Cura/UM imports - imported once at module load
# These will be available in the execution context for AI code
try:
    # Core Cura modules
    import cura
    from cura.CuraApplication import CuraApplication
    
    # UM (Uranium) modules - the framework Cura is built on
    import UM
    from UM.Math.Vector import Vector
    from UM.Math.Quaternion import Quaternion
    from UM.Math.Matrix import Matrix
    from UM.Operations.SetTransformOperation import SetTransformOperation
    from UM.Operations.TranslateOperation import TranslateOperation
    from UM.Operations.RotateOperation import RotateOperation
    from UM.Operations.ScaleOperation import ScaleOperation
    from UM.Operations.MirrorOperation import MirrorOperation
    from UM.Operations.GroupedOperation import GroupedOperation
    from UM.Scene.SceneNode import SceneNode
    from UM.Scene.Selection import Selection
    from UM.Logger import Logger
    
    # PyQt6 - Cura's UI framework
    from PyQt6.QtCore import QUrl, QObject, pyqtSignal, QTimer
    from PyQt6.QtWidgets import QApplication
    
    # Standard library modules commonly used
    import math
    import traceback
    import io
    import contextlib
    
except ImportError as e:
    # If we're running outside Cura (for testing), these won't be available
    print(f"Warning: Could not import Cura modules: {e}", file=sys.stderr)
    print("This is expected if running outside of Cura", file=sys.stderr)


def find_this_native_messaging_manifest_for_this_platform() -> Optional[Path]:
  """
  Find the native messaging manifest file for com.aurafriday.shim.
  Searches platform-specific locations where Chrome looks for manifests.
  
  Returns:
    Path to the manifest file, or None if not found
  """
  system_name = platform.system().lower()
  possible_paths = []
  
  if system_name == "windows":
    # Windows: Check registry first, then fallback to file locations
    # For simplicity, we'll check the file location directly
    appdata_local = os.environ.get('LOCALAPPDATA')
    if appdata_local:
      possible_paths.append(Path(appdata_local) / "AuraFriday" / "com.aurafriday.shim.json")
    possible_paths.append(Path.home() / "AppData" / "Local" / "AuraFriday" / "com.aurafriday.shim.json")
    
  elif system_name == "darwin":  # macOS
    # Check all browser-specific locations
    possible_paths.extend([
      Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / "Library" / "Application Support" / "Chromium" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / "Library" / "Application Support" / "Vivaldi" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
    ])
    
  else:  # Linux
    possible_paths.extend([
      Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / ".config" / "chromium" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / ".config" / "microsoft-edge" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / ".config" / "BraveSoftware" / "Brave-Browser" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / ".var" / "app" / "com.google.Chrome" / "config" / "google-chrome" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
      Path.home() / ".var" / "app" / "org.chromium.Chromium" / "config" / "chromium" / "NativeMessagingHosts" / "com.aurafriday.shim.json",
    ])
  
  # Find the first existing manifest
  for path in possible_paths:
    if path.exists():
      return path
  
  return None


def read_this_native_messaging_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
  """
  Read and parse the native messaging manifest JSON file.
  
  Args:
    manifest_path: Path to the manifest file
    
  Returns:
    Parsed manifest dictionary, or None on error
  """
  try:
    with open(manifest_path, 'r', encoding='utf-8') as f:
      return json.load(f)
  except Exception as e:
    print(f"Error reading manifest: {e}", file=sys.stderr)
    return None


def discover_this_mcp_server_endpoint_by_running_native_binary(manifest: Dict[str, Any]) -> Optional[Dict[str, Any]]:
  """
  Discover the MCP server endpoint by running the native messaging binary,
  exactly as Chrome would do it.
  
  The binary is a long-running stdio service that outputs JSON config immediately,
  then waits for input. We read the JSON and terminate the process.
  
  Args:
    manifest: The parsed native messaging manifest
    
  Returns:
    The full JSON response from the native binary, or None on error
  """
  import subprocess
  
  binary_path = manifest.get('path')
  if not binary_path:
    print("ERROR: No 'path' in manifest", file=sys.stderr)
    return None
  
  binary_path = Path(binary_path)
  if not binary_path.exists():
    print(f"ERROR: Native binary not found: {binary_path}", file=sys.stderr)
    return None
  
  print(f"Running native binary: {binary_path}", file=sys.stderr)
  print(f"[DEBUG] Native messaging protocol uses 4-byte length prefix (little-endian uint32)", file=sys.stderr)
  
  try:
    # Determine if we can use CREATE_NO_WINDOW (Python 3.7+, Windows only)
    creation_flags = 0
    if platform.system() == 'Windows':
      try:
        creation_flags = subprocess.CREATE_NO_WINDOW
      except AttributeError:
        # Python < 3.7 doesn't have CREATE_NO_WINDOW
        pass
    
    # Start the binary as a subprocess
    # Note: This is a long-running stdio service, not a one-shot command
    proc = subprocess.Popen(
      [str(binary_path)],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      stdin=subprocess.PIPE,
      text=False,  # Read as bytes to handle encoding issues
      bufsize=0,   # Unbuffered
      creationflags=creation_flags
    )
    
    # Read output using Chrome Native Messaging protocol
    # Protocol: 4-byte length (little-endian uint32) followed by JSON message
    json_data = None
    
    try:
      start_time = time.time()
      timeout = 5.0
      
      # Step 1: Read the 4-byte length prefix (little-endian uint32)
      length_bytes = b""
      while len(length_bytes) < 4 and time.time() - start_time < timeout:
        chunk = proc.stdout.read(4 - len(length_bytes))
        if not chunk:
          time.sleep(0.01)
          continue
        length_bytes += chunk
      
      if len(length_bytes) != 4:
        print(f"ERROR: Failed to read 4-byte length prefix (got {len(length_bytes)} bytes)", file=sys.stderr)
        proc.terminate()
        return None
      
      # Convert little-endian bytes to int
      import struct
      message_length = struct.unpack('<I', length_bytes)[0]
      
      print(f"[DEBUG] Message length from native binary: {message_length} bytes", file=sys.stderr)
      
      if message_length <= 0 or message_length > 10_000_000:
        print(f"ERROR: Invalid message length: {message_length}", file=sys.stderr)
        proc.terminate()
        return None
      
      # Step 2: Read the JSON payload of the specified length
      json_bytes = b""
      while len(json_bytes) < message_length and time.time() - start_time < timeout:
        chunk = proc.stdout.read(message_length - len(json_bytes))
        if not chunk:
          time.sleep(0.01)
          continue
        json_bytes += chunk
      
      if len(json_bytes) != message_length:
        print(f"ERROR: Stream ended after {len(json_bytes)} bytes (expected {message_length})", file=sys.stderr)
        proc.terminate()
        return None
      
      # Step 3: Decode and parse the JSON
      try:
        text = json_bytes.decode('utf-8')
        print(f"[DEBUG] Successfully read {len(json_bytes)} bytes of JSON", file=sys.stderr)
        print(f"[DEBUG] JSON preview: {text[:100]}...", file=sys.stderr)
        json_data = json.loads(text)
      except UnicodeDecodeError:
        # Try latin-1 as fallback
        text = json_bytes.decode('latin-1', errors='ignore')
        print(f"[DEBUG] Successfully read {len(json_bytes)} bytes of JSON (latin-1 fallback)", file=sys.stderr)
        print(f"[DEBUG] JSON preview: {text[:100]}...", file=sys.stderr)
        try:
          json_data = json.loads(text)
        except json.JSONDecodeError as e:
          print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
          print(f"Output was: {text[:200]}", file=sys.stderr)
          proc.terminate()
          return None
      except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
        print(f"Output was: {text[:200]}", file=sys.stderr)
        proc.terminate()
        return None
      
    finally:
      # Terminate the process (it's waiting for stdin)
      try:
        proc.terminate()
        proc.wait(timeout=1.0)
      except:
        try:
          proc.kill()
        except:
          pass
    
    return json_data
    
  except Exception as e:
    print(f"ERROR: Failed to run native binary: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    return None


def extract_this_server_url_from_config(config_json: Dict[str, Any]) -> Optional[str]:
  """
  Extract the MCP server URL from the configuration JSON returned by the native binary.
  
  Args:
    config_json: The JSON configuration from the native binary
    
  Returns:
    The server URL, or None if not found
  """
  try:
    # The structure is: { "mcpServers": { "mypc": { "url": "..." } } }
    mcp_servers = config_json.get('mcpServers', {})
    if not mcp_servers:
      return None
    
    # Get the first server (usually "mypc")
    first_server = next(iter(mcp_servers.values()), None)
    if not first_server:
      return None
    
    return first_server.get('url')
    
  except Exception as e:
    print(f"ERROR: Failed to extract URL from config: {e}", file=sys.stderr)
    return None


def register_cura_tool(sse_connection: Dict[str, Any], server_url: str, auth_header: str, cura_app) -> bool:
  """
  Register the cura tool with the MCP server using the remote tool system.
  
  Args:
    sse_connection: Active SSE connection
    server_url: Base server URL
    auth_header: Authorization header
    cura_app: CuraApplication instance
    
  Returns:
    True if registration successful, False otherwise
  """
  print("Registering 'cura' tool with MCP server...", file=sys.stderr)
  
  tool_description = """
Cura Slicer MCP Tool - Complete API Access + Python Execution (v1.0.7)

This tool provides AI agents with COMPLETE, UNRESTRICTED access to Ultimaker Cura's slicing capabilities.

## Complete Slicing Workflow Example

```python
# Load model
url = QUrl.fromLocalFile(r'C:\path\to\model.stl')
app.readLocalFile(url)
time.sleep(1)  # Wait for load

# Find and rotate model 45° (if needed to fit build plate)
for node in scene.getRoot().getAllChildren():
    if hasattr(node, 'callDecoration') and node.callDecoration('isSliceable'):
        rotation = Quaternion.fromAngleAxis(math.radians(45), Vector(0, 1, 0))
        new_orientation = rotation * node.getOrientation()
        new_pos = Vector(0, node.getPosition().y, 0)  # Center
        op = SetTransformOperation(node, new_pos, new_orientation)
        op.push()
        break

# Configure settings
global_stack = app.getGlobalContainerStack()
global_stack.setProperty('infill_sparse_density', 'value', 100)
global_stack.setProperty('wall_line_count', 'value', 3)

# CRITICAL: Reset backend state before slicing!
backend.setState(0)
backend.forceSlice()

# Wait for completion
for i in range(60):
    state = backend._backend_state
    if state == 2:  # Done
        print_info = app.getPrintInformation()
        time_obj = print_info.currentPrintTime
        print(f'Print time: {time_obj.getDisplayString()}')
        print(f'Material: {print_info.materialWeights[0]:.2f}g')
        break
    elif state in [3, 4]:  # Error
        print(f'Failed: {backend._slicing_error_message.getText()}')
        break
    time.sleep(0.5)
```

## Three Powerful Capabilities

### 1. Generic API Calls (Simple Operations)

Call any Cura API method using dotted path notation:

{
  "api_path": "getMachineManager().activeMachine.name",
  "args": [],
  "kwargs": {},
  "store_as": "machine_name",
  "return_properties": ["value"]
}

Path shortcuts:
- `app` → CuraApplication.getInstance()
- `backend` → app.getBackend()
- `scene` → app.getController().getScene()
- `$variable` → Previously stored object

Examples:
- Load model: {"api_path": "readLocalFile", "args": ["file:///path/to/model.stl"]}
- Start slicing: {"api_path": "getBackend().slice"}
- Get G-code: {"api_path": "getBackend().getGCode", "store_as": "gcode"}

### 2. Python Execution (Complex Workflows)

Execute arbitrary Python code with full Cura API access:

{
  "operation": "execute_python",
  "code": "print(f'Cura version: {app.getVersion()}')"
}

**Pre-imported objects** (no need to import!):

**Core instances:**
- `app` - CuraApplication.getInstance()
- `scene` - app.getController().getScene()
- `backend` - app.getBackend()

**Full API access:**
- `cura` - Entire Cura module namespace
- `UM` - Entire Uranium (UM) framework namespace

**Common classes (for convenience):**
- `Vector`, `Quaternion`, `Matrix` - Math operations
- `SetTransformOperation`, `TranslateOperation`, `RotateOperation`, `ScaleOperation` - Transformations
- `SceneNode`, `Selection` - Scene management
- `Logger` - Logging
- `QUrl`, `QObject`, `QTimer`, `QApplication` - Qt framework

**Standard library:**
- `math`, `time`, `json`, `io`, `traceback`, `contextlib`

**MCP bridge:**
- `mcp` - Call other MCP tools (sqlite, browser, etc.)

The entire Cura API is available through the `cura` and `UM` namespaces!

### 3. API Discovery

Use Python introspection to explore the API:

{
  "operation": "execute_python",
  "code": "print(dir(app.getMachineManager()))"
}

This allows AI to discover methods dynamically without documentation!

## Special Commands

- `{"api_path": "get_pid"}` - Get Cura process ID
- `{"api_path": "clear_context"}` - Clear stored objects

## Async Operations & Waiting

**IMPORTANT**: Many Cura operations are ASYNCHRONOUS (slicing, loading files, etc.)

### Backend States
The backend has these states (access via `backend._backend_state`):
- `0` = NotStarted
- `1` = Processing (slicing in progress)
- `2` = Done (slice completed successfully)
- `3` = Error (slice failed - check logs)
- `4` = Disabled (slice failed - check `backend._slicing_error_message`)

### Slicing - CRITICAL: Reset Backend State First!

**IMPORTANT**: The backend can get stuck in "Processing" state (1) from previous operations.
You MUST reset it to "NotStarted" (0) before each slice:

```python
# THE CORRECT WAY TO SLICE:
backend.setState(0)  # Reset to NotStarted - THIS IS CRITICAL!
backend.forceSlice()  # Now it will actually slice

# Wait for completion
max_wait = 30
for i in range(max_wait * 2):
    state = backend._backend_state
    if state == 2:  # Done
        print("Slice completed!")
        break
    elif state == 3:  # Error
        # Get error details from backend log
        log = backend.getLog()
        print(f"Slice failed! Last log entries: {log[-10:]}")
        break
    elif state == 4:  # Disabled (failed)
        # Get error message
        error_msg = backend._slicing_error_message
        print(f"Slice failed: {error_msg.getTitle()}")
        print(f"Details: {error_msg.getText()}")
        break
    time.sleep(0.5)
```

**Why this is needed**: Without `setState(0)`, the backend stays in "Processing" state
and `forceSlice()` does nothing. This is a Cura backend quirk.

### Getting Error Details
Always check backend log after errors:
```python
log_lines = backend.getLog()
# Show last 20 lines
for line in log_lines[-20:]:
    print(line.decode('utf-8', errors='ignore'))
```

### Common Pitfalls
1. **MUST call `backend.setState(0)` before slicing** - Backend gets stuck in Processing state!
2. **Spiral vase + 100% infill = INCOMPATIBLE** - Spiral vase requires 1 wall, 0 top/bottom
3. **State 4 (Disabled) = Slice failed** - Check `backend._slicing_error_message.getText()`
4. **Operations may fail silently** - Always check backend state after slice()
5. **File loading is async** - Wait a moment after readLocalFile()

## Transforming Objects (Rotate/Move/Scale)

**CRITICAL**: Use `SetTransformOperation` and `push()` - direct setters don't work!

### Finding the Model
```python
# Find sliceable model node (not BuildVolume or Platform!)
model_node = None
for node in scene.getRoot().getAllChildren():
    if hasattr(node, 'callDecoration') and node.callDecoration('isSliceable'):
        model_node = node
        break
```

### Rotate and Center Example
```python
# Rotate 45° around Z-axis (Y is up in Cura)
rotation = Quaternion.fromAngleAxis(math.radians(45), Vector(0, 1, 0))
new_orientation = rotation * model_node.getOrientation()

# Center on build plate (X=0, Z=0, keep Y height)
current_pos = model_node.getPosition()
new_pos = Vector(0, current_pos.y, 0)

# Apply transformation
op = SetTransformOperation(model_node, new_pos, new_orientation)
op.push()

# Trigger UI update
scene.sceneChanged.emit(model_node)
```

## Note

Cura must be running with this MCP plugin active.
Version: 1.0.7 - Slicing now works! Use `backend.setState(0)` before `forceSlice()`
"""
  
  # Build the registration request
  registration_params = {
    "name": "remote",
    "arguments": {
      "input": {
        "operation": "register",
        "tool_name": "cura",
        "readme": "Ultimaker Cura slicer - Use this to slice 3D models, configure print settings, and generate G-code",
        "description": tool_description,
        "parameters": {
          "type": "object",
          "properties": {
            "operation": {
              "type": "string",
              "description": "Operation type: 'execute_python' for Python code, or omit for generic API call"
            },
            "api_path": {
              "type": "string",
              "description": "Dotted path to API method/property (for generic API calls)"
            },
            "args": {
              "type": "array",
              "description": "Positional arguments"
            },
            "kwargs": {
              "type": "object",
              "description": "Keyword arguments"
            },
            "store_as": {
              "type": "string",
              "description": "Variable name to store result"
            },
            "return_properties": {
              "type": "array",
              "description": "Properties to extract from result"
            },
            "code": {
              "type": "string",
              "description": "Python code to execute (for execute_python operation)"
            }
          }
        },
        "callback_endpoint": "cura-mcp://cura-callback",
        "TOOL_API_KEY": "cura_mcp_auth_key_12345"
      }
    }
  }
  
  response = send_this_jsonrpc_request_and_wait_for_this_response(
    sse_connection,
    server_url,
    auth_header,
    "tools/call",
    registration_params
  )
  
  if not response:
    print("ERROR: Failed to register cura tool", file=sys.stderr)
    return False
  
  # Check if registration was successful
  if 'result' in response:
    result = response['result']
    if isinstance(result, dict):
      content = result.get('content', [])
      if content and len(content) > 0:
        text = content[0].get('text', '')
        if 'Successfully registered tool' in text:
          print(f"[OK] {text}", file=sys.stderr)
          return True
  
  print(f"ERROR: Unexpected registration response: {json.dumps(response, indent=2)}", file=sys.stderr)
  return False


def call_mcp_tool(sse_connection: Dict[str, Any], server_url: str, auth_header: str, 
                  tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
  """
  Call another MCP tool on the server.
  
  This function demonstrates how to call other MCP tools from within your remote tool handler.
  It uses the existing SSE connection and JSON-RPC infrastructure to make tool calls.
  
  Args:
    sse_connection: Active SSE connection dictionary
    server_url: Base server URL
    auth_header: Authorization header value
    tool_name: Name of the tool to call (e.g., "sqlite", "browser", "user")
    arguments: Arguments to pass to the tool
    
  Returns:
    JSON-RPC response dictionary, or None on error
    
  Example:
    # Call sqlite tool to list tables
    result = call_mcp_tool(
      sse_connection,
      server_url,
      auth_header,
      "sqlite",
      {"input": {"sql": ".tables", "tool_unlock_token": "29e63eb5"}}
    )
    
    # Call browser tool to list tabs
    result = call_mcp_tool(
      sse_connection,
      server_url,
      auth_header,
      "browser",
      {"input": {"operation": "list_tabs", "tool_unlock_token": "e5076d"}}
    )
  """
  tool_call_params = {
    "name": tool_name,
    "arguments": arguments
  }
  
  response = send_this_jsonrpc_request_and_wait_for_this_response(
    sse_connection,
    server_url,
    auth_header,
    "tools/call",
    tool_call_params,
    timeout_seconds=30.0  # Longer timeout for tool calls
  )
  
  return response


def handle_cura_tool_call(call_data: Dict[str, Any], cura_app, cura_context: Dict[str, Any],
                          sse_connection: Optional[Dict[str, Any]] = None,
                          server_url: Optional[str] = None, auth_header: Optional[str] = None) -> Dict[str, Any]:
  """
  Handle a cura tool call from the server.
  
  Args:
    call_data: The tool call data from the reverse message
    cura_app: CuraApplication instance
    cura_context: Dictionary for storing objects between calls
    sse_connection: Optional SSE connection for making tool calls
    server_url: Optional server URL for making tool calls
    auth_header: Optional auth header for making tool calls
    
  Returns:
    Result dictionary to send back
  """
  import io
  import contextlib
  import traceback
  
  try:
    params = call_data.get('params', {})
    arguments = params.get('arguments', {})
    
    # Check for operation type
    operation = arguments.get('operation')
    
    if operation == 'execute_python':
      # Handle Python execution
      code = arguments.get('code')
      if not code:
        return {
          "content": [{"type": "text", "text": "ERROR: 'code' parameter required"}],
          "isError": True
        }
      
      stdout_capture = io.StringIO()
      stderr_capture = io.StringIO()
      
      try:
        # Prepare globals with Cura context and pre-imported modules
        # All imports are done at module level, so we just reference them here
        exec_globals = {
          # Core Cura objects (instances)
          'app': cura_app,
          'scene': cura_app.getController().getScene(),
          'backend': cura_app.getBackend(),
          
          # Entire Cura and UM namespaces (for full API access)
          'cura': cura,
          'UM': UM,
          
          # Commonly used classes (pre-imported for convenience)
          'CuraApplication': CuraApplication,
          'Vector': Vector,
          'Quaternion': Quaternion,
          'Matrix': Matrix,
          'SetTransformOperation': SetTransformOperation,
          'TranslateOperation': TranslateOperation,
          'RotateOperation': RotateOperation,
          'ScaleOperation': ScaleOperation,
          'MirrorOperation': MirrorOperation,
          'GroupedOperation': GroupedOperation,
          'SceneNode': SceneNode,
          'Selection': Selection,
          'Logger': Logger,
          'QUrl': QUrl,
          'QObject': QObject,
          'QTimer': QTimer,
          'QApplication': QApplication,
          
          # Standard library modules
          'math': math,
          'time': time,
          'json': json,
          'io': io,
          'traceback': traceback,
          'contextlib': contextlib,
          
          # MCP bridge for calling other tools
          'mcp': {'call_tool': lambda name, args: call_mcp_tool(sse_connection, server_url, auth_header, name, args) if sse_connection else None}
        }
        
        # Capture backend state before execution
        backend_state_before = None
        backend_log_before_count = 0
        try:
          backend = cura_app.getBackend()
          backend_state_before = backend._backend_state
          backend_log_before_count = len(backend.getLog())
        except:
          pass
        
        # Execute code
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
          exec(compile(code, "<ai-code>", "exec"), exec_globals)
        
        return_value = exec_globals.get('__return__', None)
        
        # Capture backend state and new log entries after execution
        backend_info = {}
        try:
          backend = cura_app.getBackend()
          backend_state_after = backend._backend_state
          backend_info['backend_state_before'] = backend_state_before
          backend_info['backend_state_after'] = backend_state_after
          backend_info['state_meaning'] = {0: 'NotStarted', 1: 'Processing', 2: 'Done', 3: 'Error', 4: 'Disabled'}.get(backend_state_after, 'Unknown')
          
          # Get new log entries
          all_logs = backend.getLog()
          if len(all_logs) > backend_log_before_count:
            new_logs = all_logs[backend_log_before_count:]
            backend_info['new_log_entries'] = [line.decode('utf-8', errors='ignore').strip() for line in new_logs[-10:]]  # Last 10 new entries
        except Exception as e:
          backend_info['error_getting_backend_info'] = str(e)
        
        result_data = {
          "stdout": stdout_capture.getvalue(),
          "stderr": stderr_capture.getvalue(),
          "return_value": str(return_value) if return_value else None,
          "success": True
        }
        
        if backend_info:
          result_data['backend_info'] = backend_info
        
        return {
          "content": [{
            "type": "text",
            "text": json.dumps(result_data, indent=2)
          }],
          "isError": False
        }
      except Exception as e:
        # Capture backend log on error
        backend_error_info = {}
        try:
          backend = cura_app.getBackend()
          backend_error_info['backend_state'] = backend._backend_state
          backend_error_info['state_meaning'] = {0: 'NotStarted', 1: 'Processing', 2: 'Done', 3: 'Error', 4: 'Disabled'}.get(backend._backend_state, 'Unknown')
          log_lines = backend.getLog()
          if log_lines:
            backend_error_info['last_log_entries'] = [line.decode('utf-8', errors='ignore').strip() for line in log_lines[-15:]]
        except:
          pass
        
        error_data = {
          "stdout": stdout_capture.getvalue(),
          "stderr": stderr_capture.getvalue(),
          "error": str(e),
          "traceback": traceback.format_exc(),
          "success": False
        }
        
        if backend_error_info:
          error_data['backend_info'] = backend_error_info
        
        return {
          "content": [{
            "type": "text",
            "text": json.dumps(error_data, indent=2)
          }],
          "isError": True
        }
    
    # Default: Generic API call
    api_path = arguments.get('api_path', '')
    args = arguments.get('args', [])
    kwargs = arguments.get('kwargs', {})
    store_as = arguments.get('store_as')
    return_properties = arguments.get('return_properties', [])
    
    # Handle special commands
    if api_path == 'get_pid':
      pid = os.getpid()
      return {
        "content": [{"type": "text", "text": f"Cura Process ID: {pid}"}],
        "isError": False
      }
    
    if api_path == 'clear_context':
      count = len(cura_context)
      cura_context.clear()
      return {
        "content": [{"type": "text", "text": f"Cleared {count} stored objects"}],
        "isError": False
      }
    
    # Resolve API path
    target = resolve_api_path(api_path, cura_app, cura_context)
    
    # Resolve arguments
    resolved_args = [resolve_argument(arg, cura_app, cura_context) for arg in args]
    resolved_kwargs = {k: resolve_argument(v, cura_app, cura_context) for k, v in kwargs.items()}
    
    # Execute
    if callable(target):
      result = target(*resolved_args, **resolved_kwargs)
    else:
      result = target
    
    # Store if requested
    if store_as:
      cura_context[store_as] = result
    
    # Extract result info
    result_info = extract_result_info(result, return_properties)
    
    return {
      "content": [{"type": "text", "text": f"✅ SUCCESS: {api_path}\n\nResult: {result_info}\n\nContext: {list(cura_context.keys())}"}],
      "isError": False
    }
  except Exception as e:
    error_trace = traceback.format_exc()
    return {
      "content": [{"type": "text", "text": f"❌ ERROR: {str(e)}\n\n{error_trace}"}],
      "isError": True
    }


def resolve_api_path(path: str, cura_app, cura_context: Dict[str, Any]):
  """Resolve API path to actual object/method"""
  if not path:
    raise ValueError("api_path is required")
  
  # Handle stored object references
  if path.startswith('$'):
    parts = path[1:].split('.', 1)
    obj = cura_context.get(parts[0])
    if obj is None:
      raise ValueError(f"Stored object '{parts[0]}' not found")
    if len(parts) > 1:
      return navigate_path(obj, parts[1])
    return obj
  
  # Start from known roots
  if path.startswith('app.'):
    root = cura_app
    remaining = path[4:]
  elif path.startswith('backend.'):
    root = cura_app.getBackend()
    remaining = path[8:]
  elif path.startswith('scene.'):
    root = cura_app.getController().getScene()
    remaining = path[6:]
  elif path == 'app':
    return cura_app
  elif path == 'backend':
    return cura_app.getBackend()
  elif path == 'scene':
    return cura_app.getController().getScene()
  else:
    root = cura_app
    remaining = path
  
  return navigate_path(root, remaining)


def navigate_path(obj, path: str):
  """Navigate a dotted path from an object"""
  parts = path.split('.')
  current = obj
  
  for part in parts:
    if not part:
      continue
    current = getattr(current, part)
    if current is None:
      raise ValueError(f"Path resolved to None at '{part}'")
  
  return current


def resolve_argument(arg, cura_app, cura_context: Dict[str, Any]):
  """Resolve an argument that might be an API path or stored reference"""
  if arg is None or isinstance(arg, (bool, int, float)):
    return arg
  
  if isinstance(arg, str):
    if '.' in arg or arg.startswith('$') or arg in ['app', 'backend', 'scene']:
      try:
        return resolve_api_path(arg, cura_app, cura_context)
      except:
        return arg
    return arg
  
  if isinstance(arg, list):
    return [resolve_argument(item, cura_app, cura_context) for item in arg]
  
  return arg


def extract_result_info(result, properties=None):
  """Extract information from result object"""
  if result is None:
    return "None"
  
  if isinstance(result, (str, int, float, bool)):
    return str(result)
  
  if properties:
    info = {}
    for prop in properties:
      try:
        value = getattr(result, prop, None)
        info[prop] = str(value) if value is not None else "None"
      except:
        info[prop] = "Error accessing property"
    return str(info)
  
  result_type = type(result).__name__
  try:
    if hasattr(result, 'name'):
      return f"{result_type}(name='{result.name}')"
    elif hasattr(result, 'count'):
      return f"{result_type}(count={result.count})"
    else:
      return result_type
  except:
    return result_type



def send_tool_reply(sse_connection: Dict[str, Any], server_url: str, auth_header: str, 
                   call_id: str, result: Dict[str, Any]) -> bool:
  """
  Send a tools/reply back to the server.
  
  Args:
    sse_connection: Active SSE connection
    server_url: Base server URL
    auth_header: Authorization header
    call_id: The call_id from the reverse message
    result: The result to send back
    
  Returns:
    True if sent successfully, False otherwise
  """
  try:
    # Build the tools/reply request
    reply_request = {
      "jsonrpc": "2.0",
      "id": call_id,
      "method": "tools/reply",
      "params": {
        "result": result
      }
    }
    
    request_body = json.dumps(reply_request)
    
    # Parse the server URL to get host
    parsed_url = urlparse(server_url)
    host = parsed_url.netloc
    use_https = parsed_url.scheme == 'https'
    
    # Create a new connection for the POST request
    if use_https:
      context = ssl.create_default_context()
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE
      post_conn = http.client.HTTPSConnection(host, context=context, timeout=10)
    else:
      post_conn = http.client.HTTPConnection(host, timeout=10)
    
    # Send POST request
    headers = {
      'Content-Type': 'application/json',
      'Content-Length': str(len(request_body)),
      'Authorization': auth_header,
    }
    
    message_path = sse_connection['message_endpoint']
    post_conn.request('POST', message_path, body=request_body, headers=headers)
    post_response = post_conn.getresponse()
    
    # Should get 202 Accepted
    if post_response.status != 202:
      print(f"ERROR: tools/reply POST failed with status {post_response.status}", file=sys.stderr)
      print(f"Response: {post_response.read().decode('utf-8', errors='ignore')}", file=sys.stderr)
      post_conn.close()
      return False
    
    post_conn.close()
    print(f"[OK] Sent tools/reply for call_id {call_id}", file=sys.stderr)
    return True
    
  except Exception as e:
    print(f"ERROR: Failed to send tools/reply: {e}", file=sys.stderr)
    return False


def main_worker(background: bool = False) -> int:
  """
  Worker function that registers demo_tool and listens for reverse calls.
  
  Includes automatic reconnection with exponential backoff if the SSE connection drops.
  
  Args:
    background: If True, run in background thread and return immediately
  
  Returns:
    Exit code (0 for success, non-zero for error)
  """
  print("=== Aura Friday Remote Tool Provider Demo ===", file=sys.stderr)
  print(f"PID: {os.getpid()}", file=sys.stderr)
  print("Registering demo_tool with MCP server\n", file=sys.stderr)
  
  # Connection state for reconnection logic
  retry_count = 0
  max_retry_delay = 60  # Max 1 minute between retries
  
  # Outer reconnection loop - keeps trying forever
  while True:
    try:
      # Calculate retry delay with exponential backoff
      if retry_count > 0:
        delay = min(2 ** retry_count, max_retry_delay)
        print(f"\n[RECONNECT] Waiting {delay} seconds before retry (attempt #{retry_count})...", file=sys.stderr)
        time.sleep(delay)
        print(f"[RECONNECT] Attempting to reconnect...\n", file=sys.stderr)
      
      # Step 1: Find the native messaging manifest
      print("Step 1: Finding native messaging manifest...", file=sys.stderr)
      manifest_path = find_this_native_messaging_manifest_for_this_platform()
      
      if not manifest_path:
        print("ERROR: Could not find native messaging manifest", file=sys.stderr)
        print("Expected locations (platform-specific):", file=sys.stderr)
        print("  Windows: %LOCALAPPDATA%\\AuraFriday\\com.aurafriday.shim.json", file=sys.stderr)
        print("  macOS: ~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.aurafriday.shim.json", file=sys.stderr)
        print("  Linux: ~/.config/google-chrome/NativeMessagingHosts/com.aurafriday.shim.json", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      print(f"[OK] Found manifest: {manifest_path}\n", file=sys.stderr)
      
      # Step 2: Read the manifest
      print("Step 2: Reading manifest...", file=sys.stderr)
      manifest = read_this_native_messaging_manifest(manifest_path)
      
      if not manifest:
        print("ERROR: Could not read manifest", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      print(f"[OK] Manifest loaded\n", file=sys.stderr)
      
      # Step 3: Run the native binary to get the server configuration
      print("Step 3: Discovering MCP server endpoint...", file=sys.stderr)
      config_json = discover_this_mcp_server_endpoint_by_running_native_binary(manifest)
      
      if not config_json:
        print("ERROR: Could not get configuration from native binary", file=sys.stderr)
        print("Is the Aura Friday MCP server running?", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      # Step 4: Extract the server URL from the configuration
      server_url = extract_this_server_url_from_config(config_json)
      
      if not server_url:
        print("ERROR: Could not extract server URL from configuration", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      print(f"[OK] Found server at: {server_url}\n", file=sys.stderr)
      
      # Step 5: Extract authorization header from config
      auth_header = None
      mcp_servers = config_json.get('mcpServers', {})
      if mcp_servers:
        first_server = next(iter(mcp_servers.values()), None)
        if first_server and 'headers' in first_server:
          auth_header = first_server['headers'].get('Authorization')
      
      if not auth_header:
        print("ERROR: No authorization header found in configuration", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      # Step 6: Connect to the SSE endpoint
      print("Step 4: Connecting to SSE endpoint...", file=sys.stderr)
      sse_connection = connect_to_this_sse_endpoint_and_get_this_message_endpoint(server_url, auth_header)
      
      if not sse_connection:
        print("ERROR: Could not connect to SSE endpoint", file=sys.stderr)
        retry_count += 1
        continue  # Retry
      
      print(f"[OK] Connected! Session ID: {sse_connection['session_id']}\n", file=sys.stderr)
      
      # Step 7: Check if remote tool exists
      print("Step 5: Checking for remote tool...", file=sys.stderr)
      tools_response = send_this_jsonrpc_request_and_wait_for_this_response(
        sse_connection,
        server_url,
        auth_header,
        "tools/list",
        {}
      )
      
      if not tools_response:
        print("ERROR: Could not get tools list", file=sys.stderr)
        sse_connection['stop_event'].set()
        sse_connection['thread'].join(timeout=2)
        retry_count += 1
        continue  # Retry
      
      # Check if remote tool exists
      tools = tools_response.get('result', {}).get('tools', [])
      has_remote = any(tool.get('name') == 'remote' for tool in tools)
      
      if not has_remote:
        print("ERROR: Server does not have 'remote' tool - cannot register demo_tool", file=sys.stderr)
        sse_connection['stop_event'].set()
        sse_connection['thread'].join(timeout=2)
        retry_count += 1
        continue  # Retry
      
      print(f"[OK] Remote tool found\n", file=sys.stderr)
      
      # Step 8: Get Cura application instance (will be None in standalone mode)
      cura_app = None
      cura_context = {}
      try:
        from cura.CuraApplication import CuraApplication
        cura_app = CuraApplication.getInstance()
        print(f"[OK] Got Cura application instance\n", file=sys.stderr)
      except Exception as e:
        print(f"[WARN] Could not get Cura application (running standalone?): {e}\n", file=sys.stderr)
      
      # Step 9: Register cura tool
      print("Step 6: Registering cura tool...", file=sys.stderr)
      if not register_cura_tool(sse_connection, server_url, auth_header, cura_app):
        print("ERROR: Failed to register cura tool", file=sys.stderr)
        sse_connection['stop_event'].set()
        sse_connection['thread'].join(timeout=2)
        retry_count += 1
        continue  # Retry
      
      # Reset retry count after successful connection and registration
      retry_count = 0
      
      print("\n" + "="*60, file=sys.stderr)
      print("[OK] cura tool registered successfully!", file=sys.stderr)
      print("Listening for reverse tool calls... (Press Ctrl+C to stop)", file=sys.stderr)
      print("="*60 + "\n", file=sys.stderr)
      
      # Step 9: Listen for reverse calls (blocking on queue - no polling!)
      try:
        while True:
          try:
            # Check if SSE reader thread is still alive
            if not sse_connection['thread'].is_alive():
              print("\n[WARN] SSE connection lost - reconnecting...", file=sys.stderr)
              sse_connection['stop_event'].set()
              sse_connection['thread'].join(timeout=2)
              retry_count = 1  # Start with first retry delay
              break  # Break inner loop to trigger reconnection
            
            # Block until a reverse call arrives (timeout allows checking for Ctrl+C and connection health)
            msg = sse_connection['reverse_queue'].get(timeout=1.0)
            
            if isinstance(msg, dict) and 'reverse' in msg:
              reverse_data = msg['reverse']
              tool_name = reverse_data.get('tool')
              call_id = reverse_data.get('call_id')
              input_data = reverse_data.get('input')
              
              print(f"\n[CALL] Reverse call received:", file=sys.stderr)
              print(f"       Tool: {tool_name}", file=sys.stderr)
              print(f"       Call ID: {call_id}", file=sys.stderr)
              print(f"       Input: {json.dumps(input_data, indent=2)}", file=sys.stderr)
              
              if tool_name == 'cura':
                # Handle the cura tool call (pass connection info so it can call other tools)
                result = handle_cura_tool_call(input_data, cura_app, cura_context, sse_connection, server_url, auth_header)
                
                # Send the reply back
                send_tool_reply(sse_connection, server_url, auth_header, call_id, result)
              else:
                print(f"[WARN] Unknown tool: {tool_name}", file=sys.stderr)
          
          except queue.Empty:
            # No messages, just loop again (allows Ctrl+C and connection health checks)
            continue
        
      except KeyboardInterrupt:
        print("\n\n" + "="*60, file=sys.stderr)
        print("Shutting down...", file=sys.stderr)
        print("="*60, file=sys.stderr)
        # Clean up SSE connection
        sse_connection['stop_event'].set()
        sse_connection['thread'].join(timeout=2)
        print("Done!", file=sys.stderr)
        return 0
      
      # If we get here, it means the connection dropped and we need to reconnect
      # (the break statement above brings us here)
      
    except KeyboardInterrupt:
      # Handle Ctrl+C in outer loop too
      print("\n\n" + "="*60, file=sys.stderr)
      print("Shutting down...", file=sys.stderr)
      print("="*60, file=sys.stderr)
      print("Done!", file=sys.stderr)
      return 0
    except Exception as e:
      print(f"\n[ERROR] Unexpected error in main loop: {e}", file=sys.stderr)
      import traceback
      traceback.print_exc(file=sys.stderr)
      retry_count += 1
      # Loop continues to retry


def connect_to_this_sse_endpoint_and_get_this_message_endpoint(server_url: str, auth_header: str) -> Optional[Dict[str, Any]]:
  """
  Connect to the SSE endpoint and extract the message endpoint from the initial event.
  
  This implements the SSE handshake:
  1. GET /sse with Authorization header
  2. Receive "event: endpoint" with the session-specific message endpoint
  3. Keep the connection open for receiving responses
  
  Args:
    server_url: The SSE endpoint URL (e.g., "https://127-0-0-1.local.aurafriday.com:31173/sse")
    auth_header: The Authorization header value (e.g., "Bearer xxx")
    
  Returns:
    Dictionary with connection info, or None on error:
      {
        'session_id': str,
        'message_endpoint': str,
        'connection': http.client.HTTPSConnection or HTTPConnection,
        'response': http.client.HTTPResponse,
        'thread': threading.Thread (SSE reader thread),
        'stop_event': threading.Event (to stop the reader thread),
        'messages': queue-like list (received SSE messages)
      }
  """
  try:
    parsed_url = urlparse(server_url)
    host = parsed_url.netloc
    path = parsed_url.path
    use_https = parsed_url.scheme == 'https'
    
    # Create connection
    if use_https:
      # Create SSL context that doesn't verify certificates (for self-signed certs)
      context = ssl.create_default_context()
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE
      conn = http.client.HTTPSConnection(host, context=context, timeout=30)
    else:
      conn = http.client.HTTPConnection(host, timeout=30)
    
    # Send GET request to SSE endpoint
    headers = {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Authorization': auth_header,
    }
    
    conn.request('GET', path, headers=headers)
    response = conn.getresponse()
    
    if response.status != 200:
      print(f"ERROR: SSE connection failed with status {response.status}", file=sys.stderr)
      print(f"Response: {response.read().decode('utf-8', errors='ignore')}", file=sys.stderr)
      conn.close()
      return None
    
    # Read the initial SSE event to get the message endpoint
    # Format: "event: endpoint\ndata: /messages/?session_id=xxx\n\n"
    session_id = None
    message_endpoint = None
    
    # Read line by line until we get the endpoint
    event_type = None
    for _ in range(10):  # Read up to 10 lines
      line = response.readline().decode('utf-8').strip()
      
      if line.startswith('event:'):
        event_type = line.split(':', 1)[1].strip()
      elif line.startswith('data:'):
        data = line.split(':', 1)[1].strip()
        if event_type == 'endpoint':
          message_endpoint = data
          # Extract session_id from the endpoint
          # Format: /messages/?session_id=xxx
          if 'session_id=' in message_endpoint:
            session_id = message_endpoint.split('session_id=')[1].split('&')[0]
          break
      elif line == '':
        # Empty line marks end of event
        if message_endpoint:
          break
    
    if not message_endpoint or not session_id:
      print("ERROR: Could not extract message endpoint from SSE stream", file=sys.stderr)
      conn.close()
      return None
    
    # Set up message routing queues
    reverse_queue = queue.Queue()  # For reverse tool calls
    pending_responses = {}  # {request_id: queue.Queue()} for waiting responses
    pending_responses_lock = threading.Lock()
    stop_event = threading.Event()
    
    def sse_reader_thread_function():
      """Background thread to read SSE messages and route them."""
      try:
        while not stop_event.is_set():
          line = response.readline()
          if not line:
            # Connection closed
            break
          
          line_str = line.decode('utf-8', errors='ignore').strip()
          
          # Skip ping messages
          if line_str.startswith(':'):
            continue
          
          if line_str.startswith('data:'):
            data_str = line_str.split(':', 1)[1].strip()
            try:
              # Try to parse as JSON
              json_data = json.loads(data_str)
              
              # Route message based on type
              if 'reverse' in json_data:
                # This is a reverse tool call - route to reverse queue
                reverse_queue.put(json_data)
              elif 'id' in json_data:
                # This is a response to a request - route to pending response queue
                request_id = json_data['id']
                with pending_responses_lock:
                  if request_id in pending_responses:
                    pending_responses[request_id].put(json_data)
                  # If no one is waiting for this response, just drop it
              
            except json.JSONDecodeError:
              # Not JSON, ignore
              pass
      except Exception as e:
        if not stop_event.is_set():
          print(f"\nSSE reader thread error: {e}", file=sys.stderr)
    
    reader_thread = threading.Thread(target=sse_reader_thread_function, daemon=True)
    reader_thread.start()
    
    return {
      'session_id': session_id,
      'message_endpoint': message_endpoint,
      'connection': conn,
      'response': response,
      'thread': reader_thread,
      'stop_event': stop_event,
      'reverse_queue': reverse_queue,
      'pending_responses': pending_responses,
      'pending_responses_lock': pending_responses_lock,
      'server_url': server_url,
    }
    
  except Exception as e:
    print(f"ERROR: Failed to connect to SSE endpoint: {e}", file=sys.stderr)
    return None


def send_this_jsonrpc_request_and_wait_for_this_response(
  sse_connection: Dict[str, Any],
  server_url: str,
  auth_header: str,
  method: str,
  params: Dict[str, Any],
  timeout_seconds: float = 10.0
) -> Optional[Dict[str, Any]]:
  """
  Send a JSON-RPC request via POST and wait for the response via SSE.
  
  This implements the MCP request/response pattern:
  1. POST to /messages/?session_id=xxx with JSON-RPC request
  2. Server responds with 202 Accepted
  3. Actual response comes via the SSE stream (routed by request ID)
  
  Args:
    sse_connection: Connection info from connect_to_this_sse_endpoint_and_get_this_message_endpoint()
    server_url: Base server URL
    auth_header: Authorization header value
    method: JSON-RPC method name (e.g., "tools/list")
    params: JSON-RPC params dictionary
    timeout_seconds: How long to wait for a response
    
  Returns:
    JSON-RPC response dictionary, or None on error/timeout
  """
  try:
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Create a queue for this request's response
    response_queue = queue.Queue()
    with sse_connection['pending_responses_lock']:
      sse_connection['pending_responses'][request_id] = response_queue
    
    try:
      # Build JSON-RPC request
      jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
      }
      
      request_body = json.dumps(jsonrpc_request)
      
      # Parse the server URL to get host and build full message endpoint URL
      parsed_url = urlparse(server_url)
      host = parsed_url.netloc
      use_https = parsed_url.scheme == 'https'
      
      # Create a new connection for the POST request
      if use_https:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        post_conn = http.client.HTTPSConnection(host, context=context, timeout=10)
      else:
        post_conn = http.client.HTTPConnection(host, timeout=10)
      
      # Send POST request
      headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(request_body)),
        'Authorization': auth_header,
      }
      
      message_path = sse_connection['message_endpoint']
      post_conn.request('POST', message_path, body=request_body, headers=headers)
      post_response = post_conn.getresponse()
      
      # Should get 202 Accepted
      if post_response.status != 202:
        print(f"ERROR: POST request failed with status {post_response.status}", file=sys.stderr)
        print(f"Response: {post_response.read().decode('utf-8', errors='ignore')}", file=sys.stderr)
        post_conn.close()
        return None
      
      post_conn.close()
      
      # Wait for the response to arrive via SSE (blocking on queue)
      try:
        response = response_queue.get(timeout=timeout_seconds)
        return response
      except queue.Empty:
        print(f"ERROR: Timeout waiting for response to {method}", file=sys.stderr)
        return None
      
    finally:
      # Clean up the pending response queue
      with sse_connection['pending_responses_lock']:
        sse_connection['pending_responses'].pop(request_id, None)
    
  except Exception as e:
    print(f"ERROR: Failed to send JSON-RPC request: {e}", file=sys.stderr)
    return None


def main() -> int:
  """
  Main entry point with argument parsing.
  
  Returns:
    Exit code (0 for success, non-zero for error)
  """
  parser = argparse.ArgumentParser(
    description='Aura Friday Remote Tool Provider - Registers demo_tool_python with MCP server',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=DOCO
  )
  parser.add_argument(
    '--background',
    action='store_true',
    help='Run in background thread and return immediately (for testing/automation)'
  )
  
  args = parser.parse_args()
  
  if args.background:
    # Run in background thread
    print(f"Starting in background mode (PID: {os.getpid()})...", file=sys.stderr)
    worker_thread = threading.Thread(target=main_worker, args=(True,), daemon=False)
    worker_thread.start()
    
    # Wait a moment for initialization
    time.sleep(2)
    
    print(f"[OK] Background worker started (PID: {os.getpid()})", file=sys.stderr)
    print(f"  Use 'kill {os.getpid()}' to stop", file=sys.stderr)
    
    # Keep main thread alive
    try:
      worker_thread.join()
    except KeyboardInterrupt:
      print("\nShutting down background worker...", file=sys.stderr)
    
    return 0
  else:
    # Run in foreground (blocking)
    return main_worker(background=False)


if __name__ == "__main__":
  sys.exit(main())
