from typing import *
from pydantic import BaseModel, Field

class DecomposedTask(BaseModel):
    """
    DecomposedTask model
        Individual task from decomposition.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : str = Field(validation_alias="title" )
    
    description : str = Field(validation_alias="description" )
    
    priority : Optional[int] = Field(validation_alias="priority" , default = None )
    
    labels : Optional[List[str]] = Field(validation_alias="labels" , default = None )
    
    acceptance : str = Field(validation_alias="acceptance" )
    
    estimated_hours : float = Field(validation_alias="estimated_hours" )
    