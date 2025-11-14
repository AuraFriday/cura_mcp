"""
Cura MCP Plugin - Entry Point
Connects Cura to MCP-Link server for AI-driven slicing
"""

from UM.Extension import Extension
from UM.Logger import Logger
import threading

class CuraMCPExtension(Extension):
  """Cura MCP Extension - integrates Cura with MCP-Link server"""
  
  def __init__(self, app):
    super().__init__()
    self._app = app
    self._worker_thread = None
    Logger.log("i", "[MCP] Cura MCP Extension initialized")
    
    # Start MCP worker in background thread
    self._worker_thread = threading.Thread(target=self._run_mcp_worker, daemon=True)
    self._worker_thread.start()
    Logger.log("i", "[MCP] MCP worker thread started")
  
  def _run_mcp_worker(self):
    """Run the MCP worker (imported from cura_mcp module)"""
    try:
      # Import the main worker function from cura_mcp
      from . import cura_mcp
      
      # Run the worker (this will block until stopped)
      cura_mcp.main_worker(background=False)
    except Exception as e:
      Logger.log("e", f"[MCP] Worker thread error: {e}")
      import traceback
      Logger.log("e", traceback.format_exc())

def getMetaData():
  """Return plugin metadata (optional, can be empty)."""
  return {}

def register(app):
  """
  Register the plugin with Cura.
  Called once when Cura loads the plugin.
  
  Args:
    app: CuraApplication instance
  
  Returns:
    Dictionary with extension instance
  """
  return {
    "extension": CuraMCPExtension(app)
  }

