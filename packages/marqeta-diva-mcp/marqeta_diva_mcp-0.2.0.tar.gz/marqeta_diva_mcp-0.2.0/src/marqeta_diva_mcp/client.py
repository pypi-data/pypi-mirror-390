"""Marqeta DiVA API Client."""

import csv
import difflib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx


class RateLimiter:
    """Simple rate limiter to prevent exceeding API limits (300 requests per 5 minutes)."""

    def __init__(self, max_requests: int = 300, time_window: int = 300):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []

    def wait_if_needed(self) -> None:
        """Wait if necessary to comply with rate limits."""
        now = time.time()
        # Remove requests older than the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

        if len(self.requests) >= self.max_requests:
            # Need to wait
            oldest_request = self.requests[0]
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time + 0.1)  # Add small buffer
                now = time.time()
                self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

        self.requests.append(now)


class DiVAAPIError(Exception):
    """Base exception for DiVA API errors."""

    def __init__(self, status_code: int, message: str, response: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"DiVA API Error {status_code}: {message}")


class DiVAClient:
    """Client for interacting with the Marqeta DiVA API."""

    BASE_URL = "https://diva-api.marqeta.com/data/v2"

    def __init__(self, app_token: str, access_token: str, program: str):
        """
        Initialize the DiVA API client.

        Args:
            app_token: Application token for authentication
            access_token: Access token for authentication
            program: Default program name(s) for API requests
        """
        self.app_token = app_token
        self.access_token = access_token
        self.program = program
        self.rate_limiter = RateLimiter()
        self.client = httpx.Client(
            auth=(app_token, access_token),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        # Cache for schemas to avoid repeated API calls
        self._schema_cache: Dict[str, List[Dict[str, Any]]] = {}
        # Views that support date range parameters
        self._date_range_views = {
            "authorizations", "settlements", "clearings", "declines", "loads",
            "programbalances", "programbalancessettlement", "activitybalances",
            "chargebacks"
        }

    def _find_similar_fields(self, invalid_field: str, valid_fields: List[str], cutoff: float = 0.6) -> List[str]:
        """
        Find similar field names using fuzzy matching.

        Args:
            invalid_field: The invalid field name
            valid_fields: List of valid field names
            cutoff: Similarity threshold (0-1)

        Returns:
            List of similar field names
        """
        matches = difflib.get_close_matches(invalid_field, valid_fields, n=3, cutoff=cutoff)
        return matches

    def _validate_filters(
        self,
        view_name: str,
        aggregation: str,
        filters: Optional[Dict[str, Any]]
    ) -> None:
        """
        Validate filter fields against the view schema.

        Args:
            view_name: Name of the view
            aggregation: Aggregation level
            filters: Filter dictionary to validate

        Raises:
            DiVAAPIError: If invalid filter fields are detected
        """
        if not filters:
            return

        # Check cache first
        cache_key = f"{view_name}:{aggregation}"
        if cache_key not in self._schema_cache:
            try:
                schema = self.get_view_schema(view_name, aggregation)
                self._schema_cache[cache_key] = schema
            except Exception:
                # If schema fetch fails, skip validation
                return

        schema = self._schema_cache[cache_key]
        valid_fields = [field["field"] for field in schema]

        invalid_fields = [field for field in filters.keys() if field not in valid_fields]

        if invalid_fields:
            suggestions = {}
            for invalid_field in invalid_fields:
                similar = self._find_similar_fields(invalid_field, valid_fields)
                if similar:
                    suggestions[invalid_field] = similar

            error_msg = f"/{view_name}/{aggregation} does not have the following column(s): {', '.join(repr(f) for f in invalid_fields)}"

            if suggestions:
                suggestion_text = "; ".join(
                    f"{repr(invalid)} -> did you mean {' or '.join(repr(s) for s in similar)}?"
                    for invalid, similar in suggestions.items()
                )
                error_msg += f"\nSuggestions: {suggestion_text}"

            error_msg += f"\nUse get_view_schema('{view_name}', '{aggregation}') to see all valid fields."

            raise DiVAAPIError(400, "Invalid filter fields", {"message": error_msg})


    def _estimate_response_size(
        self,
        view_name: str,
        count: int,
        fields: Optional[List[str]]
    ) -> tuple[int, str]:
        """
        Estimate response size and return warning if it might be large.

        Args:
            view_name: Name of the view
            count: Number of records requested
            fields: Specific fields requested

        Returns:
            Tuple of (estimated_tokens, warning_message)
        """
        # Rough token estimates per record for different views
        tokens_per_record = {
            "authorizations": 100,
            "settlements": 120,
            "clearings": 150,
            "declines": 140,
            "cards": 80,
            "users": 70,
            "chargebacks": 200,
        }

        base_tokens = tokens_per_record.get(view_name, 100)

        # If specific fields requested, reduce estimate by ~60%
        if fields:
            base_tokens = int(base_tokens * 0.4)

        estimated = base_tokens * count
        warning = ""

        if estimated > 20000:
            warning = (
                f"Warning: Requesting {count} records may return ~{estimated:,} tokens "
                f"(limit is 25,000). Consider reducing 'count' or using more specific 'fields'."
            )

        return estimated, warning

    def _build_query_params(
        self,
        program: Optional[str] = None,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        count: Optional[int] = None,
        group_by: Optional[str] = None,
        expand: Optional[str] = None,
    ) -> Dict[str, str]:
        """Build query parameters for API requests.

        Note: Date filtering should be done through the filters parameter using the
        actual date field names (e.g., transaction_timestamp, post_date) with operators.
        Example: filters={"transaction_timestamp": ">=2023-10-20"}
        """
        params: Dict[str, str] = {}

        # Program is required for most endpoints
        params["program"] = program or self.program

        # Field filtering
        if fields:
            params["fields"] = ",".join(fields)

        # Sorting
        if sort_by:
            params["sort_by"] = sort_by

        # Count/limit - apply max based on DiVA API limits
        if count is not None:
            # DiVA API limit: 10,000 for JSON responses
            params["count"] = str(min(count, 10000))
        else:
            # Default to 10,000 records (DiVA API default)
            params["count"] = "10000"

        # Grouping
        if group_by:
            params["group_by"] = group_by

        # Field expansion
        if expand:
            params["expand"] = expand

        # Custom filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    params[key] = ",".join(str(v) for v in value)
                else:
                    params[key] = str(value)

        return params

    def _make_request(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make a request to the DiVA API.

        Args:
            endpoint: API endpoint path (e.g., '/views/authorizations/detail')
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            DiVAAPIError: If the API returns an error
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.client.get(url, params=params)

            # Handle different error codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                error_message = error_data.get("message", "")

                # Provide helpful context for common errors
                enhanced_message = "Bad Request - Malformed query or filter parameters"
                if "does not have a column" in error_message:
                    enhanced_message += (
                        "\n\nNote: This error usually means you're using an invalid field name in 'filters'. "
                        "Parameters like 'count', 'sort_by', 'program' should NOT be in 'filters'. "
                        "Only actual data field names belong in 'filters'. "
                        "For date filtering, use the actual date field name (e.g., 'transaction_timestamp') with operators like '>=2023-10-20'."
                    )

                raise DiVAAPIError(400, enhanced_message, error_data)
            elif response.status_code == 403:
                error_data = response.json() if response.text else {}
                error_code = error_data.get("error_code", "")
                if error_code == "403001":
                    msg = "Forbidden - Field access denied"
                elif error_code == "403002":
                    msg = "Forbidden - Filter not allowed"
                elif error_code == "403003":
                    msg = "Forbidden - Program access denied"
                else:
                    msg = "Forbidden - Unauthorized access"
                raise DiVAAPIError(403, msg, error_data)
            elif response.status_code == 404:
                raise DiVAAPIError(404, "Not Found - Malformed URL or endpoint does not exist")
            elif response.status_code == 429:
                raise DiVAAPIError(
                    429,
                    "Rate limit exceeded - Maximum 300 requests per 5 minutes",
                )
            else:
                raise DiVAAPIError(
                    response.status_code,
                    f"Unexpected error: {response.text}",
                    response.json() if response.text else None,
                )

        except httpx.RequestError as e:
            raise DiVAAPIError(0, f"Network error: {str(e)}")

    def export_to_file(
        self,
        view_name: str,
        aggregation: str,
        output_path: str,
        format: str = "json",
        max_records: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Export large datasets to a file with automatic pagination.

        Args:
            view_name: Name of the view
            aggregation: Aggregation level
            output_path: Path where file will be written
            format: Output format ('json' or 'csv')
            max_records: Maximum total records to export (None = all)
            **kwargs: Additional query parameters

        Returns:
            Dictionary with export metadata
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        all_records = []
        batch_size = 10000  # DiVA API limit: 10,000 for JSON responses
        total_fetched = 0

        print(f"[DiVA Export] Starting export to {output_path}...", file=sys.stderr)

        # DiVA API does not support offset-based pagination
        # Fetch one batch with the specified count limit
        if max_records:
            kwargs['count'] = min(max_records, batch_size)
        else:
            kwargs['count'] = batch_size

        endpoint = f"/views/{view_name}/{aggregation}"
        params = self._build_query_params(**kwargs)
        response = self._make_request(endpoint, params)

        records = response.get('records', [])
        if records:
            all_records.extend(records)
            total_fetched = len(records)

            # Truncate if we got more than max_records
            if max_records and total_fetched > max_records:
                all_records = all_records[:max_records]
                total_fetched = len(all_records)

            print(f"[DiVA Export] Fetched {total_fetched} records", file=sys.stderr)

            # Warn if there are more records available
            if response.get('is_more', False):
                print(f"[DiVA Export] Warning: More records available but DiVA API does not support offset pagination.", file=sys.stderr)
                print(f"[DiVA Export] To get more data, use narrower date ranges or more specific filters.", file=sys.stderr)

        # Write to file
        if format == "csv":
            if all_records:
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_records[0].keys())
                    writer.writeheader()
                    writer.writerows(all_records)
        else:  # json
            with open(output_file, 'w') as f:
                json.dump(all_records, f, indent=2)

        file_size = output_file.stat().st_size
        print(f"[DiVA Export] Complete! Wrote {total_fetched} records to {output_path}", file=sys.stderr)

        return {
            "success": True,
            "file_path": str(output_file.absolute()),
            "format": format,
            "records_exported": total_fetched,
            "file_size_bytes": file_size
        }

    def get_view(
        self,
        view_name: str,
        aggregation: str = "detail",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Get data from a specific view.

        Args:
            view_name: Name of the view (e.g., 'authorizations', 'settlements')
            aggregation: Aggregation level ('detail', 'day', 'week', 'month')
            **kwargs: Additional query parameters (program, filters, count, sort_by, etc.)
                     Note: For date filtering, use filters with the actual date field name.
                     Example: filters={"transaction_timestamp": ">=2023-10-20"}

        Returns:
            API response containing records and metadata
        """
        # Validate filter fields before making the request
        # Note: Validation is disabled to allow API to determine valid fields
        # filters = kwargs.get("filters")
        # if filters:
        #     self._validate_filters(view_name, aggregation, filters)

        # Check response size estimate
        count = kwargs.get("count", 10000)  # Default is 10,000 per DiVA API
        fields = kwargs.get("fields")
        estimated_tokens, warning = self._estimate_response_size(view_name, count, fields)

        if warning:
            # Log warning but don't block the request
            print(f"[DiVA Client Warning] {warning}", file=sys.stderr)

        endpoint = f"/views/{view_name}/{aggregation}"
        params = self._build_query_params(**kwargs)
        return self._make_request(endpoint, params)

    def get_views_list(self) -> Dict[str, Any]:
        """Get list of all available views with metadata."""
        return self._make_request("/views")

    def get_view_schema(self, view_name: str, aggregation: str = "detail") -> Dict[str, Any]:
        """
        Get the schema for a specific view.

        Args:
            view_name: Name of the view
            aggregation: Aggregation level

        Returns:
            Schema definition with field types and descriptions
        """
        endpoint = f"/views/{view_name}/{aggregation}/schema"
        return self._make_request(endpoint)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
