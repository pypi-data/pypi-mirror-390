"""
RAG (Retrieval-Augmented Generation) resource client
"""

from typing import Any, Dict, List, Optional, Union

from inference_provider.resources.base import BaseResource
from inference_provider.types import Document, DocumentCollection, SimilaritySearchResult
from inference_provider.utils import encode_file_to_base64


class RAG(BaseResource):
    """RAG resource client"""

    # ============================================================================
    # Collection Methods
    # ============================================================================

    def list_collections(self) -> List[DocumentCollection]:
        """List all collections"""
        response = self.http.post(self.endpoint, {"action": "list_collections"})
        collections_data = response.get("data", {}).get("collections", [])
        return [DocumentCollection(**collection) for collection in collections_data]

    def get_collection(self, collection_id: str) -> DocumentCollection:
        """Get collection by ID"""
        self.validate_required({"collection_id": collection_id}, ["collection_id"], "get collection")

        response = self.http.post(
            self.endpoint, {"action": "get_collection", "collection_id": collection_id}
        )
        collection_data = response.get("data", {}).get("collection")
        return DocumentCollection(**collection_data)

    def create_collection(
        self,
        name: str,
        embedding_model: str,
        embedding_dimensions: int,
        description: Optional[str] = None,
        metadata: Optional[Any] = None,
    ) -> DocumentCollection:
        """Create a new collection"""
        self.validate_required(
            {"name": name, "embedding_model": embedding_model, "embedding_dimensions": embedding_dimensions},
            ["name", "embedding_model", "embedding_dimensions"],
            "create collection",
        )

        request_body = self.clean_dict(
            {
                "action": "create_collection",
                "name": name,
                "description": description,
                "embedding_model": embedding_model,
                "embedding_dimensions": embedding_dimensions,
                "metadata": metadata,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        collection_data = response.get("data", {}).get("collection")
        return DocumentCollection(**collection_data)

    def delete_collection(self, collection_id: str) -> None:
        """Delete a collection"""
        self.validate_required({"collection_id": collection_id}, ["collection_id"], "delete collection")

        self.http.post(self.endpoint, {"action": "delete_collection", "collection_id": collection_id})

    # ============================================================================
    # Document Methods
    # ============================================================================

    def list_documents(self, collection_id: str) -> List[Document]:
        """List documents in a collection"""
        self.validate_required({"collection_id": collection_id}, ["collection_id"], "list documents")

        response = self.http.post(
            self.endpoint, {"action": "list_documents", "collection_id": collection_id}
        )
        documents_data = response.get("data", {}).get("documents", [])
        return [Document(**document) for document in documents_data]

    def create_document(
        self,
        collection_id: str,
        title: str,
        content: str,
        metadata: Optional[Any] = None,
    ) -> Document:
        """Create a new document"""
        self.validate_required(
            {"collection_id": collection_id, "title": title, "content": content},
            ["collection_id", "title", "content"],
            "create document",
        )

        request_body = self.clean_dict(
            {
                "action": "create_document",
                "collection_id": collection_id,
                "title": title,
                "content": content,
                "metadata": metadata,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        document_data = response.get("data", {}).get("document")
        return Document(**document_data)

    def delete_document(self, document_id: str) -> None:
        """Delete a document"""
        self.validate_required({"document_id": document_id}, ["document_id"], "delete document")

        self.http.post(self.endpoint, {"action": "delete_document", "document_id": document_id})

    def upload_file(
        self,
        collection_id: str,
        file_name: str,
        file_content: Union[bytes, bytearray, str],
        title: Optional[str] = None,
        metadata: Optional[Any] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> Document:
        """Upload file to collection"""
        self.validate_required(
            {"collection_id": collection_id, "file_name": file_name, "file_content": file_content},
            ["collection_id", "file_name", "file_content"],
            "upload file",
        )

        # Convert file content to base64 if it's bytes
        if isinstance(file_content, (bytes, bytearray)):
            base64_content = encode_file_to_base64(file_content)
        else:
            base64_content = file_content

        request_body = self.clean_dict(
            {
                "action": "upload_file",
                "collection_id": collection_id,
                "file_name": file_name,
                "file_content": base64_content,
                "title": title or file_name,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "metadata": metadata,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        document_data = response.get("data", {}).get("document")
        return Document(**document_data)

    # ============================================================================
    # Search Methods
    # ============================================================================

    def similarity_search(
        self,
        collection_id: str,
        query: str,
        match_threshold: float = 0.7,
        match_count: int = 5,
        embedding_model_id: Optional[str] = None,
    ) -> List[SimilaritySearchResult]:
        """Perform similarity search"""
        self.validate_required(
            {"collection_id": collection_id, "query": query}, ["collection_id", "query"], "similarity search"
        )

        request_body = self.clean_dict(
            {
                "action": "similarity_search",
                "collection_id": collection_id,
                "query": query,
                "match_threshold": match_threshold,
                "match_count": match_count,
                "embedding_model_id": embedding_model_id,
            }
        )

        response = self.http.post(self.endpoint, request_body)
        results_data = response.get("data", {}).get("results", [])
        return [SimilaritySearchResult(**result) for result in results_data]

    # ============================================================================
    # Maintenance Methods
    # ============================================================================

    def regenerate_embeddings(self, collection_id: str, embedding_model_id: str) -> None:
        """Regenerate embeddings for a collection"""
        self.validate_required(
            {"collection_id": collection_id, "embedding_model_id": embedding_model_id},
            ["collection_id", "embedding_model_id"],
            "regenerate embeddings",
        )

        self.http.post(
            self.endpoint,
            {
                "action": "regenerate_embeddings",
                "collection_id": collection_id,
                "embedding_model_id": embedding_model_id,
            },
        )

    # ============================================================================
    # Convenience Methods
    # ============================================================================

    def create_collection_with_documents(
        self,
        collection_name: str,
        embedding_model: str,
        embedding_dimensions: int,
        documents: List[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create collection and upload documents in one operation"""
        # Create collection
        collection = self.create_collection(
            name=collection_name,
            description=description,
            embedding_model=embedding_model,
            embedding_dimensions=embedding_dimensions,
        )

        # Upload documents
        uploaded_docs: List[Document] = []
        for doc in documents:
            uploaded = self.create_document(
                collection_id=collection.id,
                title=doc["title"],
                content=doc["content"],
                metadata=doc.get("metadata"),
            )
            uploaded_docs.append(uploaded)

        return {"collection": collection, "documents": uploaded_docs}

    def search_relevant(
        self,
        collection_id: str,
        query: str,
        threshold: float = 0.7,
        count: int = 5,
        embedding_model_id: Optional[str] = None,
    ) -> List[SimilaritySearchResult]:
        """Search with automatic relevance filtering"""
        return self.similarity_search(
            collection_id=collection_id,
            query=query,
            match_threshold=threshold,
            match_count=count,
            embedding_model_id=embedding_model_id,
        )
