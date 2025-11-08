from typing import *
from pydantic import BaseModel, Field

class CreateGoalRequest(BaseModel):
    """
    CreateGoalRequest model
        Request model for creating a goal.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : str = Field(validation_alias="title" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    project_id : int = Field(validation_alias="project_id" )
    
    context : Optional[Dict[str, Any]] = Field(validation_alias="context" , default = None )
    