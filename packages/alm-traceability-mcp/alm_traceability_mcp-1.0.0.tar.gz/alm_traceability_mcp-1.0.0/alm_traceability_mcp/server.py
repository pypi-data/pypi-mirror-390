"""
ALM Server - MCP Server wrapper for deployment
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path to import your existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from ado_client import ADOClient
from jira_client import JiraClient
from vector_service import VectorService
from traceability_manager import TraceabilityManager
from mcp_tools import register_all_tools
from mcp_traceability_tools import register_all_tools as register_traceability_tools

logger = logging.getLogger(__name__)

class ALMServer:
    """
    ALM Traceability MCP Server
    Wrapper around your existing MCP server implementation
    """
    
    def __init__(self, server_name: str = "alm-traceability-server"):
        self.mcp = FastMCP(server_name)
        self.ado_client = None
        self.jira_client = None
        self.vector_service = None
        self.traceability_manager = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize all services and register tools"""
        if self.initialized:
            return
        
        logger.info("Initializing ALM Traceability MCP Server...")
        
        # Initialize service clients (same as your mcp_main.py)
        self.ado_client = ADOClient()
        self.jira_client = JiraClient()
        self.vector_service = VectorService()
        self.traceability_manager = TraceabilityManager()
        
        # Register comprehensive tools from mcp_tools.py
        register_all_tools(
            self.mcp, 
            self.ado_client, 
            self.jira_client, 
            self.vector_service, 
            self.traceability_manager
        )
        
        # Register additional traceability tools
        register_traceability_tools(
            self.mcp,
            self.ado_client,
            self.jira_client, 
            self.vector_service,
            self.traceability_manager
        )
        
        self.initialized = True
        tools_count = len(self.mcp.list_tools())
        logger.info(f"ALM Traceability MCP Server initialized with {tools_count} tools")
    
    async def run(self):
        """Run the MCP server"""
        if not self.initialized:
            await self.initialize()
        
        logger.info("Starting ALM Traceability MCP Server...")
        await self.mcp.run()
    
    def get_mcp_instance(self):
        """Get the underlying FastMCP instance"""
        return self.mcp

async def run_server():
    """Run the ALM server - can be used as entry point"""
    server = ALMServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(run_server())
