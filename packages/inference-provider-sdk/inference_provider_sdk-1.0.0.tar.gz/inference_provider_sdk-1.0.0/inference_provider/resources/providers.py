"""
Providers and Models resource client
"""

from typing import Any, Dict, List, Optional

from inference_provider.resources.base import BaseResource
from inference_provider.types import AIModel, AIProvider, ModelType, ProviderType


class Providers(BaseResource):
    """Providers and Models resource client"""

    # ============================================================================
    # Provider Methods
    # ============================================================================

    def list(self) -> List[AIProvider]:
        """List all providers"""
        response = self.http.post(self.endpoint, {"action": "list_providers"})
        providers_data = response.get("data", {}).get("providers", [])
        return [AIProvider(**provider) for provider in providers_data]

    def create(
        self,
        name: str,
        provider_type: ProviderType,
        api_endpoint: str,
        is_active: bool = True,
    ) -> AIProvider:
        """Create a new provider"""
        self.validate_required(
            {"name": name, "provider_type": provider_type, "api_endpoint": api_endpoint},
            ["name", "provider_type", "api_endpoint"],
            "create provider",
        )

        request_body = self.clean_dict(
            {
                "action": "create_provider",
                "name": name,
                "provider_type": provider_type.value if isinstance(provider_type, ProviderType) else provider_type,
                "api_endpoint": api_endpoint,
                "is_active": is_active,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        provider_data = response.get("data", {}).get("provider")
        return AIProvider(**provider_data)

    def update(self, provider_id: str, **kwargs: Any) -> AIProvider:
        """Update an existing provider"""
        self.validate_required({"provider_id": provider_id}, ["provider_id"], "update provider")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        request_body = self.clean_dict({"action": "update_provider", "provider_id": provider_id, **kwargs})

        response = self.http.post(self.endpoint, request_body)
        provider_data = response.get("data", {}).get("provider")
        return AIProvider(**provider_data)

    def delete(self, provider_id: str) -> None:
        """Delete a provider"""
        self.validate_required({"provider_id": provider_id}, ["provider_id"], "delete provider")

        self.http.post(self.endpoint, {"action": "delete_provider", "provider_id": provider_id})

    def set_api_key(self, provider_id: str, api_key: str) -> None:
        """Set provider API key"""
        self.validate_required(
            {"provider_id": provider_id, "api_key": api_key},
            ["provider_id", "api_key"],
            "set provider API key",
        )

        self.http.post(
            self.endpoint,
            {"action": "set_provider_api_key", "provider_id": provider_id, "api_key": api_key},
        )

    # ============================================================================
    # Model Methods
    # ============================================================================

    def list_models(self, provider_id: Optional[str] = None) -> List[AIModel]:
        """List all models"""
        request_body: Dict[str, Any] = {"action": "list_models"}

        if provider_id:
            request_body["provider_id"] = provider_id

        response = self.http.post(self.endpoint, request_body)
        models_data = response.get("data", {}).get("models", [])
        return [AIModel(**model) for model in models_data]

    def create_model(
        self,
        provider_id: str,
        name: str,
        display_name: str,
        context_window: int,
        max_output_tokens: int,
        input_cost_per_1k_tokens: float,
        output_cost_per_1k_tokens: float,
        model_type: ModelType,
        description: Optional[str] = None,
        supports_streaming: bool = False,
        supports_function_calling: bool = False,
        is_active: bool = True,
        embedding_dimensions: Optional[int] = None,
        supports_embeddings: bool = False,
    ) -> AIModel:
        """Create a new model"""
        self.validate_required(
            {
                "provider_id": provider_id,
                "name": name,
                "display_name": display_name,
                "context_window": context_window,
                "max_output_tokens": max_output_tokens,
                "input_cost_per_1k_tokens": input_cost_per_1k_tokens,
                "output_cost_per_1k_tokens": output_cost_per_1k_tokens,
                "model_type": model_type,
            },
            [
                "provider_id",
                "name",
                "display_name",
                "context_window",
                "max_output_tokens",
                "input_cost_per_1k_tokens",
                "output_cost_per_1k_tokens",
                "model_type",
            ],
            "create model",
        )

        # Validate embedding model has dimensions
        if model_type == ModelType.EMBEDDING and not embedding_dimensions:
            raise ValueError("embedding_dimensions is required for embedding models")

        request_body = self.clean_dict(
            {
                "action": "create_model",
                "provider_id": provider_id,
                "name": name,
                "display_name": display_name,
                "description": description,
                "context_window": context_window,
                "max_output_tokens": max_output_tokens,
                "input_cost_per_1k_tokens": input_cost_per_1k_tokens,
                "output_cost_per_1k_tokens": output_cost_per_1k_tokens,
                "model_type": model_type.value if isinstance(model_type, ModelType) else model_type,
                "supports_streaming": supports_streaming,
                "supports_function_calling": supports_function_calling,
                "is_active": is_active,
                "embedding_dimensions": embedding_dimensions,
                "supports_embeddings": supports_embeddings,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        model_data = response.get("data", {}).get("model")
        return AIModel(**model_data)

    def update_model(self, model_id: str, **kwargs: Any) -> AIModel:
        """Update an existing model"""
        self.validate_required({"model_id": model_id}, ["model_id"], "update model")

        if not kwargs:
            raise ValueError("At least one field must be provided for update")

        request_body = self.clean_dict({"action": "update_model", "model_id": model_id, **kwargs})

        response = self.http.post(self.endpoint, request_body)
        model_data = response.get("data", {}).get("model")
        return AIModel(**model_data)

    def delete_model(self, model_id: str) -> None:
        """Delete a model"""
        self.validate_required({"model_id": model_id}, ["model_id"], "delete model")

        self.http.post(self.endpoint, {"action": "delete_model", "model_id": model_id})

    def get_models_by_type(
        self, model_type: ModelType, provider_id: Optional[str] = None
    ) -> List[AIModel]:
        """Get models by type"""
        all_models = self.list_models(provider_id)
        return [model for model in all_models if model.model_type == model_type]

    def get_completion_models(self, provider_id: Optional[str] = None) -> List[AIModel]:
        """Get completion models"""
        return self.get_models_by_type(ModelType.COMPLETION, provider_id)

    def get_embedding_models(self, provider_id: Optional[str] = None) -> List[AIModel]:
        """Get embedding models"""
        return self.get_models_by_type(ModelType.EMBEDDING, provider_id)
