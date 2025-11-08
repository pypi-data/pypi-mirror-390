from typing import *
from pydantic import BaseModel, Field

class CreateArtifactRequest(BaseModel):
    """
    CreateArtifactRequest model
        Request for creating a new artifact.

Note: uri and attempt_id are not included as they are derived from:
- uri: Generated from content (inline storage or future S3/R2)
- attempt_id: Provided as path parameter
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    type : str = Field(validation_alias="type" )
    
    name : str = Field(validation_alias="name" )
    
    content : str = Field(validation_alias="content" )
    
    mime_type : Optional[Union[str,None]] = Field(validation_alias="mime_type" , default = None )
    
    extra_metadata : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="extra_metadata" , default = None )
    