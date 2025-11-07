from typing import *
from pydantic import BaseModel, Field
from .Owner import Owner
from .EventDetails import EventDetails

class TimelineEventItem_Output(BaseModel):
    """
    TimelineEventItem model
        An item in the timeline (event or other activity).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    type : str = Field(validation_alias="type" )
    
    ts : str = Field(validation_alias="ts" )
    
    summary : str = Field(validation_alias="summary" )
    
    owner : Owner = Field(validation_alias="owner" )
    
    details : EventDetails = Field(validation_alias="details" )
    