from typing import *
from pydantic import BaseModel, Field

class OrganizeRequest(BaseModel):
    """
    OrganizeRequest model
        Request parameters for workspace organization.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    actions : Optional[List[str]] = Field(validation_alias="actions" , default = None )
    
    dry_run : Optional[bool] = Field(validation_alias="dry_run" , default = None )
    