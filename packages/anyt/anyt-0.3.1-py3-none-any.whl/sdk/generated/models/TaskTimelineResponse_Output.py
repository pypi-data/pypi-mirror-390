from typing import *
from pydantic import BaseModel, Field
from .TimelineEventItem_Output import TimelineEventItem_Output

class TaskTimelineResponse_Output(BaseModel):
    """
    TaskTimelineResponse model
        Response for task timeline with all activity.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    items : List[TimelineEventItem_Output] = Field(validation_alias="items" )
    