from typing import *
from pydantic import BaseModel, Field
from .AgentType import AgentType

class Agent(BaseModel):
    """
    Agent model
        Full agent schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    agent_type : AgentType = Field(validation_alias="agent_type" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    config : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="config" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    agent_id : str = Field(validation_alias="agent_id" )
    
    is_active : bool = Field(validation_alias="is_active" )
    
    created_by : str = Field(validation_alias="created_by" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    
    deleted_at : Optional[Union[str,None]] = Field(validation_alias="deleted_at" , default = None )
    