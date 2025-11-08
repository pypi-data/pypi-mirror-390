from typing import *
from pydantic import BaseModel, Field
from .AssigneeUser import AssigneeUser
from .AssigneeAgent import AssigneeAgent

class AssigneesData(BaseModel):
    """
    AssigneesData model
        Data structure for assignees with separate users and agents arrays.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    users : Optional[List[Optional[AssigneeUser]]] = Field(validation_alias="users" , default = None )
    
    agents : Optional[List[Optional[AssigneeAgent]]] = Field(validation_alias="agents" , default = None )
    