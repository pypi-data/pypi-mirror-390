from typing import *
from pydantic import BaseModel, Field

class AttemptMetadata(BaseModel):
    """
    AttemptMetadata model
        Typed metadata for AI agent attempts.

Provides type-safe fields for common AI agent execution metadata
while allowing additional custom fields via extra=&#39;allow&#39;.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    model_used : Optional[Union[str,None]] = Field(validation_alias="model_used" , default = None )
    
    temperature : Optional[Union[float,None]] = Field(validation_alias="temperature" , default = None )
    
    context_length : Optional[Union[int,None]] = Field(validation_alias="context_length" , default = None )
    
    max_tokens : Optional[Union[int,None]] = Field(validation_alias="max_tokens" , default = None )
    
    execution_environment : Optional[Union[str,None]] = Field(validation_alias="execution_environment" , default = None )
    
    agent_version : Optional[Union[str,None]] = Field(validation_alias="agent_version" , default = None )
    
    input_tokens : Optional[Union[int,None]] = Field(validation_alias="input_tokens" , default = None )
    
    output_tokens : Optional[Union[int,None]] = Field(validation_alias="output_tokens" , default = None )
    
    cache_read_tokens : Optional[Union[int,None]] = Field(validation_alias="cache_read_tokens" , default = None )
    
    cache_creation_tokens : Optional[Union[int,None]] = Field(validation_alias="cache_creation_tokens" , default = None )
    
    notes : Optional[Union[str,None]] = Field(validation_alias="notes" , default = None )
    