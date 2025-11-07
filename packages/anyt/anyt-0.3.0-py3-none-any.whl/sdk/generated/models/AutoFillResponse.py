from typing import *
from pydantic import BaseModel, Field

class AutoFillResponse(BaseModel):
    """
    AutoFillResponse model
        Response from task auto-fill.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    filled_fields : Dict[str, Any] = Field(validation_alias="filled_fields" )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    