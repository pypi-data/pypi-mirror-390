from typing import *
from pydantic import BaseModel, Field

class ExecutionPhase(BaseModel):
    """
    ExecutionPhase model
        Represents a phase in the execution order.

A phase is a group of tasks at the same dependency level that can
potentially run in parallel (depending on the number of runners).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    phase : int = Field(validation_alias="phase" )
    
    tasks : List[str] = Field(validation_alias="tasks" )
    
    parallel : bool = Field(validation_alias="parallel" )
    
    estimated_duration : float = Field(validation_alias="estimated_duration" )
    
    blockers : List[str] = Field(validation_alias="blockers" )
    