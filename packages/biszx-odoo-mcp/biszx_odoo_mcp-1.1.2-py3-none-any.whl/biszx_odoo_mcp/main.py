"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

import inspect
import os
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from biszx_odoo_mcp.server import resources, tools
from biszx_odoo_mcp.server.context import AppContext
from biszx_odoo_mcp.tools.odoo_client import get_odoo_client


def init() -> None:
    """
    Initialize the Odoo MCP Server environment
    """
    try:
        from dotenv import load_dotenv  # pylint: disable=import-outside-toplevel

        load_dotenv()
    except ImportError:
        pass

    # Configure loguru with appropriate log level
    logger.remove()
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
    )


@asynccontextmanager
async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    """Application lifespan for initialization and cleanup"""
    odoo_client = get_odoo_client()
    try:
        yield AppContext(odoo=odoo_client)
    finally:
        pass


# Create MCP server
mcp = FastMCP(
    name="Odoo MCP Server",
    instructions="MCP Server for interacting with Odoo ERP systems",
    dependencies=["requests"],
    lifespan=app_lifespan,
)


# Tool registration helper
def tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to register a tool that calls the underlying function with mcp"""

    # Get the original function signature
    sig = inspect.signature(func)

    # Create a new signature excluding the 'mcp' parameter
    new_params = [p for name, p in sig.parameters.items() if name != "mcp"]
    new_sig = sig.replace(parameters=new_params)

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(mcp, *args, **kwargs)

    # Set wrapper properties manually to match the new signature
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = {
        k: v for k, v in func.__annotations__.items() if k != "mcp"
    }

    # Set the corrected signature
    object.__setattr__(wrapper, "__signature__", new_sig)

    return mcp.tool()(wrapper)


# Resource wrapper functions
async def search_models_resource(query: str):
    """Search for models by name or description"""
    return await resources.search_models_resource(mcp, query)


async def model_info_resource(model_name: str):
    """Get information about a specific model"""
    return await resources.get_model_info_resource(mcp, model_name)


async def model_fields_resource(model_name: str, query_field: str) -> str:
    """Get field definitions for a specific model"""
    return await resources.get_model_fields_resource(mcp, model_name, query_field)


init()

# Register all resources directly
mcp.resource("odoo://models/search/{query}")(search_models_resource)
mcp.resource("odoo://models/{model_name}/info")(model_info_resource)
mcp.resource("odoo://models/{model_name}/fields/{query_field}")(model_fields_resource)
mcp.resource("odoo://help/domains")(resources.get_domain_help_resource)
mcp.resource("odoo://help/operations")(resources.get_operations_help_resource)


# Register all tools using the helper
tool(tools.search_models)
tool(tools.get_model_info)
tool(tools.get_model_fields)
tool(tools.search_records)
tool(tools.read_records)
tool(tools.create_record)
tool(tools.create_records)
tool(tools.write_record)
tool(tools.write_records)
tool(tools.unlink_record)
tool(tools.unlink_records)
tool(tools.search_count)
tool(tools.search_ids)
tool(tools.call_method)
tool(tools.search_and_update)
