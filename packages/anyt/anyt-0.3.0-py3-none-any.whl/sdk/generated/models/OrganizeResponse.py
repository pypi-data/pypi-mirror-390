from typing import *
from pydantic import BaseModel, Field
from .OrganizationChange import OrganizationChange
from .DuplicateSuggestion import DuplicateSuggestion

class OrganizeResponse(BaseModel):
    """
    OrganizeResponse model
        Response from workspace organization.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    changes : List[OrganizationChange] = Field(validation_alias="changes" )
    
    duplicates : List[DuplicateSuggestion] = Field(validation_alias="duplicates" )
    
    dry_run : bool = Field(validation_alias="dry_run" )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    