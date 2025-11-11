"""
Data models for Join Agent operations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import re
import json


class Join(BaseModel):
    left_table: str
    right_table: str
    join_type: str  
    join_fields: List[Tuple[str, str]] = Field(
        ..., description="Pairs of columns used as join keys"
    )


class JoinOutput(BaseModel):
    joins: List[Join]
    unjoinable_tables: List[str]



class OperationEnum(str, Enum):
    golden_dataset = "golden_dataset"
    manual_data_prep = "manual_data_prep"


class JoinInput(BaseModel):
    operation: OperationEnum
    tables: List[str]
    col_metadata: Dict[str, Dict[str, Dict[str, Any]]]
    primary_table: Optional[str] = None
    groupby_fields: Optional[Dict[str, List[str]]] = None
    use_case: Optional[str] = None
    ml_approach: Optional[str] = None
    domain_metadata: Optional[Dict[str, Any]] = None

def clean_json_string(llm_response: str) -> str:
        """
        Cleans an LLM JSON-like string output.

        - Removes markdown code fences (``` or ```json)
        - Strips leading/trailing whitespace
        - Leaves plain JSON untouched
        """
        if not isinstance(llm_response, str):
            return llm_response

        cleaned = llm_response.strip()
        # Only remove if it actually starts with ```
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
        return cleaned

