from typing import Any, Optional

from pydantic import BaseModel


class Response(BaseModel):
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "data": "Sample data",
            }
        }
