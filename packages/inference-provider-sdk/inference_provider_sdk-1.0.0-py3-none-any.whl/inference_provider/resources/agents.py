"""
Agents resource client
"""

from typing import Any, Dict, List, Optional

from inference_provider.resources.base import BaseResource
from inference_provider.types import (
    Agent,
    AgentInferenceResponse,
    ConversationMessage,
    ImageInput,
    Variable,
)


class Agents(BaseResource):
    """Agents resource client (sync)"""

    def list(
        self,
        is_active: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        provider_id: Optional[str] = None,
    ) -> List[Agent]:
        """List all agents"""
        request_body: Dict[str, Any] = {"action": "list_agents"}

        if is_active is not None:
            request_body["is_active"] = is_active
        if tags:
            request_body["tags"] = tags
        if provider_id:
            request_body["provider_id"] = provider_id

        response = self.http.post(self.endpoint, request_body)
        agents_data = response.get("data", {}).get("agents", [])
        return [Agent(**agent) for agent in agents_data]

    def get(self, agent_id: str) -> Agent:
        """Get agent by ID"""
        self.validate_required({"agent_id": agent_id}, ["agent_id"], "get agent")

        agents = self.list()
        agent = next((a for a in agents if a.id == agent_id), None)

        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found")

        return agent

    def create(
        self,
        name: str,
        system_prompt: str,
        model_name: str,
        description: Optional[str] = None,
        variables: Optional[List[Variable]] = None,
        custom_response_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        default_embedding_model_id: Optional[str] = None,
    ) -> Agent:
        """Create a new agent"""
        self.validate_required(
            {"name": name, "system_prompt": system_prompt, "model_name": model_name},
            ["name", "system_prompt", "model_name"],
            "create agent",
        )

        request_body = self.clean_dict(
            {
                "action": "create_agent",
                "name": name,
                "description": description,
                "system_prompt": system_prompt,
                "variables": [v.dict() for v in variables] if variables else [],
                "custom_response_id": custom_response_id,
                "provider_id": provider_id,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "tags": tags or [],
                "is_active": is_active,
                "default_embedding_model_id": default_embedding_model_id,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        agent_data = response.get("data", {}).get("agent")
        return Agent(**agent_data)

    def update(self, agent_id: str, **kwargs: Any) -> Agent:
        """Update an existing agent"""
        self.validate_required({"agent_id": agent_id}, ["agent_id"], "update agent")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        # Convert Variable objects to dicts if present
        if "variables" in kwargs and kwargs["variables"]:
            kwargs["variables"] = [v.dict() if isinstance(v, Variable) else v for v in kwargs["variables"]]

        request_body = self.clean_dict({"action": "update_agent", "agent_id": agent_id, **kwargs})

        response = self.http.post(self.endpoint, request_body)
        agent_data = response.get("data", {}).get("agent")
        return Agent(**agent_data)

    def delete(self, agent_id: str) -> None:
        """Delete an agent"""
        self.validate_required({"agent_id": agent_id}, ["agent_id"], "delete agent")

        self.http.post(self.endpoint, {"action": "delete_agent", "agent_id": agent_id})

    def run(
        self,
        agent_id: str,
        user_message: str,
        rag_collection_id: Optional[str] = None,
        rag_match_threshold: Optional[float] = None,
        rag_match_count: Optional[int] = None,
        embedding_model_id: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        response_structure: Optional[Any] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        images: Optional[List[ImageInput]] = None,
    ) -> AgentInferenceResponse:
        """Run agent inference"""
        self.validate_required(
            {"agent_id": agent_id, "user_message": user_message},
            ["agent_id", "user_message"],
            "run agent",
        )

        request_body = self.clean_dict(
            {
                "agent_id": agent_id,
                "user_message": user_message,
                "rag_collection_id": rag_collection_id,
                "rag_match_threshold": rag_match_threshold,
                "rag_match_count": rag_match_count,
                "embedding_model_id": embedding_model_id,
                "variables": variables,
                "response_structure": response_structure,
                "conversation_history": (
                    [msg.dict() if isinstance(msg, ConversationMessage) else msg for msg in conversation_history]
                    if conversation_history
                    else None
                ),
                "images": [img.dict() if isinstance(img, ImageInput) else img for img in images] if images else None,
            }
        )

        response = self.http.post("/functions/v1/agent-inference", request_body)
        return AgentInferenceResponse(**response)

    def chat(
        self,
        agent_id: str,
        message: str,
        history: Optional[List[ConversationMessage]] = None,
        **options: Any,
    ) -> AgentInferenceResponse:
        """Run agent with conversation history"""
        return self.run(agent_id=agent_id, user_message=message, conversation_history=history, **options)

    def run_with_rag(
        self,
        agent_id: str,
        message: str,
        collection_id: str,
        match_threshold: Optional[float] = None,
        match_count: Optional[int] = None,
        embedding_model_id: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
    ) -> AgentInferenceResponse:
        """Run agent with RAG"""
        return self.run(
            agent_id=agent_id,
            user_message=message,
            rag_collection_id=collection_id,
            rag_match_threshold=match_threshold,
            rag_match_count=match_count,
            embedding_model_id=embedding_model_id,
            variables=variables,
            conversation_history=conversation_history,
        )

    def run_with_vision(
        self,
        agent_id: str,
        message: str,
        images: List[ImageInput],
        **options: Any,
    ) -> AgentInferenceResponse:
        """Run agent with vision (image inputs)"""
        return self.run(agent_id=agent_id, user_message=message, images=images, **options)
