from typing import *
from pydantic import BaseModel, Field

class CriticalPath(BaseModel):
    """
    CriticalPath model
        Critical path information for task execution.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    tasks : List[str] = Field(validation_alias="tasks" )
    
    total_estimate : float = Field(validation_alias="total_estimate" )
    
    depth : int = Field(validation_alias="depth" )
    
    completion_date : Optional[Union[str,None]] = Field(validation_alias="completion_date" , default = None )
    