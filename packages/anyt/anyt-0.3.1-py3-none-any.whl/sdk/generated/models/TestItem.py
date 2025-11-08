from typing import *
from pydantic import BaseModel, Field

class TestItem(BaseModel):
    """
    TestItem model
        Test item model.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    name : str = Field(validation_alias="name" )
    
    version : Optional[int] = Field(validation_alias="version" , default = None )
    