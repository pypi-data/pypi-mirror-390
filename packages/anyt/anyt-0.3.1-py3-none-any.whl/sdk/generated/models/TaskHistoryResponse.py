from typing import *
from pydantic import BaseModel, Field
from .Event import Event
from .EventListPagination import EventListPagination

class TaskHistoryResponse(BaseModel):
    """
    TaskHistoryResponse model
        Response for task history with events.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    events : List[Event] = Field(validation_alias="events" )
    
    total : int = Field(validation_alias="total" )
    
    pagination : EventListPagination = Field(validation_alias="pagination" )
    