from typing import *
from pydantic import BaseModel, Field
from .Project import Project

class ProjectListResponse_Output(BaseModel):
    """
    ProjectListResponse model
        Response for paginated project list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[Project] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    