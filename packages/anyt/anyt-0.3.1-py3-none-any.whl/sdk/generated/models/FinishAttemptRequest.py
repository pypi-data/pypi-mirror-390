from typing import *
from pydantic import BaseModel, Field
from .AttemptMetadata import AttemptMetadata

class FinishAttemptRequest(BaseModel):
    """
    FinishAttemptRequest model
        Request for finishing an attempt.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    status : str = Field(validation_alias="status" )
    
    failure_class : Optional[Union[str,None]] = Field(validation_alias="failure_class" , default = None )
    
    failure_message : Optional[Union[str,None]] = Field(validation_alias="failure_message" , default = None )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    
    wall_clock_ms : Optional[Union[int,None]] = Field(validation_alias="wall_clock_ms" , default = None )
    
    notes : Optional[Union[str,None]] = Field(validation_alias="notes" , default = None )
    
    extra_metadata : Optional[Union[AttemptMetadata,None]] = Field(validation_alias="extra_metadata" , default = None )
    