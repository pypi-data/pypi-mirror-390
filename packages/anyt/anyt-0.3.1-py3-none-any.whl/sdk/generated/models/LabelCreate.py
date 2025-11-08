from typing import *
from pydantic import BaseModel, Field

class LabelCreate(BaseModel):
    """
    LabelCreate model
        Data required to create a label.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    