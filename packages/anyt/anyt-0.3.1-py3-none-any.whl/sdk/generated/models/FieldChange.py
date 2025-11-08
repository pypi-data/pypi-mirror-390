from typing import *
from pydantic import BaseModel, Field

class FieldChange(BaseModel):
    """
    FieldChange model
        Represents a field change in an event.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    field : str = Field(validation_alias="field" )
    
    old_value : Any = Field(validation_alias="old_value" )
    
    new_value : Any = Field(validation_alias="new_value" )
    