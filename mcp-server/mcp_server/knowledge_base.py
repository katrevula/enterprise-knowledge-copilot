from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from .chunking import DocumentChunk, chunk_markdown
from .config import CHROMA_PERSIST_DIR, COLLECTION_NAME, DATA_DIR, EMBEDDING_MODEL


class KnowledgeBase:
    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        persist_dir: Path = CHROMA_PERSIST_DIR,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ) -> None:
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._embedding_function = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))

    def collection(self) -> Collection:
        return self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_function,
            metadata={"description": "Synthetic HR policy knowledge base"},
        )

    def load_chunks(self) -> list[DocumentChunk]:
        markdown_files = sorted(self.data_dir.glob("*.md"))
        chunks: list[DocumentChunk] = []
        for path in markdown_files:
            chunks.extend(chunk_markdown(path))
        return chunks

    def rebuild_index(self) -> dict[str, Any]:
        chunks = self.load_chunks()
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass

        collection = self.collection()
        if chunks:
            collection.add(
                ids=[chunk.id for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                metadatas=[
                    {
                        "source_id": chunk.source_id,
                        "chunk_id": chunk.chunk_id,
                        "title": chunk.title,
                        "section": chunk.section,
                        "file_path": chunk.file_path,
                    }
                    for chunk in chunks
                ],
            )

        return {
            "collection": self.collection_name,
            "document_count": len(list(self.data_dir.glob("*.md"))),
            "chunk_count": len(chunks),
            "persist_dir": str(self.persist_dir),
        }

    def search(self, query: str, top_k: int = 5) -> dict[str, Any]:
        top_k = max(1, min(top_k, 10))
        collection = self.collection()
        if collection.count() == 0:
            return {
                "query": query,
                "results": [],
                "warning": "Knowledge index is empty. Run the ingestion script first.",
            }

        raw = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]
        ids = raw.get("ids", [[]])[0]

        results = []
        for index, document in enumerate(documents):
            metadata = metadatas[index] or {}
            distance = float(distances[index]) if index < len(distances) else 0.0
            results.append(
                {
                    "source_id": metadata.get("source_id", ""),
                    "chunk_id": metadata.get("chunk_id", ""),
                    "title": metadata.get("title", "Untitled policy"),
                    "section": metadata.get("section", ""),
                    "excerpt": document,
                    "score": round(1 / (1 + max(distance, 0.0)), 4),
                    "distance": round(distance, 4),
                    "mcp_id": ids[index] if index < len(ids) else "",
                }
            )

        return {"query": query, "results": results}

    def get_excerpt(self, source_id: str, chunk_id: str) -> dict[str, Any]:
        collection = self.collection()
        mcp_id = f"{source_id}:{chunk_id}"
        raw = collection.get(ids=[mcp_id], include=["documents", "metadatas"])
        if not raw.get("ids"):
            return {"found": False, "source_id": source_id, "chunk_id": chunk_id}

        metadata = raw["metadatas"][0] or {}
        return {
            "found": True,
            "source_id": source_id,
            "chunk_id": chunk_id,
            "title": metadata.get("title", "Untitled policy"),
            "section": metadata.get("section", ""),
            "excerpt": raw["documents"][0],
        }

    def list_resources(self) -> dict[str, Any]:
        resources = []
        for path in sorted(self.data_dir.glob("*.md")):
            chunks = chunk_markdown(path)
            title = chunks[0].title if chunks else path.stem.replace("_", " ").title()
            resources.append(
                {
                    "source_id": path.stem.replace("_", "-"),
                    "title": title,
                    "path": str(path),
                    "chunk_count": len(chunks),
                }
            )
        return {"resources": resources}

