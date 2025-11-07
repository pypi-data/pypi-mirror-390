from typing import *
from pydantic import BaseModel, Field
from .SummaryPeriod import SummaryPeriod

class SummaryRequest(BaseModel):
    """
    SummaryRequest model
        Request parameters for summary generation.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    period : Optional[SummaryPeriod] = Field(validation_alias="period" , default = None )
    
    include_sections : Optional[List[str]] = Field(validation_alias="include_sections" , default = None )
    