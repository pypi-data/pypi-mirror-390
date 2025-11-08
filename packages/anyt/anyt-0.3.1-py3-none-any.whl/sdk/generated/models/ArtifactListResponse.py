from typing import *
from pydantic import BaseModel, Field
from .Artifact import Artifact

class ArtifactListResponse(BaseModel):
    """
    ArtifactListResponse model
        Response for paginated artifact list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[Artifact] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    