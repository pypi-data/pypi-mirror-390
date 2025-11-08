from typing import *
from pydantic import BaseModel, Field

class Artifact(BaseModel):
    """
    Artifact model
        Full artifact schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    type : str = Field(validation_alias="type" )
    
    name : str = Field(validation_alias="name" )
    
    uri : str = Field(validation_alias="uri" )
    
    size_bytes : Optional[Union[int,None]] = Field(validation_alias="size_bytes" , default = None )
    
    mime_type : Optional[Union[str,None]] = Field(validation_alias="mime_type" , default = None )
    
    preview : Optional[Union[str,None]] = Field(validation_alias="preview" , default = None )
    
    extra_metadata : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="extra_metadata" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    attempt_id : int = Field(validation_alias="attempt_id" )
    
    created_at : str = Field(validation_alias="created_at" )
    