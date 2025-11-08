from typing import *
from pydantic import BaseModel, Field

class PingResponse(BaseModel):
    """
    PingResponse model
        Ping response model.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    message : str = Field(validation_alias="message" )
    
    timestamp : str = Field(validation_alias="timestamp" )
    