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


class ProjectStatus:
    active = "active"
    suspended = "suspended"


USAGE_TOKEN_LIMIT_MAP = {
    ProjectStatus.active: int(os.getenv("USAGE_TOKEN_LIMIT_ACTIVE", -1)),
}


class ContanstTable:
    topic = "topic"
    sub_topic = "sub_topic"
    update_hits = "update_hits"


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
        if overwrite_config is None:
            return cls()
        fields = {field.name for field in dataclasses.fields(cls)}
        # Filter out any keys from overwrite_config that aren't in the dataclass
        filtered_config = {k: v for k, v in overwrite_config.items() if k in fields}
        overwrite_config = dataclasses.replace(cls(), **filtered_config)
        LOG.info(f"{overwrite_config}")
        return overwrite_config


@dataclass
class ProfileConfig:
    language: Literal["en", "zh"] = None
    additional_user_profiles: list[dict] = field(default_factory=list)
    overwrite_user_profiles: Optional[list[dict]] = None

    def __post_init__(self):
        if self.language not in ["en", "zh"]:
            self.language = None

    @classmethod
    def load_config_string(cls, config_string: str) -> "Config":
        overwrite_config = yaml.safe_load(config_string)
        if overwrite_config is None:
            return cls()
        # Get all field names from the dataclass
        fields = {field.name for field in dataclasses.fields(cls)}
        # Filter out any keys from overwrite_config that aren't in the dataclass
        filtered_config = {k: v for k, v in overwrite_config.items() if k in fields}
        overwrite_config = dataclasses.replace(cls(), **filtered_config)
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
