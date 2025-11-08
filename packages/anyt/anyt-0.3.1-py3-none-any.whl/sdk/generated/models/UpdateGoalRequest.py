from typing import *
from pydantic import BaseModel, Field

class UpdateGoalRequest(BaseModel):
    """
    UpdateGoalRequest model
        Request model for updating a goal.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : Optional[Union[str,None]] = Field(validation_alias="title" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    context : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="context" , default = None )
    
    status : Optional[Union[str,None]] = Field(validation_alias="status" , default = None )
    