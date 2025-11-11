"""Local SQLite storage for complete transaction data."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class TransactionStorage:
    """Local SQLite storage for complete transaction data."""

    def __init__(self, db_path: str = "./transactions.db"):
        """
        Initialize the transaction storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[Storage] Initializing SQLite database at {self.db_path}...", file=sys.stderr)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        self._create_tables()

        print(f"[Storage] SQLite database ready", file=sys.stderr)

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Main transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_token TEXT PRIMARY KEY,
                view_name TEXT NOT NULL,
                aggregation TEXT NOT NULL,
                merchant_name TEXT,
                transaction_amount REAL,
                transaction_type TEXT,
                state TEXT,
                user_token TEXT,
                card_token TEXT,
                business_user_token TEXT,
                created_time TEXT,
                transaction_timestamp TEXT,
                network TEXT,
                merchant_category_code TEXT,
                currency_code TEXT,
                full_data TEXT NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_merchant_name
            ON transactions(merchant_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_amount
            ON transactions(transaction_amount)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_token
            ON transactions(user_token)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_business_user_token
            ON transactions(business_user_token)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_time
            ON transactions(created_time)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_view_name
            ON transactions(view_name)
        """)

        self.conn.commit()

    def add_transactions(
        self,
        transactions: List[Dict[str, Any]],
        view_name: str,
        aggregation: str
    ) -> int:
        """
        Add or update transactions in the database.

        Args:
            transactions: List of transaction dictionaries
            view_name: DiVA view name
            aggregation: Aggregation level

        Returns:
            Number of transactions added/updated
        """
        cursor = self.conn.cursor()
        count = 0

        for txn in transactions:
            transaction_token = txn.get("transaction_token")
            if not transaction_token:
                print(f"[Storage] Warning: Transaction missing token, skipping", file=sys.stderr)
                continue

            # Extract common fields for indexing
            merchant_name = txn.get("merchant_name", txn.get("acquirer_merchant_name"))
            transaction_amount = txn.get("transaction_amount")
            transaction_type = txn.get("transaction_type")
            state = txn.get("state", txn.get("transaction_status"))
            user_token = txn.get("user_token", txn.get("acting_user_token"))
            card_token = txn.get("card_token")
            business_user_token = txn.get("business_user_token")
            created_time = txn.get("created_time", txn.get("transaction_timestamp"))
            transaction_timestamp = txn.get("transaction_timestamp")
            network = txn.get("network")
            merchant_category_code = txn.get("merchant_category_code")
            currency_code = txn.get("currency_code")

            # Store full transaction as JSON
            full_data = json.dumps(txn)

            # Upsert (insert or replace)
            cursor.execute("""
                INSERT OR REPLACE INTO transactions (
                    transaction_token, view_name, aggregation,
                    merchant_name, transaction_amount, transaction_type,
                    state, user_token, card_token, business_user_token,
                    created_time, transaction_timestamp, network,
                    merchant_category_code, currency_code, full_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_token, view_name, aggregation,
                merchant_name, transaction_amount, transaction_type,
                state, user_token, card_token, business_user_token,
                created_time, transaction_timestamp, network,
                merchant_category_code, currency_code, full_data
            ))

            count += 1

        self.conn.commit()
        print(f"[Storage] Added/updated {count} transactions", file=sys.stderr)
        return count

    def get_transactions(
        self,
        transaction_tokens: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get transactions by their tokens.

        Args:
            transaction_tokens: List of transaction tokens

        Returns:
            List of complete transaction dictionaries
        """
        if not transaction_tokens:
            return []

        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(transaction_tokens))

        cursor.execute(f"""
            SELECT full_data FROM transactions
            WHERE transaction_token IN ({placeholders})
        """, transaction_tokens)

        results = []
        for row in cursor.fetchall():
            full_data = json.loads(row["full_data"])
            results.append(full_data)

        return results

    def query_transactions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_time DESC"
    ) -> Dict[str, Any]:
        """
        Query transactions with filters.

        Args:
            filters: Dictionary of filters (e.g., {"merchant_name": "Starbucks", "transaction_amount": {">": 10}})
            limit: Maximum number of results
            offset: Offset for pagination
            order_by: SQL ORDER BY clause

        Returns:
            Dictionary with results and metadata
        """
        cursor = self.conn.cursor()

        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Handle operators like {"transaction_amount": {">": 10}}
                    for op, val in value.items():
                        if op in [">", "<", ">=", "<=", "=", "!="]:
                            where_clauses.append(f"{field} {op} ?")
                            params.append(val)
                        elif op == "like":
                            where_clauses.append(f"{field} LIKE ?")
                            params.append(f"%{val}%")
                else:
                    # Simple equality
                    where_clauses.append(f"{field} = ?")
                    params.append(value)

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM transactions WHERE {where_clause}
        """, params)
        total_count = cursor.fetchone()["count"]

        # Get results
        cursor.execute(f"""
            SELECT full_data FROM transactions
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """, params + [limit, offset])

        results = []
        for row in cursor.fetchall():
            full_data = json.loads(row["full_data"])
            results.append(full_data)

        return {
            "total": total_count,
            "count": len(results),
            "offset": offset,
            "limit": limit,
            "is_more": offset + len(results) < total_count,
            "data": results
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the local storage.

        Returns:
            Dictionary with storage statistics
        """
        cursor = self.conn.cursor()

        # Total transactions
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        total_count = cursor.fetchone()["count"]

        # By view
        cursor.execute("""
            SELECT view_name, aggregation, COUNT(*) as count
            FROM transactions
            GROUP BY view_name, aggregation
        """)
        by_view = [dict(row) for row in cursor.fetchall()]

        # Date range
        cursor.execute("""
            SELECT
                MIN(created_time) as earliest,
                MAX(created_time) as latest
            FROM transactions
        """)
        date_range = dict(cursor.fetchone())

        # Database file size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            "database_path": str(self.db_path.absolute()),
            "total_transactions": total_count,
            "by_view": by_view,
            "date_range": date_range,
            "database_size_bytes": db_size,
            "database_size_mb": round(db_size / (1024 * 1024), 2)
        }

    def clear(self, view_name: Optional[str] = None) -> int:
        """
        Clear transactions from the database.

        Args:
            view_name: If specified, only clear transactions from this view

        Returns:
            Number of transactions deleted
        """
        cursor = self.conn.cursor()

        if view_name:
            cursor.execute("DELETE FROM transactions WHERE view_name = ?", (view_name,))
            count = cursor.rowcount
            print(f"[Storage] Cleared {count} transactions from view '{view_name}'", file=sys.stderr)
        else:
            cursor.execute("DELETE FROM transactions")
            count = cursor.rowcount
            print(f"[Storage] Cleared all {count} transactions", file=sys.stderr)

        self.conn.commit()
        return count

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global storage instance (lazy-loaded)
_storage: TransactionStorage | None = None


def get_storage(db_path: str = "./transactions.db") -> TransactionStorage:
    """Get or create the global transaction storage instance."""
    global _storage
    if _storage is None:
        _storage = TransactionStorage(db_path=db_path)
    return _storage
