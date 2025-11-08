from typing import *
from pydantic import BaseModel, Field
from .AgentType import AgentType

class AgentUpdate(BaseModel):
    """
    AgentUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    
    agent_type : Optional[Union[AgentType,None]] = Field(validation_alias="agent_type" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    config : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="config" , default = None )
    
    is_active : Optional[Union[bool,None]] = Field(validation_alias="is_active" , default = None )
    