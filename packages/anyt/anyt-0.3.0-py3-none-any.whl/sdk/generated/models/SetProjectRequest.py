from typing import *
from pydantic import BaseModel, Field

class SetProjectRequest(BaseModel):
    """
    SetProjectRequest model
        Request to set current project.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    project_id : int = Field(validation_alias="project_id" )
    