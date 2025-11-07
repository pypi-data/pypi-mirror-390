from typing import *
from pydantic import BaseModel, Field
from .AgentType import AgentType

class CreateAgentRequest(BaseModel):
    """
    CreateAgentRequest model
        Request for creating a new agent.

Note: workspace_id and created_by are not included as they are derived from:
- workspace_id: Provided as path parameter
- created_by: Extracted from authentication (actor)
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    agent_type : AgentType = Field(validation_alias="agent_type" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    config : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="config" , default = None )
    
    agent_id : Optional[Union[str,None]] = Field(validation_alias="agent_id" , default = None )
    