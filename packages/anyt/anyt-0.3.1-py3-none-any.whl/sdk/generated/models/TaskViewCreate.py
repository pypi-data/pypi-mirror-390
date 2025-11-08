from typing import *
from pydantic import BaseModel, Field

class TaskViewCreate(BaseModel):
    """
    TaskViewCreate model
        Data required to create a task view.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    filters : Optional[Dict[str, Any]] = Field(validation_alias="filters" , default = None )
    
    is_default : Optional[bool] = Field(validation_alias="is_default" , default = None )
    
    display_order : Optional[int] = Field(validation_alias="display_order" , default = None )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    user_id : str = Field(validation_alias="user_id" )
    