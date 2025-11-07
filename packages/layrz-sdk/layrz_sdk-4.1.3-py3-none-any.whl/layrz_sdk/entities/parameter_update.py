from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ParameterUpdate(BaseModel):
  asset_id: int = Field(..., description='The unique identifier for the asset.')
  parameter: str = Field(..., description='The name of the parameter.')
  updated_at: datetime = Field(..., description='The timestamp when the parameter was updated.')
  current_value: Any | None = Field(default=None, description='The current value of the parameter.')

  @field_validator('parameter', mode='before')
  def validate_parameter(cls, value: str) -> str:
    return value.replace('__', '.')
