from fastmcp import FastMCP
from helper import read_schema_file

# Initialize MCP server
mcp = FastMCP(
    name="Redshift MCP Server",
    instructions="Execute SQL queries and inspect table schema in AWS Redshift.")


# Load schemas
schemas = read_schema_file()
