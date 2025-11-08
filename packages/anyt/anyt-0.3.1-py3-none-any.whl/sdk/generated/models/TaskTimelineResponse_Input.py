from typing import *
from pydantic import BaseModel, Field
from .TimelineEventItem_Input import TimelineEventItem_Input

class TaskTimelineResponse_Input(BaseModel):
    """
    TaskTimelineResponse model
        Response for task timeline with all activity.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    items : List[TimelineEventItem_Input] = Field(validation_alias="items" )
    