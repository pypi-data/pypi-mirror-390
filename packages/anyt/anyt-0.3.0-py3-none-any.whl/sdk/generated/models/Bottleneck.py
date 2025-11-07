from typing import *
from pydantic import BaseModel, Field

class Bottleneck(BaseModel):
    """
    Bottleneck model
        Task that blocks many other tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task : str = Field(validation_alias="task" )
    
    blocks_count : int = Field(validation_alias="blocks_count" )
    
    downstream_estimate : float = Field(validation_alias="downstream_estimate" )
    