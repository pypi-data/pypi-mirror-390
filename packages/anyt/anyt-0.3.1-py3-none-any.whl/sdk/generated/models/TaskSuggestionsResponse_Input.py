from typing import *
from pydantic import BaseModel, Field
from .TaskSuggestion_Input import TaskSuggestion_Input

class TaskSuggestionsResponse_Input(BaseModel):
    """
    TaskSuggestionsResponse model
        Response for task suggestions endpoint.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    suggestions : List[TaskSuggestion_Input] = Field(validation_alias="suggestions" )
    
    total_ready : int = Field(validation_alias="total_ready" )
    
    total_blocked : int = Field(validation_alias="total_blocked" )
    