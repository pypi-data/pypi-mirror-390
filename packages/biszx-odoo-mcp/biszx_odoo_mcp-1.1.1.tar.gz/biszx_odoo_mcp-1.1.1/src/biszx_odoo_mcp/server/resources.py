"""
MCP Resources for Odoo integration

This module contains all the MCP resource functions for Odoo data access.
"""

from typing import Any, cast

from biszx_odoo_mcp.exceptions import OdooMCPError, ResourceError
from biszx_odoo_mcp.server.context import AppContext
from biszx_odoo_mcp.server.response import Response


async def search_models_resource(mcp: Any, query: str) -> str:
    """
    Resource for searching models from the Odoo application.

    This searches through model names and display names to find models that
    match the given query term.

    Args:
        query: Search term to find models (searches in model name and display name)

    Returns:
        JSON string with matching models
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.search_models(query)
        return Response(data=data).to_json_string()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_json_string()
    except Exception as e:
        resource_error = ResourceError(
            f"Unexpected error searching models: {str(e)}",
            resource_name="search_models_resource",
            details={"query": query},
            original_error=e,
        )
        return Response(error=resource_error.to_dict()).to_json_string()


async def get_model_fields_resource(mcp: Any, model_name: str, query_field: str) -> str:
    """
    Resource containing field definitions for a specific model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')
        query_field: Search term to find fields (searches in field name and string)

    Returns:
        JSON string with field definitions
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_fields(model_name, query_field)
        return Response(data=data).to_json_string()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_json_string()
    except Exception as e:
        resource_error = ResourceError(
            f"Unexpected error getting model fields: {str(e)}",
            resource_name="get_model_fields_resource",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=resource_error.to_dict()).to_json_string()


async def get_model_info_resource(mcp: Any, model_name: str) -> str:
    """
    Resource containing information about a specific model.

    Args:
        model_name: Name of the model (e.g., 'res.partner')

    Returns:
        JSON string with model information
    """
    # Access lifespan context to get the Odoo client
    ctx = mcp.get_context()
    app_context = cast(AppContext, ctx.request_context.lifespan_context)

    try:
        data = app_context.odoo.get_model_info(model_name)
        return Response(data=data).to_json_string()
    except OdooMCPError as e:
        return Response(error=e.to_dict()).to_json_string()
    except Exception as e:
        resource_error = ResourceError(
            f"Unexpected error getting model info: {str(e)}",
            resource_name="get_model_info_resource",
            details={"model_name": model_name},
            original_error=e,
        )
        return Response(error=resource_error.to_dict()).to_json_string()


async def get_domain_help_resource() -> str:
    """
    Resource containing help information about Odoo domain syntax.

    Returns:
        JSON string with domain syntax examples and explanations
    """
    domain_help = {
        "odoo_domain_syntax": {
            "description": "Odoo domains are used for filtering records",
            "syntax": "List of tuples: [('field', 'operator', 'value')]",
            "operators": {
                "=": "equals",
                "!=": "not equals",
                "<": "less than",
                "<=": "less than or equal",
                ">": "greater than",
                ">=": "greater than or equal",
                "in": "in list",
                "not in": "not in list",
                "like": "contains (case insensitive)",
                "ilike": "contains (case insensitive)",
                "=like": "matches pattern",
                "=ilike": "matches pattern (case insensitive)",
            },
            "logical_operators": {
                "&": "AND (default between conditions)",
                "|": "OR",
                "!": "NOT",
            },
            "examples": [
                {
                    "description": "Find companies only",
                    "domain": "[('is_company', '=', True)]",
                },
                {
                    "description": "Find partners with email containing 'gmail'",
                    "domain": "[('email', 'ilike', 'gmail')]",
                },
                {
                    "description": "Find products with price between 10 and 100",
                    "domain": "[('list_price', '>=', 10), ('list_price', '<=', 100)]",
                },
                {
                    "description": "Find active products or services",
                    "domain": (
                        "['|', ('type', '=', 'product'), "
                        "('type', '=', 'service'), ('active', '=', True)]"
                    ),
                },
                {
                    "description": "Find draft or confirmed sales orders",
                    "domain": "['|', ('state', '=', 'draft'), ('state', '=', 'sent')]",
                },
            ],
        }
    }

    response = Response(data=domain_help)
    return response.to_json_string()


async def get_operations_help_resource() -> str:
    """
    Resource containing help information about available MCP tools and operations.

    Returns:
        JSON string with operations documentation
    """
    operations_help = {
        "mcp_tools": {
            "data_retrieval": {
                "get_odoo_models": "Get list of all available models",
                "get_model_info": "Get information about a specific model",
                "get_model_fields": "Get field definitions for a model",
                "search_records": "Search for records with domain filters",
                "read_records": "Read specific records by IDs",
                "search_ids": "Get only IDs of matching records",
                "search_count": "Count records matching a domain",
            },
            "data_modification": {
                "create_record": "Create a single new record",
                "create_records": "Create multiple records at once",
                "write_record": "Update a single record",
                "write_records": "Update multiple records",
                "unlink_record": "Delete a single record",
                "unlink_records": "Delete multiple records",
            },
            "advanced": {
                "call_method": "Call custom methods on models",
                "search_and_update": "Search and update records in one operation",
            },
        },
        "common_workflows": [
            {
                "name": "Create a new customer",
                "steps": [
                    "1. Use create_record with model 'res.partner'",
                    (
                        "2. Provide values like {'name': 'Customer Name', "
                        "'email': 'email@domain.com', 'is_company': True}"
                    ),
                ],
            },
            {
                "name": "Search for products",
                "steps": [
                    "1. Use search_records with model 'product.template'",
                    (
                        "2. Use domain like [('name', 'ilike', 'search_term')] "
                        "to find products by name"
                    ),
                ],
            },
            {
                "name": "Update product price",
                "steps": [
                    "1. Use search_ids to find the product",
                    "2. Use write_records to update the list_price field",
                ],
            },
        ],
    }

    response = Response(data=operations_help)
    return response.to_json_string()
