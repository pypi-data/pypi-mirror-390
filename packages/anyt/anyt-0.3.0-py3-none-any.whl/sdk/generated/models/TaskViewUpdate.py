from typing import *
from pydantic import BaseModel, Field

class TaskViewUpdate(BaseModel):
    """
    TaskViewUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    filters : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="filters" , default = None )
    
    is_default : Optional[Union[bool,None]] = Field(validation_alias="is_default" , default = None )
    
    display_order : Optional[Union[int,None]] = Field(validation_alias="display_order" , default = None )
    