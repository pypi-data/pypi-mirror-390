from typing import *
from pydantic import BaseModel, Field

class TaskView(BaseModel):
    """
    TaskView model
        Full task view schema.
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
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    user_id : str = Field(validation_alias="user_id" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    