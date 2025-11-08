from typing import *
from pydantic import BaseModel, Field

class Owner(BaseModel):
    """
    Owner model
        Owner/actor information for events.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : str = Field(validation_alias="id" )
    
    type : str = Field(validation_alias="type" )
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    