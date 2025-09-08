from typing import Optional, Literal
from dotenv import load_dotenv
import os

load_dotenv()

# class ServerConfig:
#     db_url: str = os.getenv("DB_URL")
#     db_user: str = os.getenv("DB_USER")
#     db_password: str = os.getenv("DB_PASSWORD")
#     # mcp_transport: Literal["stdio", "streamable-http"] = "streamable-http"
#     schema_file:str = "_api__analytics__models.yml"


class ServerConfig:
    db_url: str = ""
    db_user: str = ""
    db_password: str = ""
    schema_file: str = "_api__analytics__models.yml"