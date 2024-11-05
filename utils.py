import logging
import logging.handlers
import sys
import os
from enum import IntEnum
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
import dataclasses
import json

@dataclasses.dataclass
class WorkerInfo:
    model_names: List[str]
    speed: int
    queue_length: int
    check_heart_beat: bool
    last_heart_beat: str
    extend_info: dict

    def to_str(self):
        return json.dumps(dataclasses.asdict(self))
    
    @classmethod
    def from_str(cls, s):
        data = json.loads(s)
        return cls(**data)
    
def pretty_print_semaphore(semaphore):
    """Print a semaphore in better format."""
    if semaphore is None:
        return "None"
    return f"Semaphore(value={semaphore._value}, locked={semaphore.locked()})"

def build_logger(logger_name, logger_filename, logger_dir):
    global handler
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.basicConfig(level=logging.INFO, encoding="utf-8")
    logging.getLogger().handlers[0].setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    filename = os.path.join(logger_dir, logger_filename)
    handler = logging.handlers.TimedRotatingFileHandler(
        filename, when="D", utc=True, encoding="utf-8"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

SEQUENCE_LENGTH_KEYS = [
    "max_sequence_length",
    "seq_length",
    "max_position_embeddings",
    "max_seq_len",
    "model_max_length",
]

def get_context_length(config):
    """Get the context length of a model from a huggingface model config."""
    rope_scaling = getattr(config, "rope_scaling", None)
    if rope_scaling:
        rope_scaling_factor = config.rope_scaling["factor"]
    else:
        rope_scaling_factor = 1

    for key in SEQUENCE_LENGTH_KEYS:
        val = getattr(config, key, None)
        if val is not None:
            return int(rope_scaling_factor * val)
    return 2048

