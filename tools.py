from server import mcp, schemas
from typing import Dict, List
from sqlalchemy import text
from helper import extract_database_schema_and_table, get_db_connection
import os
import json


# @mcp.tool(name="health_check")
# def health_check() -> dict:
#     """
#     Simple GET tool to check if the MCP server is up.
#     """
#     return {"status": "ok", "message": "MCP proxy is working!"}


# @mcp.tool(name="get_tables_schema")
# def get_tables_schema(tables:list) -> Dict:
#   '''
#   Returns schema of a tables as a  dictionary. Each entry consists of:
#     Key: table name
#     Values: Dictionary. Each sub dictionary contains:
#       - column_name: name of a column
#       - column_type: type of cilumn
#       - column_description - descritpion of column values and purpose

#   Examples:
#   - Single table schema : get_tables_schema(["api_analytics_orders"])
#   - Multiple tables schema : get_tables_schema(["api_analytics_orders", "api_analytics_products"])
#   Args:
#     tables: list of tables to get schema for
#   Returns:
#     Dictionary containing schema for each table in the input list.
#   '''

#   return {t: schemas[t] for t in tables if t in schemas}

@mcp.tool(name="get_tables_schema")
def get_tables_schema(tables: list) -> Dict:
    """
    Returns schema of tables as a dictionary. Works with table names
    with or without database/schema prefixes like 'platinum.'.
    
    Each entry consists of:
        Key: table name
        Values: Dictionary with:
            - column_name: name of the column
            - column_type: type of column
            - column_description: description of column values and purpose

    Examples:
    - Single table schema: get_tables_schema(["api__analytics__ratings"])
    - Multiple tables schema: get_tables_schema(["api__analytics__ratings", "api__analytics__coupons"])
    
    Args:
        tables: list of tables to get schema for
    Returns:
        Dictionary containing schema for each table in the input list.
    """
    result = {}
    for t in tables:
        key = t.split('.')[-1]  # Remove prefix if any
        for schema_key in schemas.keys():
            if schema_key.lower() == key.lower():
                result[schema_key] = schemas[schema_key]
                break
    return result

@mcp.tool(name="run_sql_query")
def run_sql_query(query:str) -> Dict:
  '''
  Runs given sql query on redshift and returns the result.
  Args:
    query: sql querystring to execute
  Returns:
    Dictionary contianing sql query result.
  '''
  # Block query with blacklisted keywords
  blacklisted_keywords = ['INSERT', 'DROP', 'DELETE', 'TRUNCATE', 'ALTER']
  sql = query.upper().strip()
  for keyword in blacklisted_keywords:
    if keyword in sql and not sql.startswith('SELECT'):
      return {"error": f"Query contains blacklisted keyword: {keyword}"}
  
  # Check if select statement is not using any table outside permitted list
  if sql.startswith('SELECT'):
    database,schema, table =extract_database_schema_and_table(sql)[0]
    with open("sql_permitted_tables.json") as f:
      data = json.load(f)
  
    if not database is None and data['database'].upper() != database:
        return {"error": f"Database {database} access denied"}
    if data['schema'].upper() != schema:
        return {"error": f"Schema {schema} access denied in database"}
    if not table in [t.upper() for t in list(schemas.keys())]:
        return {"error": f"Table {table} access denied in schema {schema}"}      

  # run query
  engine = get_db_connection()
  if not sql:
      return {"error": "No SQL provided"}

  try:
      with engine.connect() as conn:
          result = conn.execute(text(sql))
          rows = [list(row) for row in result.fetchall()]
      return {"rows": rows}
  except Exception as e:
      return {"error": str(e)}
