from server import mcp, schemas 
from typing import Any
import json

# @mcp.resource("file://database_permitted_tables")
# def database_permitted_tables() -> Any:
#   '''
#   Returns information about database, schema and tables which are allowed to acces  or execute sql query against.
#   '''
#   with open("sql_permitted_tables.json") as f:
#     data = json.load(f)
#   data['tables'] = list(schemas.keys())
#   return data
  
# @mcp.tool
# def database_permitted_tables() -> Any:
#     """
#     Returns information about the database, schema, and tables
#     which are allowed to be accessed or queried.
#     """
#     with open("sql_permitted_tables.json") as f:
#         data = json.load(f)
#     data['tables'] = list(schemas.keys())
#     return data

# @mcp.tool
# def database_permitted_tables() -> dict:
#     return {
#         "database": "dev",
#         "schema": "platinum",
#         "tables": list(schemas.keys())  
#     }


@mcp.tool
def database_permitted_tables() -> dict:
    schema_name = "platinum"
    return {
        "database": "dev",
        "schema": "platinum",
        "tables": [f"{schema_name}.{table}" for table in schemas.keys()] 
    }