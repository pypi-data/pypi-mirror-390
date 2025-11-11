"""Transaction embedding generation for RAG capabilities."""

import sys
from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer


class TransactionEmbedder:
    """Generates embeddings for financial transactions."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the transaction embedder.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default: all-MiniLM-L6-v2 (fast, lightweight, 384 dimensions)
        """
        print(f"[Embeddings] Loading model: {model_name}...", file=sys.stderr)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"[Embeddings] Model loaded. Embedding dimension: {self.embedding_dim}", file=sys.stderr)

    def format_transaction_text(self, transaction: Dict[str, Any]) -> str:
        """
        Format a transaction into text for embedding.

        Args:
            transaction: Transaction dictionary from DiVA API

        Returns:
            Formatted text string combining key transaction attributes
        """
        parts = []

        # Merchant name (most important)
        merchant = transaction.get("merchant_name", transaction.get("acquirer_merchant_name", ""))
        if merchant:
            parts.append(f"Merchant: {merchant}")

        # Transaction amount
        amount = transaction.get("transaction_amount")
        if amount is not None:
            currency_code = transaction.get("currency_code", "USD")
            parts.append(f"Amount: {amount} {currency_code}")

        # Transaction type/status
        txn_type = transaction.get("transaction_type")
        if txn_type:
            parts.append(f"Type: {txn_type}")

        state = transaction.get("state", transaction.get("transaction_status"))
        if state:
            parts.append(f"Status: {state}")

        # Merchant category
        mcc = transaction.get("merchant_category_code")
        if mcc:
            parts.append(f"MCC: {mcc}")

        # Cardholder presence
        card_presence = transaction.get("card_presence_indicator")
        if card_presence:
            parts.append(f"Card Presence: {card_presence}")

        # Network
        network = transaction.get("network")
        if network:
            parts.append(f"Network: {network}")

        # If we have very little info, at least include tokens
        if len(parts) < 2:
            txn_token = transaction.get("transaction_token")
            if txn_token:
                parts.append(f"Transaction: {txn_token}")

        return " | ".join(parts)

    def embed_transaction(self, transaction: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a single transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Embedding vector as list of floats
        """
        text = self.format_transaction_text(transaction)
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_transactions_batch(self, transactions: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Generate embeddings for multiple transactions efficiently.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of embedding vectors
        """
        texts = [self.format_transaction_text(txn) for txn in transactions]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Natural language search query

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()


# Global embedder instance (lazy-loaded)
_embedder: TransactionEmbedder | None = None


def get_embedder() -> TransactionEmbedder:
    """Get or create the global transaction embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = TransactionEmbedder()
    return _embedder
