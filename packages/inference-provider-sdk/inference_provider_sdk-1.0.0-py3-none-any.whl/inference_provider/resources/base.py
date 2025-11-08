"""
Base resource class for common functionality
"""

from typing import Any, Dict, List, Union

from inference_provider.errors import ValidationError
from inference_provider.http_client import AsyncHttpClient, HttpClient


class BaseResource:
    """Base resource class"""

    def __init__(self, http: Union[HttpClient, AsyncHttpClient], endpoint: str):
        self.http = http
        self.endpoint = endpoint

    def validate_required(self, data: Dict[str, Any], required_fields: List[str], context: str = "request") -> None:
        """Validate required fields in an object"""
        missing = [
            field
            for field in required_fields
            if field not in data or data[field] is None or data[field] == ""
        ]

        if missing:
            raise ValidationError(
                f"Missing required fields in {context}: {', '.join(missing)}",
                field=missing[0],
            )

    def clean_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from dictionary"""
        return {k: v for k, v in data.items() if v is not None}
