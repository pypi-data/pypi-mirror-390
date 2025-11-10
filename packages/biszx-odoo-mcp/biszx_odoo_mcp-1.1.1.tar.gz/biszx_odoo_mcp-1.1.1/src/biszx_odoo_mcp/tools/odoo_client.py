"""
Odoo client for interacting with Odoo via JSON-RPC using OdooRPC library.

TABLE OF CONTENTS:
=================

1. INITIALIZATION AND CONNECTION MANAGEMENT
   - __init__()
   - _connect()
   - _ensure_connected()

2. MODEL INTROSPECTION
   - get_models()
   - get_model_info()
   - get_model_fields()
3. SEARCH AND READ OPERATIONS
   - search_ids()
   - search_count()
   - search_read()
   - read_records()

4. CRUD OPERATIONS
   - create_record()
   - create_records()
   - write_records()
   - unlink_records()
   - copy_record()

5. ACCESS CONTROL
   - check_access_rights()

6. GENERIC METHOD EXECUTION
   - execute_method()
   - call_method()
"""

import urllib.parse
from typing import Any, Protocol, cast

import odoorpc  # type: ignore
from loguru import logger
from odoorpc.error import InternalError, RPCError  # type: ignore
from odoorpc.rpc.error import ConnectorError  # type: ignore

from biszx_odoo_mcp.exceptions import (
    AuthenticationError,
    ConnectionTimeoutError,
    InternalServerError,
    ModelNotFoundError,
    OdooRPCError,
)
from biszx_odoo_mcp.tools.config import Config


class OdooModelProtocol(Protocol):
    """Protocol defining the interface for Odoo model proxy objects"""

    def search(self, domain: list[Any], **kwargs: Any) -> list[int]:
        """Search for record IDs"""
        ...

    def search_count(self, domain: list[Any]) -> int:
        """Count records matching domain"""
        ...

    def search_read(
        self, domain: list[Any], fields: list[str] | None = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Search and read records"""
        ...

    def browse(self, ids: list[int]) -> Any:
        """Browse records by IDs"""
        ...

    def create(self, values: list[dict[str, Any]]) -> Any:
        """Create records"""
        ...

    def fields_get(self) -> dict[str, Any]:
        """Get field definitions"""
        ...

    def check_access_rights(self, operation: str, raise_exception: bool = True) -> bool:
        """Check access rights for the given operation"""
        ...


class OdooClient:
    """
    Client for interacting with Odoo via JSON-RPC
    """

    # ============================================================================
    # INITIALIZATION AND CONNECTION MANAGEMENT
    # ============================================================================

    def __init__(
        self,
        config: Config,
    ) -> None:
        """
        Initialize the Odoo client with connection parameters

        Args:
            config: Odoo client configuration
        """
        self.config = config
        parsed_url = urllib.parse.urlparse(self.config.url)
        self.hostname = parsed_url.netloc
        self.odoo: odoorpc.ODOO | None = None  # Will be initialized in _connect
        self.uid: int | None = None  # Will be set after login
        self._connect()

    def _ensure_connected(self) -> Any:
        """Ensure we have a valid connection"""
        if self.odoo is None:
            raise InternalServerError("Not connected to Odoo")
        return self.odoo

    def _get_model(self, model_name: str) -> OdooModelProtocol:
        """Get a model proxy with proper typing"""
        odoo_conn = self._ensure_connected()
        return cast(OdooModelProtocol, odoo_conn.env[model_name])

    def _connect(self) -> None:
        """Initialize the OdooRPC connection and authenticate"""
        logger.debug(f"Connecting to Odoo at: {self.config.url}")
        logger.debug(f"Database: {self.config.db}, User: {self.config.username}")

        try:
            # Determine protocol and port based on URL scheme
            is_https = self.config.url.startswith("https://")
            protocol = "jsonrpc+ssl" if is_https else "jsonrpc"
            port = 443 if is_https else 80

            self.odoo = odoorpc.ODOO(
                self.hostname,
                protocol=protocol,
                port=port,
                timeout=self.config.timeout,
                version=None,
            )
            self.odoo.login(self.config.db, self.config.username, self.config.password)

            # Get user ID for later use
            user_model = self._get_model("res.users")
            user_records = user_model.search([("login", "=", self.config.username)])
            self.uid = user_records[0] if user_records else None

            logger.info("✅ Successfully connected to Odoo")

        except (RPCError, InternalError, ConnectorError) as e:
            # Log connection errors as they're important for debugging
            logger.error(f"🔴 Failed to connect to Odoo: {str(e)}")

            # Check specific error types and raise appropriate custom exceptions
            error_msg = str(e).lower()
            if isinstance(e, RPCError):
                if "access" in error_msg or "denied" in error_msg:
                    raise AuthenticationError(
                        f"Authentication failed: {str(e)}",
                        username=self.config.username,
                        database=self.config.db,
                    ) from e
                raise OdooRPCError(error=e, method="connect") from e
            if isinstance(e, ConnectorError):
                raise ConnectionTimeoutError(
                    f"Connection failed: {str(e)}", timeout=self.config.timeout
                ) from e
            raise InternalServerError(f"Internal error: {str(e)}") from e

    # ============================================================================
    # MODEL INTROSPECTION
    # ============================================================================

    def search_models(self, query: str) -> dict[str, Any]:
        """
        Search for models that match a query term

        This searches through model names and display names to find models that
        match the given query term.

        Args:
            query: Search term to find models (searches in model name and display name)

        Returns:
            Dictionary with search results

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> results = client.search_models('partner')
            >>> print(results['length'])
            3
            >>> print([m['model'] for m in results['models']])
            ['res.partner', 'res.partner.bank', 'res.partner.category']
        """
        try:
            IrModel = self._get_model("ir.model")
            IrModel.check_access_rights("read")
            domain = [
                "&",
                ("transient", "=", False),
                "&",
                "|",
                ("model", "like", query),
                ("name", "like", query),
                "|",
                "&",
                ("model", "not like", "base.%"),
                ("model", "not like", "ir.%"),
                (
                    "model",
                    "in",
                    [
                        "ir.attachment",
                        "ir.model",
                        "ir.model.fields",
                    ],
                ),
            ]
            matching_models = IrModel.search_read(domain, ["model", "name"])
            return {
                "query": query,
                "length": len(matching_models),
                "models": [
                    {
                        "model": model["model"],
                        "name": model["name"],
                    }
                    for model in matching_models
                ],
            }
        except RPCError as e:
            raise OdooRPCError(e, method="search_models") from e

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        """
        Get information about a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary with model information

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> info = client.get_model_info('res.partner')
            >>> print(info['name'])
            'Contact'
        """
        try:
            IrModel = self._get_model("ir.model")
            IrModel.check_access_rights("read")
            result = IrModel.search_read(
                [("model", "=", model_name)], ["model", "name"]
            )
            if not result:
                raise ModelNotFoundError(model_name)
            return result[0]
        except RPCError as e:
            raise OdooRPCError(e, method="get_model_info") from e

    def get_model_fields(
        self, model_name: str, query: str | None = None
    ) -> dict[str, Any]:
        """
        Get field definitions for a specific model

        Args:
            model_name: Name of the model (e.g., 'res.partner')

        Returns:
            Dictionary mapping field names to their definitions

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> fields = client.get_model_fields('res.partner')
            >>> print(fields['name']['type'])
            'char'
        """
        try:
            Model = self._get_model(model_name)
            data: dict[str, Any] = Model.fields_get()
            result: dict[str, Any] = {
                "length": 0,
                "fields": {},
            }
            if query is not None:
                for field, value in data.items():
                    if "related" in value:
                        continue

                    if all(
                        {
                            query.lower() in field.lower()
                            or query.lower() in value["string"].lower(),
                        }
                    ):
                        result["fields"][field] = {
                            "name": field,
                            "string": value["string"],
                            "type": value["type"],
                            "required": value.get("required", False),
                            "readonly": value.get("readonly", False),
                            "searchable": value.get("searchable", False),
                            "relation": value.get("relation", False),
                        }
            else:
                result["fields"] = data
            result["length"] = len(result["fields"])
            return result
        except RPCError as e:
            raise OdooRPCError(e, method="get_model_fields") from e

    # ============================================================================
    # SEARCH AND READ OPERATIONS
    # ============================================================================

    def search_ids(
        self,
        model_name: str,
        domain: list[Any],
        offset: int | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> list[int]:
        """
        Search for record IDs that match a domain

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Sorting criteria (e.g., 'name ASC, id DESC')

        Returns:
            List of matching record IDs

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> ids = client.search_ids(
            ...     'res.partner', [('is_company', '=', True)], limit=5
            ... )
            >>> print(ids)
            [1, 2, 3, 4, 5]
        """
        try:
            Model = self._get_model(model_name)

            # Build search kwargs
            search_kwargs: dict[str, Any] = {}
            if offset is not None:
                search_kwargs["offset"] = offset
            if limit is not None:
                search_kwargs["limit"] = limit
            if order is not None:
                search_kwargs["order"] = order

            return Model.search(domain, **search_kwargs)
        except RPCError as e:
            raise OdooRPCError(e, method="search_ids") from e

    def search_count(self, model_name: str, domain: list[Any]) -> int:
        """
        Count records that match a search domain

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])

        Returns:
            Integer count of matching records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> count = client.search_count('res.partner', [('is_company', '=', True)])
            >>> print(count)
            25
        """
        try:
            Model = self._get_model(model_name)
            return Model.search_count(domain)
        except RPCError as e:
            raise OdooRPCError(e, method="search_count") from e

    def search_read(
        self,
        model_name: str,
        domain: list[Any],
        fields: list[str] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for records and read their data in a single call

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            domain: Search domain (e.g., [('is_company', '=', True)])
            fields: List of field names to return (None for all)
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Sorting criteria (e.g., 'name ASC, id DESC')

        Returns:
            List of dictionaries with the matching records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.search_read('res.partner', [
                    ('is_company', '=', True)
                ], limit=5)
            >>> print(len(records))
            5
        """
        try:
            Model = self._get_model(model_name)

            # Build search_read arguments
            search_kwargs: dict[str, Any] = {}
            if offset is not None:
                search_kwargs["offset"] = offset
            if fields is not None:
                search_kwargs["fields"] = fields
            if limit is not None:
                search_kwargs["limit"] = limit
            if order is not None:
                search_kwargs["order"] = order

            result = Model.search_read(domain, **search_kwargs)
            return result
        except RPCError as e:
            raise OdooRPCError(e, method="search_read") from e

    def read_records(
        self,
        model_name: str,
        ids: list[int],
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Read data of records by IDs

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            ids: List of record IDs to read
            fields: List of field names to return (None for all)

        Returns:
            List of dictionaries with the requested records

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> records = client.read_records('res.partner', [1])
            >>> print(records[0]['name'])
            'YourCompany'
        """
        try:
            Model = self._get_model(model_name)

            if fields is not None:
                result = Model.browse(ids).read(fields)
            else:
                result = Model.browse(ids).read()

            return cast(list[dict[str, Any]], result)
        except RPCError as e:
            raise OdooRPCError(e, method="read_records") from e

    # ============================================================================
    # CRUD OPERATIONS
    # ============================================================================

    def create_records(
        self, model_name: str, values_list: list[dict[str, Any]]
    ) -> int | list[int]:
        """
        Create records in an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            values_list: List of dictionaries with field values for the new records

        Returns:
            List of created record IDs

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> record_ids = client.create_records('res.partner', [
                    {'name': 'Company 1'}, {'name': 'Company 2'}
                ])
            >>> print(record_ids)
            [42, 43]
        """
        try:
            Model = self._get_model(model_name)
            return cast(int | list[int], Model.create(values_list))
        except RPCError as e:
            raise OdooRPCError(e, method="create_records") from e

    def write_records(
        self,
        model_name: str,
        record_ids: list[int],
        values: dict[str, Any],
    ) -> bool:
        """
        Update records in an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            record_ids: List of record IDs to update
            values: Dictionary with field values to update

        Returns:
            Boolean indicating success

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> success = client.write_records(
            ...     'res.partner', [1], {'name': 'Updated Name'}
            ... )
            >>> print(success)
            True
        """
        try:
            Model = self._get_model(model_name)
            records = Model.browse(record_ids)
            return cast(bool, records.write(values))
        except RPCError as e:
            raise OdooRPCError(e, method="write_records") from e

    def unlink_records(self, model_name: str, record_ids: list[int]) -> bool:
        """
        Delete records from an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            record_ids: List of record IDs to delete

        Returns:
            Boolean indicating success

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> success = client.unlink_records('res.partner', [42])
            >>> print(success)
            True
        """
        try:
            Model = self._get_model(model_name)
            records = Model.browse(record_ids)
            return cast(bool, records.unlink())
        except RPCError as e:
            raise OdooRPCError(e, method="unlink_records") from e

    # ============================================================================
    # GENERIC METHOD EXECUTION
    # ============================================================================

    def execute_method(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        """
        Execute an arbitrary method on a model

        Args:
            model: The model name (e.g., 'res.partner')
            method: Method name to execute
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            Result of the method execution
        """
        try:
            model_proxy = self._get_model(model)
            # Use getattr to dynamically call the method on the model proxy
            method_func = getattr(model_proxy, method)
            return method_func(*args, **kwargs)
        except RPCError as e:
            raise OdooRPCError(e, method=f"execute_method: {model}.{method}") from e

    def call_method(
        self,
        model_name: str,
        method_name: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> Any:
        """
        Call a custom method on an Odoo model

        Args:
            model_name: Name of the model (e.g., 'res.partner')
            method_name: Name of the method to call
            args: Positional arguments to pass to the method
            kwargs: Keyword arguments to pass to the method

        Returns:
            Method result

        Examples:
            >>> client = OdooClient(url, db, username, password)
            >>> result = client.call_method('res.partner', 'name_get', [1], {})
            >>> print(result)
            [(1, 'YourCompany')]
        """
        try:
            model_proxy = self._get_model(model_name)
            # Use getattr to dynamically call the method on the model proxy
            method_func = getattr(model_proxy, method_name)
            result = method_func(*args, **kwargs)
            if result is None:
                raise ValueError(f"Failed to call method {method_name}")
            return result
        except RPCError as e:
            raise OdooRPCError(
                e, method=f"call_method: {model_name}.{method_name}"
            ) from e


def get_odoo_client() -> OdooClient:
    """
    Get a configured Odoo client instance

    Returns:
        OdooClient: A configured Odoo client instance
    """
    return OdooClient(config=Config())
