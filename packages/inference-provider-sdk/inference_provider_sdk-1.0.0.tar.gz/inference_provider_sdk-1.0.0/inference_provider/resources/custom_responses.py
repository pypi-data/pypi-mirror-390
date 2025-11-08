"""
Custom Responses resource client
"""

from typing import Any, List, Optional

from inference_provider.resources.base import BaseResource
from inference_provider.types import CustomResponse


class CustomResponses(BaseResource):
    """Custom Responses resource client"""

    def list(self) -> List[CustomResponse]:
        """List all custom responses"""
        response = self.http.post(self.endpoint, {"action": "list_custom_responses"})
        responses_data = response.get("data", {}).get("custom_responses", [])
        return [CustomResponse(**response) for response in responses_data]

    def get(self, response_id: str) -> CustomResponse:
        """Get custom response by ID"""
        self.validate_required({"response_id": response_id}, ["response_id"], "get custom response")

        # Note: API might not have direct get action, so we list and filter
        responses = self.list()
        custom_response = next((r for r in responses if r.id == response_id), None)

        if not custom_response:
            raise ValueError(f"Custom response with ID {response_id} not found")

        return custom_response

    def create(
        self,
        name: str,
        response_structure: Any,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> CustomResponse:
        """Create a new custom response"""
        self.validate_required(
            {"name": name, "response_structure": response_structure},
            ["name", "response_structure"],
            "create custom response",
        )

        request_body = self.clean_dict(
            {
                "action": "create_custom_response",
                "name": name,
                "description": description,
                "response_structure": response_structure,
                "tags": tags or [],
            }
        )

        response = self.http.post(self.endpoint, request_body)
        response_data = response.get("data", {}).get("custom_response")
        return CustomResponse(**response_data)

    def update(self, response_id: str, **kwargs: Any) -> CustomResponse:
        """Update an existing custom response"""
        self.validate_required({"response_id": response_id}, ["response_id"], "update custom response")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        request_body = self.clean_dict(
            {"action": "update_custom_response", "custom_response_id": response_id, **kwargs}
        )

        response = self.http.post(self.endpoint, request_body)
        response_data = response.get("data", {}).get("custom_response")
        return CustomResponse(**response_data)

    def delete(self, response_id: str) -> None:
        """Delete a custom response"""
        self.validate_required({"response_id": response_id}, ["response_id"], "delete custom response")

        self.http.post(
            self.endpoint, {"action": "delete_custom_response", "custom_response_id": response_id}
        )

    def get_by_tag(self, tag: str) -> List[CustomResponse]:
        """Get custom responses by tag"""
        responses = self.list()
        return [r for r in responses if r.tags and tag in r.tags]
