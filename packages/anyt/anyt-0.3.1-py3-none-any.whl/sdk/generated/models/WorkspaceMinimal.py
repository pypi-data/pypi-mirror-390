from typing import *
from pydantic import BaseModel, Field

class WorkspaceMinimal(BaseModel):
    """
    WorkspaceMinimal model
        Minimal workspace info for relationships.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    name : str = Field(validation_alias="name" )
    
    identifier : str = Field(validation_alias="identifier" )
    