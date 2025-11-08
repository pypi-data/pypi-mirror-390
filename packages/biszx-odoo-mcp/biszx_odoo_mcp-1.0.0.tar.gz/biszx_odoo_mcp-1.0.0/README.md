# Odoo MCP Server

An MCP server implementation for Odoo ERP systems, providing a set of tools for managing Odoo records, models, and custom methods.
Inspired by [tuanle96/mcp-odoo](https://github.com/tuanle96/mcp-odoo).

## Tools

### Core CRUD Operations

- **create_record**: Create a single new record

  - Inputs: `model_name` (string), `values` (object)
  - Returns: Dictionary with created record ID

- **create_records**: Create multiple records at once

  - Inputs: `model_name` (string), `values_list` (array of objects)
  - Returns: Dictionary with created record IDs

- **read_records**: Read specific records by their IDs

  - Inputs: `model_name` (string), `ids` (array), `fields` (optional array)
  - Returns: Dictionary with record data

- **write_record**: Update a single record

  - Inputs: `model_name` (string), `record_id` (number), `values` (object)
  - Returns: Dictionary with operation result

- **write_records**: Update multiple records

  - Inputs: `model_name` (string), `record_ids` (array), `values` (object)
  - Returns: Dictionary with operation result

- **unlink_record**: Delete a single record

  - Inputs: `model_name` (string), `record_id` (number)
  - Returns: Dictionary with operation result

- **unlink_records**: Delete multiple records
  - Inputs: `model_name` (string), `record_ids` (array)
  - Returns: Dictionary with operation result

### Search and Query Operations

- **search_records**: Search for records with advanced filtering

  - Inputs: `model_name` (string), `domain` (array), `fields` (optional array), `limit` (optional number), `offset` (optional number), `order` (optional string)
  - Returns: Dictionary with matching records

- **search_ids**: Get only IDs of matching records

  - Inputs: `model_name` (string), `domain` (array), `offset` (optional number), `limit` (optional number), `order` (optional string)
  - Returns: Dictionary with list of IDs

- **search_count**: Count records matching a domain
  - Inputs: `model_name` (string), `domain` (array)
  - Returns: Dictionary with count

### Model Operations

- **search_models**: Search for available models in the Odoo system

  - Inputs: `query` (string) - Search term for model names and display names
  - Returns: Dictionary with matching models

- **get_model_info**: Get information about a specific model

  - Inputs: `model_name` (string)
  - Returns: Dictionary with model information

- **get_model_fields**: Get field definitions for a model
  - Inputs: `model_name` (string), `query_field` (string)
  - Returns: Dictionary with field definitions

### Utility Operations

- **search_and_update**: Search and update records in one operation

  - Inputs: `model_name` (string), `domain` (array), `values` (object)
  - Returns: Dictionary with affected record count and IDs

- **call_method**: Call custom methods on models

  - Inputs: `model_name` (string), `method_name` (string), `args` (optional array), `kwargs` (optional object)
  - Returns: Dictionary with method result

## Resources

### Model Information

- **odoo://models/search/{query}**: Search for models by name or description
- **odoo://models/{model_name}/info**: Information about a specific model
- **odoo://models/{model_name}/fields**: Field definitions for a specific model

### Documentation

- **odoo://help/domains**: Complete guide to Odoo domain syntax with examples
- **odoo://help/operations**: Documentation of all available MCP tools and workflows

## Configuration

### Odoo Connection Setup

To connect to your Odoo instance, set the following environment variables:

- `ODOO_URL`: Your Odoo server URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: Login username
- `ODOO_PASSWORD`: Password or API key
- `ODOO_TIMEOUT`: Connection timeout in seconds (default: 30)
- `ODOO_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
- `LOG_LEVEL`: Logging level (default: INFO)

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "uvx",
      "args": ["biszx-odoo-mcp"],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key"
      }
    }
  }
}
```

## Installation

### Python Package

```bash
pip install biszx-odoo-mcp
```

### Running the Server

```bash
# Using the installed package
biszx-odoo-mcp

# Using uv for development
uv run biszx-odoo-mcp

# Using the MCP development tools
uv run mcp dev src/biszx_odoo_mcp/main.py
```

## License

This MCP server is licensed under the MIT License.
