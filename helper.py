import re
import sqlparse
import json
from functools import lru_cache
from sqlalchemy import create_engine, text
from settings import ServerConfig
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword
import os
import yaml

# regex to capture up to three dot-separated identifier parts (supports `quote`, "quote", [brackets], or plain names)
IDENT_RE = re.compile(
    r'^[\s(]*'                                  
    r'(?P<name>(?:`[^`]+`|"[^"]+"|\[[^\]]+\]|[A-Za-z0-9_]+)'
    r'(?:\.(?:`[^`]+`|"[^"]+"|\[[^\]]+\]|[A-Za-z0-9_]+)){0,2})'
)

@lru_cache()
def get_db_connection():
  config = ServerConfig()
#   username = config.db_user or os.environ.get("DB_USER") 
#   password = config.db_password or os.environ.get("DB_PASSWORD")

  username = "analytics_api_dev"
  password = "xiZ8nQ90l4EKRtMWA1"
  
  engine = create_engine('redshift+psycopg2://{}:{}@localhost:5439/dev?sslmode=allow'.format(username, password))

  print("***engine", engine)  
  try:
    with engine.connect() as conn: conn.execute(text("SELECT 1"))
    print("Database connection successful")
  except Exception as e:
    print("Database connection failed:", e); raise
  
  return engine



# get database,schema,table name from sql query
def extract_database_schema_and_table(sql: str):
    """
    Returns a list of tuples (database, schema, table) for all FROM/JOIN/INTO/UPDATE occurrences.
    Missing parts are returned as None.
    """
    parsed = sqlparse.parse(sql)
    results = []
    for stmt in parsed:
        from_seen = False
        for token in stmt.tokens:
            # When we've seen FROM/JOIN/INTO/UPDATE, next identifiers are table refs
            if from_seen:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        results.append(parse_identifier(identifier))
                elif isinstance(token, Identifier):
                    results.append(parse_identifier(token))
                elif token.ttype is Keyword:
                    # reached next clause
                    from_seen = False
            if token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN', 'INTO', 'UPDATE'):
                from_seen = True
    return results

def normalize(part: str):
    """Strip surrounding quotes/backticks/brackets if present."""
    if not part:
        return None
    if (part[0] == '`' and part[-1] == '`') or (part[0] == '"' and part[-1] == '"') or (part[0] == '[' and part[-1] == ']'):
        return part[1:-1]
    return part

def parse_identifier(identifier: Identifier):
    """Return (database, schema, table) or (None, schema, table) or (None, None, table)."""
    s = identifier.value
    m = IDENT_RE.match(s)
    if not m:
        return (None, None, None)
    full = m.group('name')
    parts = full.split('.')
    parts = [normalize(p) for p in parts]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return None, parts[0], parts[1]
    if len(parts) == 1:
        return None, None, parts[0]
    return (None, None, None)

# read table schemas from given schema file and stores it in memory.
def read_schema_file():
    # Load YAML file
    file = ServerConfig().schema_file
    with open(file, "r") as f:
        data = yaml.safe_load(f)
    # Build mapping
    table_mapping = {}

    for model in data["models"]:
        table_name = model["name"]
        column_list = []
        for col in model.get("columns", []):
            column_list.append({
                "column_name": col.get("name"),
                "column_type": col.get("type"),
                "column_description": col.get("description"),
            })
        table_mapping[table_name] = column_list
    return table_mapping

def get_all_tables_schema_from_database():
    print("Getting all tables schema")
    with open('sql_permitted_tables.json', 'r') as f:
        data = json.load(f)
    database = data['database']
    schema = data['schema']
    
    result_dict = {}
    engine = get_db_connection()
    
    for table in data['tables']:
        query = f"""
        SELECT column_name, data_type
        FROM {database}.information_schema.columns
        WHERE table_schema = '{schema}'
          AND table_name   = '{table}'
        ORDER BY ordinal_position;
        """
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                rows = [list(row) for row in result.fetchall()]
            result_dict[table] = [{"name": r[0], "type": r[1]} for r in rows]
        except Exception as e:
            result_dict[table] = {"error": str(e)}
    
    print("Done")
    return result_dict