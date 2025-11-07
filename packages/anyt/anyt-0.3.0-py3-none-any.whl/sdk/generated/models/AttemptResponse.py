from typing import *
from pydantic import BaseModel, Field
from .AttemptMetadata import AttemptMetadata

class AttemptResponse(BaseModel):
    """
    AttemptResponse model
        Enhanced attempt response with task identifier and artifact count.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    task_id : int = Field(validation_alias="task_id" )
    
    task_identifier : Optional[Union[str,None]] = Field(validation_alias="task_identifier" , default = None )
    
    actor_id : str = Field(validation_alias="actor_id" )
    
    actor_type : str = Field(validation_alias="actor_type" )
    
    started_at : str = Field(validation_alias="started_at" )
    
    ended_at : Optional[Union[str,None]] = Field(validation_alias="ended_at" , default = None )
    
    status : Optional[Union[str,None]] = Field(validation_alias="status" , default = None )
    
    failure_class : Optional[Union[str,None]] = Field(validation_alias="failure_class" , default = None )
    
    failure_message : Optional[Union[str,None]] = Field(validation_alias="failure_message" , default = None )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    
    wall_clock_ms : Optional[Union[int,None]] = Field(validation_alias="wall_clock_ms" , default = None )
    
    extra_metadata : Optional[Union[AttemptMetadata,None]] = Field(validation_alias="extra_metadata" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    artifacts_count : Optional[Union[int,None]] = Field(validation_alias="artifacts_count" , default = None )
    