from typing import *
from pydantic import BaseModel, Field
from .Event import Event
from .EventListPagination import EventListPagination

class EventListResponse(BaseModel):
    """
    EventListResponse model
        Response for workspace-wide event list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    events : List[Event] = Field(validation_alias="events" )
    
    pagination : EventListPagination = Field(validation_alias="pagination" )
    