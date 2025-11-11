"""Vector store management for transaction embeddings using ChromaDB."""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings


class TransactionVectorStore:
    """Manages vector storage and retrieval for transaction embeddings."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory where ChromaDB will persist data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        print(f"[VectorStore] Initializing ChromaDB at {self.persist_directory}...", file=sys.stderr)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Collection for transactions
        self.collection_name = "transactions"
        self.collection = None

        print(f"[VectorStore] ChromaDB initialized successfully", file=sys.stderr)

    def create_collection(self, embedding_dimension: int = 384) -> None:
        """
        Create or get the transactions collection.

        Args:
            embedding_dimension: Dimension of embedding vectors (default: 384 for MiniLM)
        """
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"[VectorStore] Collection '{self.collection_name}' ready", file=sys.stderr)
        except Exception as e:
            print(f"[VectorStore] Error creating collection: {e}", file=sys.stderr)
            raise

    def add_transactions(
        self,
        transactions: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """
        Add transactions and their embeddings to the vector store.

        Args:
            transactions: List of transaction dictionaries
            embeddings: List of embedding vectors

        Returns:
            Number of transactions added
        """
        if self.collection is None:
            self.create_collection()

        if len(transactions) != len(embeddings):
            raise ValueError(f"Mismatch: {len(transactions)} transactions, {len(embeddings)} embeddings")

        # Prepare data for ChromaDB
        ids = []
        metadatas = []
        documents = []

        for txn in transactions:
            # Use transaction_token as ID
            txn_id = txn.get("transaction_token")
            if not txn_id:
                print(f"[VectorStore] Warning: Transaction missing token, skipping", file=sys.stderr)
                continue

            # ChromaDB requires string IDs - convert if needed
            if not isinstance(txn_id, str):
                txn_id = str(txn_id)

            ids.append(txn_id)

            # Store essential metadata for filtering
            metadata = {
                "merchant_name": txn.get("merchant_name", ""),
                "transaction_amount": float(txn.get("transaction_amount", 0.0)),
                "transaction_type": txn.get("transaction_type", ""),
                "state": txn.get("state", txn.get("transaction_status", "")),
                "user_token": txn.get("user_token", txn.get("acting_user_token", "")),
                "card_token": txn.get("card_token", ""),
                "created_time": txn.get("created_time", txn.get("transaction_timestamp", "")),
                "network": txn.get("network", ""),
            }

            # Remove empty values to save space
            metadata = {k: v for k, v in metadata.items() if v}

            metadatas.append(metadata)

            # Store human-readable document text
            doc_parts = []
            if metadata.get("merchant_name"):
                doc_parts.append(f"Merchant: {metadata['merchant_name']}")
            if metadata.get("transaction_amount"):
                doc_parts.append(f"Amount: ${metadata['transaction_amount']:.2f}")
            if metadata.get("transaction_type"):
                doc_parts.append(f"Type: {metadata['transaction_type']}")

            documents.append(" | ".join(doc_parts) if doc_parts else txn_id)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

        print(f"[VectorStore] Added {len(ids)} transactions to vector store", file=sys.stderr)
        return len(ids)

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar transactions.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filter conditions (e.g., {"transaction_amount": {"$gt": 100}})
            where_document: Document text filter conditions

        Returns:
            Dictionary with ids, distances, metadatas, and documents
        """
        if self.collection is None:
            self.create_collection()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document
        )

        # Reformat results for easier consumption
        if results["ids"] and results["ids"][0]:
            formatted_results = {
                "count": len(results["ids"][0]),
                "transactions": []
            }

            for i in range(len(results["ids"][0])):
                formatted_results["transactions"].append({
                    "transaction_token": results["ids"][0][i],
                    "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "document": results["documents"][0][i] if results["documents"] else ""
                })

            return formatted_results
        else:
            return {"count": 0, "transactions": []}

    def get_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a transaction by its ID.

        Args:
            transaction_id: Transaction token

        Returns:
            Transaction data or None if not found
        """
        if self.collection is None:
            self.create_collection()

        try:
            result = self.collection.get(ids=[transaction_id], include=["embeddings", "metadatas", "documents"])

            if result["ids"]:
                return {
                    "transaction_token": result["ids"][0],
                    "embedding": result["embeddings"][0] if result["embeddings"] else None,
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                    "document": result["documents"][0] if result["documents"] else ""
                }
        except Exception as e:
            print(f"[VectorStore] Error retrieving transaction {transaction_id}: {e}", file=sys.stderr)

        return None

    def delete_transactions(self, transaction_ids: List[str]) -> int:
        """
        Delete transactions from the vector store.

        Args:
            transaction_ids: List of transaction tokens to delete

        Returns:
            Number of transactions deleted
        """
        if self.collection is None:
            return 0

        try:
            self.collection.delete(ids=transaction_ids)
            print(f"[VectorStore] Deleted {len(transaction_ids)} transactions", file=sys.stderr)
            return len(transaction_ids)
        except Exception as e:
            print(f"[VectorStore] Error deleting transactions: {e}", file=sys.stderr)
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with collection statistics
        """
        if self.collection is None:
            return {
                "collection_name": self.collection_name,
                "count": 0,
                "persist_directory": str(self.persist_directory),
                "status": "not_initialized"
            }

        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "count": count,
            "persist_directory": str(self.persist_directory),
            "status": "initialized"
        }

    def clear(self) -> None:
        """Clear all data from the collection."""
        if self.collection is not None:
            print(f"[VectorStore] Clearing collection '{self.collection_name}'...", file=sys.stderr)
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            print(f"[VectorStore] Collection cleared", file=sys.stderr)


# Global vector store instance (lazy-loaded)
_vector_store: TransactionVectorStore | None = None


def get_vector_store(persist_directory: str = "./chroma_db") -> TransactionVectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = TransactionVectorStore(persist_directory=persist_directory)
    return _vector_store
