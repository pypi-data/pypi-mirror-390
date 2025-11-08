from typing import *
from pydantic import BaseModel, Field

class LabelUpdate(BaseModel):
    """
    LabelUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    