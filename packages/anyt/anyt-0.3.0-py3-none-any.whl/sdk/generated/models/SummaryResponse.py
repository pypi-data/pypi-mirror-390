from typing import *
from pydantic import BaseModel, Field
from .SummaryPeriod import SummaryPeriod

class SummaryResponse(BaseModel):
    """
    SummaryResponse model
        Response from summary generation.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    period : SummaryPeriod = Field(validation_alias="period" )
    
    snapshot_ts : str = Field(validation_alias="snapshot_ts" )
    
    sections : Dict[str, Any] = Field(validation_alias="sections" )
    
    text : str = Field(validation_alias="text" )
    
    author : str = Field(validation_alias="author" )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    