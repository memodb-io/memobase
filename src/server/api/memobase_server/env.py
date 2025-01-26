"""
Initialize logger, encoder, and config.
"""

import os
from rich.logging import RichHandler
import yaml
import logging
import tiktoken
import dataclasses
from dataclasses import dataclass, field
from typing import Optional, Literal
from dotenv import load_dotenv

load_dotenv()


class TelemetryKeyName:
    insert_blob_request = "insert_blob_request"
    insert_blob_success_request = "insert_blob_success_request"
    llm_input_tokens = "llm_input_tokens"
    llm_output_tokens = "llm_output_tokens"
    has_request = "has_request"


@dataclass
class Config:
    # IMPORTANT!
    persistent_chat_blobs: bool = False

    system_prompt: str = None
    buffer_flush_interval: int = 60 * 60  # 1 hour
    max_chat_blob_buffer_token_size: int = 1024
    max_profile_subtopics: int = 15
    max_pre_profile_token_size: int = 512
    llm_tab_separator: str = "::"
    cache_user_profiles_ttl: int = 60 * 20  # 20 minutes

    # LLM
    language: Literal["en", "zh"] = "en"
    llm_style: Literal["openai", "doubao_cache"] = "openai"
    llm_base_url: str = None
    llm_api_key: str = None
    best_llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    embedding_max_token_size: int = 8192

    additional_user_profiles: list[dict] = field(default_factory=list)
    overwrite_user_profiles: Optional[list[dict]] = None

    @classmethod
    def load_config(cls) -> "Config":
        if not os.path.exists("config.yaml"):
            LOG.warning("No config file found, using default config")
            return cls()
        with open("config.yaml") as f:
            overwrite_config = yaml.safe_load(f)
            LOG.info(f"Load ./config.yaml")
        overwrite_config = dataclasses.replace(cls(), **overwrite_config)
        LOG.info(f"{overwrite_config}")
        return overwrite_config


# 1. Add logger
LOG = logging.getLogger("memobase_server")
LOG.setLevel(logging.INFO)
console_handler = RichHandler()
LOG.addHandler(console_handler)

# 2. Add encoder for tokenize strings
ENCODER = tiktoken.encoding_for_model("gpt-4o")


# 3. Load config
CONFIG = Config.load_config()
