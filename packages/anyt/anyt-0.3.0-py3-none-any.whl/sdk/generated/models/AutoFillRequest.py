from typing import *
from pydantic import BaseModel, Field

class AutoFillRequest(BaseModel):
    """
    AutoFillRequest model
        Request parameters for task auto-fill.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    fields : Optional[List[str]] = Field(validation_alias="fields" , default = None )
    