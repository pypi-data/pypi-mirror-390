from typing import *
from pydantic import BaseModel, Field
from .FieldChange import FieldChange

class EventDetails(BaseModel):
    """
    EventDetails model
        Detailed event information.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    event_id : int = Field(validation_alias="event_id" )
    
    kind : str = Field(validation_alias="kind" )
    
    field_changes : Optional[Union[List[FieldChange],None]] = Field(validation_alias="field_changes" , default = None )
    