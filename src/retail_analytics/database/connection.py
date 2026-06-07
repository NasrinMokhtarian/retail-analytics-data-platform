import os
from dataclasses import dataclass
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

@dataclass
class PostgresConfig:
    host: str
    port: str
    database: str
    user: str
    password: str

def load_postgres_config() -> PostgresConfig:
    load_dotenv()
    required_env_vars =[
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT"
     ]  
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables:{missing_vars}")
    return PostgresConfig(
        host = os.environ["POSTGRES_HOST"],
        port = int(os.environ["POSTGRES_PORT"]),
        database = os.environ["POSTGRES_DB"],
        user = os.environ["POSTGRES_USER"],
        password = os.environ["POSTGRES_PASSWORD"]
    )

def get_postgres_connection() -> connection:
    config = load_postgres_config()
    return psycopg2.connect(
        host = config.host,
        port = config.port,
        dbname = config.database,
        user = config.user,
        password = config.password
    )

def get_sqlalchemy_engine() -> Engine:
    config = load_postgres_config()

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )

    return create_engine(database_url)