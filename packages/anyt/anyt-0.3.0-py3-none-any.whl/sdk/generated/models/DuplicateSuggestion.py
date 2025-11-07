from typing import *
from pydantic import BaseModel, Field

class DuplicateSuggestion(BaseModel):
    """
    DuplicateSuggestion model
        Duplicate task detection result.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    tasks : List[str] = Field(validation_alias="tasks" )
    
    similarity : float = Field(validation_alias="similarity" )
    
    suggestion : str = Field(validation_alias="suggestion" )
    