from typing import *
from pydantic import BaseModel, Field

class CreateTestInput(BaseModel):
    """
    CreateTestInput model
        Input model for testing Pydantic validation.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    age : int = Field(validation_alias="age" )
    
    email : str = Field(validation_alias="email" )
    