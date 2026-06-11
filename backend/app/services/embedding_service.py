from app.config import settings
from loguru import logger
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings


class EmbeddingService:
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()

    def _initialize(self):
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name="academic_assistant",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.warning(f"ChromaDB connection failed: {e}. Using in-memory mode.")
            self.client = chromadb.EphemeralClient()
            self.collection = self.client.get_or_create_collection(
                name="academic_assistant",
                metadata={"hnsw:space": "cosine"},
            )

    async def add_document(self, doc_id: str, text: str, metadata: dict = None) -> str:
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            return doc_id
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {e}")
            return doc_id

    async def search(self, query: str, n_results: int = 5) -> list[dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            output = []
            for i in range(len(results["ids"][0])):
                output.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                })
            return output
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

    async def delete_document(self, doc_id: str):
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            logger.error(f"Failed to delete from ChromaDB: {e}")

    async def get_collection_stats(self) -> dict:
        try:
            count = self.collection.count()
            return {"count": count, "status": "connected"}
        except Exception as e:
            return {"count": 0, "status": f"error: {e}"}
