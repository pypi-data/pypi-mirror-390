from typing import *
from pydantic import BaseModel, Field

class SetWorkspaceRequest(BaseModel):
    """
    SetWorkspaceRequest model
        Request to set current workspace.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    