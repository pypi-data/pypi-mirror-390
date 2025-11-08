from typing import *
from pydantic import BaseModel, Field

class UserPreferencesResponse(BaseModel):
    """
    UserPreferencesResponse model
        User preferences response.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    user_id : str = Field(validation_alias="user_id" )
    
    current_workspace_id : Union[int,None] = Field(validation_alias="current_workspace_id" )
    
    current_project_id : Union[int,None] = Field(validation_alias="current_project_id" )
    