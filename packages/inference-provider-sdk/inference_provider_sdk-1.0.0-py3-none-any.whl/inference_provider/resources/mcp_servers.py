"""
MCP Servers resource client
"""

from typing import Any, Dict, List, Optional

from inference_provider.resources.base import BaseResource
from inference_provider.types import AuthType, MCPServer, MCPServerResource, MCPServerTool, MCPServerType


class MCPServers(BaseResource):
    """MCP Servers resource client"""

    def list(self) -> List[MCPServer]:
        """List all MCP servers"""
        response = self.http.post(self.endpoint, {"action": "list_mcp_servers"})
        servers_data = response.get("data", {}).get("mcp_servers", [])
        return [MCPServer(**server) for server in servers_data]

    def get(self, server_id: str) -> MCPServer:
        """Get MCP server by ID"""
        self.validate_required({"server_id": server_id}, ["server_id"], "get MCP server")

        response = self.http.post(
            self.endpoint, {"action": "get_mcp_server", "mcp_server_id": server_id}
        )
        server_data = response.get("data", {}).get("mcp_server")
        return MCPServer(**server_data)

    def create(
        self,
        name: str,
        server_type: MCPServerType,
        connection_config: Any,
        description: Optional[str] = None,
        auth_type: AuthType = AuthType.NONE,
        auth_config: Optional[Any] = None,
        is_active: bool = True,
        metadata: Optional[Any] = None,
    ) -> MCPServer:
        """Create a new MCP server"""
        self.validate_required(
            {"name": name, "server_type": server_type, "connection_config": connection_config},
            ["name", "server_type", "connection_config"],
            "create MCP server",
        )

        request_body = self.clean_dict(
            {
                "action": "create_mcp_server",
                "name": name,
                "description": description,
                "server_type": (
                    server_type.value if isinstance(server_type, MCPServerType) else server_type
                ),
                "connection_config": connection_config,
                "auth_type": auth_type.value if isinstance(auth_type, AuthType) else auth_type,
                "auth_config": auth_config,
                "is_active": is_active,
                "metadata": metadata,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        server_data = response.get("data", {}).get("mcp_server")
        return MCPServer(**server_data)

    def update(self, server_id: str, **kwargs: Any) -> MCPServer:
        """Update an existing MCP server"""
        self.validate_required({"server_id": server_id}, ["server_id"], "update MCP server")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        request_body = self.clean_dict({"action": "update_mcp_server", "mcp_server_id": server_id, **kwargs})

        response = self.http.post(self.endpoint, request_body)
        server_data = response.get("data", {}).get("mcp_server")
        return MCPServer(**server_data)

    def delete(self, server_id: str) -> None:
        """Delete an MCP server"""
        self.validate_required({"server_id": server_id}, ["server_id"], "delete MCP server")

        self.http.post(self.endpoint, {"action": "delete_mcp_server", "mcp_server_id": server_id})

    def sync(self, server_id: str) -> None:
        """Sync MCP server (fetch tools and resources)"""
        self.validate_required({"server_id": server_id}, ["server_id"], "sync MCP server")

        self.http.post(self.endpoint, {"action": "sync_mcp_server", "mcp_server_id": server_id})

    def list_tools(self, server_id: str) -> List[MCPServerTool]:
        """List tools from MCP server"""
        self.validate_required({"server_id": server_id}, ["server_id"], "list MCP server tools")

        response = self.http.post(
            self.endpoint, {"action": "list_mcp_server_tools", "mcp_server_id": server_id}
        )
        tools_data = response.get("data", {}).get("tools", [])
        return [MCPServerTool(**tool) for tool in tools_data]

    def list_resources(self, server_id: str) -> List[MCPServerResource]:
        """List resources from MCP server"""
        self.validate_required({"server_id": server_id}, ["server_id"], "list MCP server resources")

        response = self.http.post(
            self.endpoint, {"action": "list_mcp_server_resources", "mcp_server_id": server_id}
        )
        resources_data = response.get("data", {}).get("resources", [])
        return [MCPServerResource(**resource) for resource in resources_data]

    def assign_to_agent(self, server_id: str, agent_id: str, priority: Optional[int] = None) -> None:
        """Assign MCP server to agent"""
        self.validate_required(
            {"server_id": server_id, "agent_id": agent_id},
            ["server_id", "agent_id"],
            "assign MCP server to agent",
        )

        request_body: Dict[str, Any] = {
            "action": "assign_mcp_server_to_agent",
            "mcp_server_id": server_id,
            "agent_id": agent_id,
        }

        if priority is not None:
            request_body["priority"] = priority

        self.http.post(self.endpoint, request_body)

    def unassign_from_agent(self, server_id: str, agent_id: str) -> None:
        """Unassign MCP server from agent"""
        self.validate_required(
            {"server_id": server_id, "agent_id": agent_id},
            ["server_id", "agent_id"],
            "unassign MCP server from agent",
        )

        self.http.post(
            self.endpoint,
            {
                "action": "unassign_mcp_server_from_agent",
                "mcp_server_id": server_id,
                "agent_id": agent_id,
            },
        )

    def list_agent_servers(self, agent_id: str) -> List[Any]:
        """List MCP servers assigned to an agent"""
        self.validate_required({"agent_id": agent_id}, ["agent_id"], "list agent MCP servers")

        response = self.http.post(
            self.endpoint, {"action": "list_agent_mcp_servers", "agent_id": agent_id}
        )
        return response.get("data", {}).get("mcp_servers", [])
