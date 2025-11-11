import psycopg
from llama_index.vector_stores.postgres import PGVectorStore
from psycopg.errors import DuplicateDatabase, Error, InsufficientPrivilege, OperationalError
from sinapsis_core.utils.logging_utils import sinapsis_logger


def ensure_postgres_db_exists(host: str, port: str, user: str, password: str, db_name: str) -> None:
    """Ensures a specific PostgreSQL database exists, creating it if necessary.

    Args:
        host (str): The database server host address.
        port (str): The port number for the database server.
        user (str): The username to connect with.
        password (str): The password for the user.
        db_name (str): The name of the database to check for and create.

    Raises:
        RuntimeError: If the connection to the default database fails.
    """
    default_conn_str = f"host={host} port={port} user={user} password={password} dbname=postgres"
    try:
        with psycopg.connect(default_conn_str, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cur.fetchone():
                sinapsis_logger.debug(f"Database '{db_name}' does not exist. Creating it...")
                cur.execute(f'CREATE DATABASE "{db_name}"')
    except (OperationalError, InsufficientPrivilege, DuplicateDatabase, Error) as e:
        raise RuntimeError(f"Failed to connect to default 'postgres' db or check/create database '{db_name}': {e}")


def drop_table(
    db_name: str,
    table_name: str,
    user: str,
    password: str,
    host: str = "localhost",
    port: str = "5432",
) -> None:
    """Connects to the DB and issues a DROP TABLE command using psycopg.

    This is highly destructive and will delete the table schema and all data.

    Args:
        db_name (str): Name of the database to connect to
        table_name (str): Name of the table
        user (str): Username for the database connection
        password (str): Password for the database connection
        host (str, optional): Host direction for the database. Defaults to "localhost".
        port (str, optional): Port where the database is hosted. Defaults to "5432".

    Raises:
        RuntimeError: If the connection to the default database fails.
    """
    conn_str = f"host={host} port={port} user={user} password={password} dbname={db_name}"
    try:
        with psycopg.connect(conn_str, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(f'DROP TABLE IF EXISTS "data_{table_name}";')
            sinapsis_logger.info(f"Successfully dropped table: {table_name}")
    except (OperationalError, InsufficientPrivilege, DuplicateDatabase, Error) as e:
        raise RuntimeError(f"Database operation failed for dropping table '{table_name}': {e}")


def connect_to_table(
    db_name: str,
    table_name: str,
    user: str,
    password: str,
    dimension: int = 384,
    host: str = "localhost",
    port: str = "5432",
) -> PGVectorStore:
    """Creates and connects to a PostgreSQL vector table using LlamaIndex's `PGVectorStore`.

    This method initializes a `PGVectorStore` instance with the given database connection
    details and returns it to interact with the vector table in the database.

    Args:
        db_name (str): Name of the database to connect to
        table_name (str): Name of the table
        user (str): Username for the database connection
        password (str): Password for the database connection
        dimension (int): Dimension of the vector database
        host (str, optional): Host direction for the database. Defaults to "localhost".
        port (str, optional): Port where the database is hosted. Defaults to "5432".

    Returns:
        PGVectorStore: An instance of the `PGVectorStore` that allows interacting with the
            PostgreSQL vector table.
    """
    vector_store = PGVectorStore.from_params(
        database=db_name,
        host=host,
        password=password,
        port=port,
        user=user,
        table_name=table_name,
        embed_dim=dimension,
    )
    return vector_store


def clear_table(
    db_name: str,
    table_name: str,
    user: str,
    password: str,
    dimension: int = 384,
    host: str = "localhost",
    port: str = "5432",
) -> None:
    """Method to clear a table from a PGVector database.

    Args:
        db_name (str): Name of the database to connect to
        table_name (str): Name of the table
        user (str): Username for the database connection
        password (str): Password for the database connection
        dimension (int): Dimension of the vector database
        host (str, optional): Host direction for the database. Defaults to "localhost".
        port (str, optional): Port where the database is hosted. Defaults to "5432".
    """
    database = connect_to_table(db_name, table_name, user, password, dimension, host, port)
    database.clear()
