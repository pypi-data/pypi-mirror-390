from typing import *
from pydantic import BaseModel, Field

class Event(BaseModel):
    """
    Event model
        Full event schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    actor_id : str = Field(validation_alias="actor_id" )
    
    actor_type : str = Field(validation_alias="actor_type" )
    
    entity_type : str = Field(validation_alias="entity_type" )
    
    entity_id : str = Field(validation_alias="entity_id" )
    
    event_type : str = Field(validation_alias="event_type" )
    
    changes : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="changes" , default = None )
    
    extra_metadata : Optional[Dict[str, Any]] = Field(validation_alias="extra_metadata" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    ts : str = Field(validation_alias="ts" )
    
    created_at : str = Field(validation_alias="created_at" )
    