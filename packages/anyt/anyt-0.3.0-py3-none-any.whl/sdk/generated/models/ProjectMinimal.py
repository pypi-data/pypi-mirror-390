from typing import *
from pydantic import BaseModel, Field

class ProjectMinimal(BaseModel):
    """
    ProjectMinimal model
        Minimal project info for relationships.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    name : str = Field(validation_alias="name" )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    icon : Optional[Union[str,None]] = Field(validation_alias="icon" , default = None )
    