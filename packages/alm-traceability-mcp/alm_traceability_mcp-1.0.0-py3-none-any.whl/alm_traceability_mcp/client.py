"""
ADK Client Interface for ALM Traceability MCP Tools
Provides easy-to-use interface for ADK agents
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
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

class ALMClient:
    """
    ADK-friendly client for ALM traceability operations
    Wraps all your existing MCP tools in an easy-to-use interface
    """
    
    def __init__(self):
        self.mcp = FastMCP("alm-client")
        self.ado_client = None
        self.jira_client = None
        self.vector_service = None
        self.traceability_manager = None
        self.initialized = False
        self._tools_map = {}
    
    async def initialize(self):
        """Initialize all services and register tools"""
        if self.initialized:
            return
        
        logger.info("Initializing ALM Client...")
        
        # Initialize service clients
        self.ado_client = ADOClient()
        self.jira_client = JiraClient()
        self.vector_service = VectorService()
        self.traceability_manager = TraceabilityManager()
        
        # Register all comprehensive tools from mcp_tools.py
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
        
        # Build tools map for easy access
        tools = await self.mcp.list_tools()
        self._tools_map = {tool.name: tool for tool in tools}
        
        self.initialized = True
        logger.info(f"ALM Client initialized with {len(tools)} tools")
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call any MCP tool by name with parameters
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool parameters
            
        Returns:
            Dict containing the tool result
        """
        if not self.initialized:
            await self.initialize()
        
        if tool_name not in self._tools_map:
            available_tools = list(self._tools_map.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        
        try:
            result = await self.mcp.call_tool(tool_name, kwargs)
            
            # Extract and parse the result
            if result and hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    import json
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"result": content.text}
                else:
                    return {"result": str(content)}
            else:
                return {"result": "No content returned"}
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def list_tools(self) -> List[str]:
        """Get list of available tool names"""
        if not self.initialized:
            await self.initialize()
        return list(self._tools_map.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        if tool_name not in self._tools_map:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self._tools_map[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema.get("properties", {}) if tool.inputSchema else {}
        }
    
    # Azure DevOps Convenience Methods
    async def configure_ado(self, organization: str, project: str, pat: str) -> Dict[str, Any]:
        """Configure Azure DevOps connection"""
        return await self.call_tool("configure_ado_connection", 
                                   organization=organization, 
                                   project=project, 
                                   personal_access_token=pat)
    
    async def fetch_user_story(self, story_id: int) -> Dict[str, Any]:
        """Fetch Azure DevOps user story"""
        return await self.call_tool("fetch_user_story", user_story_id=story_id)
    
    async def create_test_case(self, story_id: int, title: str, description: str = "", 
                              steps: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create test case for user story"""
        return await self.call_tool("create_testcase",
                                   user_story_id=story_id,
                                   title=title,
                                   description=description,
                                   steps=steps or [])
    
    async def batch_create_test_cases(self, story_id: int, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple test cases for a user story"""
        return await self.call_tool("batch_create_testcases",
                                   user_story_id=story_id,
                                   test_cases=test_cases)
    
    async def prepare_test_context(self, story_id: int, search_similar: bool = True) -> Dict[str, Any]:
        """Prepare comprehensive context for test case generation"""
        return await self.call_tool("prepare_test_case_context",
                                   user_story_id=story_id,
                                   search_similar=search_similar)
    
    # Jira Convenience Methods
    async def configure_jira(self, base_url: str, email: str, api_token: str, project_key: str) -> Dict[str, Any]:
        """Configure Jira connection"""
        return await self.call_tool("configure_jira_connection",
                                   base_url=base_url,
                                   email=email,
                                   api_token=api_token,
                                   project_key=project_key)
    
    async def fetch_jira_issue(self, issue_key: str) -> Dict[str, Any]:
        """Fetch Jira issue/story"""
        return await self.call_tool("fetch_jira_issue", issue_key=issue_key)
    
    async def create_jira_test_case(self, story_key: str, title: str, description: str = "",
                                   steps: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create Jira test case"""
        return await self.call_tool("create_jira_testcase",
                                   story_key=story_key,
                                   title=title,
                                   description=description,
                                   steps=steps or [])
    
    # Vector Search Methods
    async def configure_vertex_ai(self, project_id: str, location: str, 
                                 index_id: str = None, endpoint_id: str = None) -> Dict[str, Any]:
        """Configure Google Cloud Vertex AI"""
        return await self.call_tool("configure_vertex_ai",
                                   project_id=project_id,
                                   location=location,
                                   index_id=index_id,
                                   endpoint_id=endpoint_id)
    
    async def search_similar_stories(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for similar user stories"""
        return await self.call_tool("search_similar_stories",
                                   query=query,
                                   max_results=max_results)
    
    # Traceability Methods
    async def get_traceability_matrix(self, story_id: int = None) -> Dict[str, Any]:
        """Get traceability matrix"""
        return await self.call_tool("traceability_map", user_story_id=story_id)
    
    async def get_test_cases_for_story(self, story_id: int) -> Dict[str, Any]:
        """Get test cases linked to a story"""
        return await self.call_tool("get_test_cases_for_story", user_story_id=story_id)
    
    async def system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return await self.call_tool("system_status")

# Convenience functions for quick usage
async def create_alm_client() -> ALMClient:
    """Create and initialize an ALM client"""
    client = ALMClient()
    await client.initialize()
    return client