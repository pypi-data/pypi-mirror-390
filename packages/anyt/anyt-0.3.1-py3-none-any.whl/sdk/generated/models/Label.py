from typing import *
from pydantic import BaseModel, Field

class Label(BaseModel):
    """
    Label model
        Full label schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : Optional[Union[str,None]] = Field(validation_alias="updated_at" , default = None )
    