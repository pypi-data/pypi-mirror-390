from typing import *
from pydantic import BaseModel, Field
from .AttemptStatus import AttemptStatus
from .FailureClass import FailureClass
from .AttemptMetadata import AttemptMetadata

class AttemptUpdate(BaseModel):
    """
    AttemptUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    status : Optional[Union[AttemptStatus,None]] = Field(validation_alias="status" , default = None )
    
    failure_class : Optional[Union[FailureClass,None]] = Field(validation_alias="failure_class" , default = None )
    
    failure_message : Optional[Union[str,None]] = Field(validation_alias="failure_message" , default = None )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    
    wall_clock_ms : Optional[Union[int,None]] = Field(validation_alias="wall_clock_ms" , default = None )
    
    extra_metadata : Optional[Union[AttemptMetadata,None]] = Field(validation_alias="extra_metadata" , default = None )
    
    ended_at : Optional[Union[str,None]] = Field(validation_alias="ended_at" , default = None )
    