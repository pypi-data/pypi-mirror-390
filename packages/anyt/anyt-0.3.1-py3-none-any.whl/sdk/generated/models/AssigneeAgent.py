from typing import *
from pydantic import BaseModel, Field

class AssigneeAgent(BaseModel):
    """
    AssigneeAgent model
        Agent assignee for tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : str = Field(validation_alias="id" )
    
    name : str = Field(validation_alias="name" )
    
    type : Optional[str] = Field(validation_alias="type" , default = None )
    
    agent_type : str = Field(validation_alias="agent_type" )
    