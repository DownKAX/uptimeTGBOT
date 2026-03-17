from typing import Any
from pydantic import BaseModel

class ColumnValue(BaseModel):
    column_name: str
    column_value: Any