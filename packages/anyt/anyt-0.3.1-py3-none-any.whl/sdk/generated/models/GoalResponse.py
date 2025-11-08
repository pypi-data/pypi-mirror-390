from typing import *
from pydantic import BaseModel, Field

class GoalResponse(BaseModel):
    """
    GoalResponse model
        Response model for goal.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    project_id : int = Field(validation_alias="project_id" )
    
    number : int = Field(validation_alias="number" )
    
    identifier : str = Field(validation_alias="identifier" )
    
    title : str = Field(validation_alias="title" )
    
    description : Union[str,None] = Field(validation_alias="description" )
    
    context : Dict[str, Any] = Field(validation_alias="context" )
    
    status : str = Field(validation_alias="status" )
    
    creator_id : str = Field(validation_alias="creator_id" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    