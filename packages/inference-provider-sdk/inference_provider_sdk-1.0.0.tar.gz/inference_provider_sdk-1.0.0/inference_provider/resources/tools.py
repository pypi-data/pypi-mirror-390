"""
Tools resource client
"""

from typing import Any, Dict, List, Optional

from inference_provider.resources.base import BaseResource
from inference_provider.types import (
    JavaScriptFunctionConfig,
    JSONSchema,
    RestApiConfig,
    ToolDefinition,
    ToolType,
)


class Tools(BaseResource):
    """Tools resource client"""

    def list(
        self,
        tool_type: Optional[ToolType] = None,
        is_active: Optional[bool] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[ToolDefinition]:
        """List all tools"""
        request_body: Dict[str, Any] = {"action": "list_tools"}

        if tool_type is not None:
            request_body["tool_type"] = (
                tool_type.value if isinstance(tool_type, ToolType) else tool_type
            )
        if is_active is not None:
            request_body["is_active"] = is_active
        if is_public is not None:
            request_body["is_public"] = is_public
        if tags:
            request_body["tags"] = tags

        response = self.http.post(self.endpoint, self.clean_dict(request_body))
        tools_data = response.get("data", {}).get("tools", [])
        return [ToolDefinition(**tool) for tool in tools_data]

    def get(self, tool_id: str) -> ToolDefinition:
        """Get tool by ID"""
        self.validate_required({"tool_id": tool_id}, ["tool_id"], "get tool")

        response = self.http.post(self.endpoint, {"action": "get_tool", "tool_id": tool_id})
        tool_data = response.get("data", {}).get("tool")
        return ToolDefinition(**tool_data)

    def create_rest_api(
        self,
        tool_name: str,
        display_name: str,
        description: str,
        config: RestApiConfig,
        input_schema: JSONSchema,
        output_schema: Optional[JSONSchema] = None,
        version: str = "1.0",
        is_active: bool = True,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
    ) -> ToolDefinition:
        """Create a REST API tool"""
        self.validate_required(
            {
                "tool_name": tool_name,
                "display_name": display_name,
                "description": description,
                "config": config,
                "input_schema": input_schema,
            },
            ["tool_name", "display_name", "description", "config", "input_schema"],
            "create REST API tool",
        )

        request_body = self.clean_dict(
            {
                "action": "create_tool",
                "tool_type": "rest_api",
                "tool_name": tool_name,
                "display_name": display_name,
                "description": description,
                "version": version,
                "is_active": is_active,
                "is_public": is_public,
                "config": config.dict() if hasattr(config, "dict") else config,
                "input_schema": input_schema.dict() if hasattr(input_schema, "dict") else input_schema,
                "output_schema": (
                    output_schema.dict() if hasattr(output_schema, "dict") else output_schema
                )
                if output_schema
                else None,
                "tags": tags or [],
            }
        )

        response = self.http.post(self.endpoint, request_body)
        tool_data = response.get("data", {}).get("tool")
        return ToolDefinition(**tool_data)

    def create_javascript(
        self,
        tool_name: str,
        display_name: str,
        description: str,
        config: JavaScriptFunctionConfig,
        input_schema: JSONSchema,
        output_schema: Optional[JSONSchema] = None,
        version: str = "1.0",
        is_active: bool = True,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
    ) -> ToolDefinition:
        """Create a JavaScript function tool"""
        self.validate_required(
            {
                "tool_name": tool_name,
                "display_name": display_name,
                "description": description,
                "config": config,
                "input_schema": input_schema,
            },
            ["tool_name", "display_name", "description", "config", "input_schema"],
            "create JavaScript tool",
        )

        request_body = self.clean_dict(
            {
                "action": "create_tool",
                "tool_type": "javascript_function",
                "tool_name": tool_name,
                "display_name": display_name,
                "description": description,
                "version": version,
                "is_active": is_active,
                "is_public": is_public,
                "config": config.dict() if hasattr(config, "dict") else config,
                "input_schema": input_schema.dict() if hasattr(input_schema, "dict") else input_schema,
                "output_schema": (
                    output_schema.dict() if hasattr(output_schema, "dict") else output_schema
                )
                if output_schema
                else None,
                "tags": tags or [],
            }
        )

        response = self.http.post(self.endpoint, request_body)
        tool_data = response.get("data", {}).get("tool")
        return ToolDefinition(**tool_data)

    def update(self, tool_id: str, **kwargs: Any) -> ToolDefinition:
        """Update an existing tool"""
        self.validate_required({"tool_id": tool_id}, ["tool_id"], "update tool")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        request_body = self.clean_dict({"action": "update_tool", "tool_id": tool_id, **kwargs})

        response = self.http.post(self.endpoint, request_body)
        tool_data = response.get("data", {}).get("tool")
        return ToolDefinition(**tool_data)

    def delete(self, tool_id: str) -> None:
        """Delete a tool"""
        self.validate_required({"tool_id": tool_id}, ["tool_id"], "delete tool")

        self.http.post(self.endpoint, {"action": "delete_tool", "tool_id": tool_id})

    def test(self, tool_id: str, input_data: Dict[str, Any]) -> Any:
        """Test a tool execution"""
        self.validate_required(
            {"tool_id": tool_id, "input_data": input_data}, ["tool_id", "input_data"], "test tool"
        )

        response = self.http.post(
            self.endpoint, {"action": "test_tool", "tool_id": tool_id, "input_data": input_data}
        )
        return response.get("data", {}).get("result")

    def get_by_type(self, tool_type: ToolType) -> List[ToolDefinition]:
        """Get tools by type"""
        return self.list(tool_type=tool_type)

    def get_rest_api_tools(self) -> List[ToolDefinition]:
        """Get REST API tools"""
        return self.get_by_type(ToolType.REST_API)

    def get_javascript_tools(self) -> List[ToolDefinition]:
        """Get JavaScript function tools"""
        return self.get_by_type(ToolType.JAVASCRIPT_FUNCTION)

    def get_mcp_tools(self) -> List[ToolDefinition]:
        """Get MCP tools (read-only, managed via MCP servers)"""
        return self.get_by_type(ToolType.MCP)

    def assign_to_agent(self, tool_id: str, agent_id: str) -> None:
        """Assign tool to agent"""
        self.validate_required(
            {"tool_id": tool_id, "agent_id": agent_id}, ["tool_id", "agent_id"], "assign tool to agent"
        )

        self.http.post(
            self.endpoint, {"action": "assign_tool_to_agent", "tool_id": tool_id, "agent_id": agent_id}
        )

    def unassign_from_agent(self, tool_id: str, agent_id: str) -> None:
        """Unassign tool from agent"""
        self.validate_required(
            {"tool_id": tool_id, "agent_id": agent_id},
            ["tool_id", "agent_id"],
            "unassign tool from agent",
        )

        self.http.post(
            self.endpoint,
            {"action": "unassign_tool_from_agent", "tool_id": tool_id, "agent_id": agent_id},
        )
