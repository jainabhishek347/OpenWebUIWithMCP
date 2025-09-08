import warnings
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", message=".*ssl.SSLContext() without protocol.*")

from server import mcp
from settings import ServerConfig

# Import tools,resources and prompts so they get registered via decorators
from tools import run_sql_query, get_tables_schema
from resources import database_permitted_tables
from prompt import get_data

# import tools
# import resources
# import prompt


 
# Entry point to run the server
if __name__ == "__main__":
    # mcp.run(transport = ServerConfig())
    mcp.run()
    # config = ServerConfig()
    # mcp.run(schema_file=config.schema_file)