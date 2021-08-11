"""
Define pydantic types to use for levy config
"""
from typing import List, Dict

from pydantic import BaseModel


class PromptCfg(BaseModel):

    # Inputs to use to break the prompt execution. E.g. "bye", "quit()"
    end_text: List[str]
    style: Dict[str, str]
