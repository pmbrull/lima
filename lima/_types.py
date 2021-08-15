"""
Define pydantic types to use for levy config
"""
from typing import Dict, List

from pydantic import BaseModel


class PromptCfg(BaseModel):
    # pylint: disable=too-few-public-methods

    # Inputs to use to break the prompt execution. E.g. "bye", "quit()"
    end_text: List[str]
    style: Dict[str, str]
    prompt: Dict[str, str]
