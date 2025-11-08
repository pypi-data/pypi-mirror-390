from typing import *
from pydantic import BaseModel, Field

class ParallelOpportunity(BaseModel):
    """
    ParallelOpportunity model
        Opportunity for parallel execution within a phase.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    phase : int = Field(validation_alias="phase" )
    
    tasks : List[str] = Field(validation_alias="tasks" )
    
    can_run_together : bool = Field(validation_alias="can_run_together" )
    