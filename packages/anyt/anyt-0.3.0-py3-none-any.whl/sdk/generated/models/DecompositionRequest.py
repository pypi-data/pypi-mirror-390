from typing import *
from pydantic import BaseModel, Field

class DecompositionRequest(BaseModel):
    """
    DecompositionRequest model
        Request parameters for goal decomposition.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    max_tasks : Optional[int] = Field(validation_alias="max_tasks" , default = None )
    
    max_depth : Optional[int] = Field(validation_alias="max_depth" , default = None )
    
    task_size_hours : Optional[int] = Field(validation_alias="task_size_hours" , default = None )
    
    dry_run : Optional[bool] = Field(validation_alias="dry_run" , default = None )
    