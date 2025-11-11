from typing import Literal

import torch
from llama_index.core.base.embeddings.base import (
    DEFAULT_EMBED_BATCH_SIZE,
)
from pydantic import BaseModel, model_validator
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR

from sinapsis_llama_index.helpers.rag_env_vars import RAGTextCompletionEnvVars


class VectorStoreDBConfig(BaseModel):
    """Configuration schema for PostgreSQL Vector Store connection.

    Attributes:
        user (str | None): Database user name. Loaded from PGVECTOR_USER if not provided. Defaults to `None`.
        password (str | None): Database password. Loaded from PGVECTOR_PASSWORD if not provided. Defaults to `None`.
        port (int): Database port number. Loaded from PGVECTOR_PORT if not provided. Defaults to `5432`.
        host (str): Database host address (hostname or IP). Loaded from PGVECTOR_HOST if not provided. Defaults to
            `"localhost"`.
        db_name (str): Name of the specific database to connect to. Defaults to `"sinapsis_db"`.
        table_name (str): Name of the table within the database containing the vectors. Defaults to `"sinapsis_table"`.
    """

    user: str | None = None
    password: str | None = None
    port: int = 5432
    host: str = "localhost"
    db_name: str = "sinapsis_db"
    table_name: str = "sinapsis_table"

    @model_validator(mode="before")
    @classmethod
    def load_from_env_vars(cls, data: dict) -> dict:
        """Loads DB credentials/config from env vars if not provided directly.

        Args:
            data (dict): The raw input data dictionary before validation.

        Raises:
            ValueError: If PGVECTOR_PORT env var is set but not a valid integer.
            ValueError: If 'user' or 'password' are not provided via input data
                        or environment variables.

        Returns:
            dict: The (potentially modified) data dictionary for Pydantic validation.
        """
        if data is None:
            data = {}

        env_user = RAGTextCompletionEnvVars.PGVECTOR_USER.value
        env_password = RAGTextCompletionEnvVars.PGVECTOR_PASSWORD.value
        env_host = RAGTextCompletionEnvVars.PGVECTOR_HOST.value
        env_port_str = RAGTextCompletionEnvVars.PGVECTOR_PORT.value

        if ("user" not in data or data.get("user") is None) and env_user is not None:
            data["user"] = env_user

        if ("password" not in data or data.get("password") is None) and env_password is not None:
            data["password"] = env_password

        if "host" not in data or data.get("host") is None:
            data["host"] = env_host if env_host is not None else "localhost"

        if "port" not in data or data.get("port") is None:
            if env_port_str is not None:
                try:
                    data["port"] = int(env_port_str)
                except (ValueError, TypeError):
                    raise ValueError(f"Environment variable PGVECTOR_PORT ('{env_port_str}') must be a valid integer.")
            else:
                data["port"] = 5432

        if not data.get("user") or not data.get("password"):
            raise ValueError(
                "Database 'user' and 'password' must be provided either directly "
                "or via PGVECTOR_USER/PGVECTOR_PASSWORD environment variables."
            )

        return data


class RetrieveArgs(BaseModel):
    """Configuration for LlamaIndex vector store retrieval.

    Attributes:
        query_mode (Literal["default", "sparse", "hybrid", "text_search", "semantic_hybrid"]): The LlamaIndex
            query mode to use for retrieval. Defaults to `"default"`.
        similarity_top_k (int): The maximum number of potentially relevant nodes to retrieve from the vector store
            before applying the similarity threshold. Defaults to `1`.
        threshold (float): The minimum similarity score required for a retrieved node to be considered relevant
            and included in the final results. Defaults to `0.85`.

    """

    query_mode: Literal["default", "sparse", "hybrid", "text_search", "semantic_hybrid"] = "default"
    similarity_top_k: int = 1
    threshold: float = 0.85


class HFEmbeddingConfig(BaseModel):
    """Configuration for the HuggingFaceEmbedding model from LlamaIndex.

    Attributes:
        model_name (str): The name or path of the HuggingFace embedding model (e.g., 'BAAI/bge-small-en-v1.5').
        max_length (int | None): Maximum sequence length for the model. Usually inferred if None. Defaults to `None`.
        query_instruction (str | None): Instruction prefix for query embeddings (e.g., for Instructor models).
            Defaults to `None`.
        text_instruction (str | None): Instruction prefix for document embeddings (e.g., for Instructor models).
            Defaults to `None`.
        normalize (bool): Whether to normalize the embeddings. Defaults to `True`.
        embed_batch_size (int): Batch size for embedding generation. Defaults to `DEFAULT_EMBED_BATCH_SIZE`.
        cache_folder (str): Path to cache directory for downloading/loading models. Defaults to `SINAPSIS_CACHE_DIR`.
        trust_remote_code (bool): Allow execution of remote code for custom models. Defaults to `False`.
        device (Literal["auto", "cuda", "cpu"]): The device to run the model on ('cuda', 'cpu', 'auto'). If 'auto',
            selects 'cuda' if available, otherwise 'cpu'. Defaults to `"auto"`.
        parallel_process (bool): Whether to use parallel processing if multiple GPUs are available. Defaults to `False`.
    """

    model_name: str
    max_length: int | None = None
    query_instruction: str | None = None
    text_instruction: str | None = None
    normalize: bool = True
    embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE
    cache_folder: str = SINAPSIS_CACHE_DIR
    trust_remote_code: bool = False
    device: Literal["auto", "cuda", "cpu"] = "auto"
    parallel_process: bool = False

    @model_validator(mode="after")
    def set_auto_device(self) -> "HFEmbeddingConfig":
        """Sets the device to 'cuda' or 'cpu' if set to 'auto'."""
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        return self


class SplitterArgs(BaseModel):
    """Base configuration arguments for LlamaIndex `NodeParser`s (splitters).

    Attributes:
        include_metadata (bool): Whether or not to consider metadata when splitting. Defaults to `True`.
        include_prev_next_rel (bool): Include prev/next node relationships. Defaults to `True`.
    """

    include_metadata: bool = True
    include_prev_next_rel: bool = True
