from typing import *
from pydantic import BaseModel, Field

class SummarySection(BaseModel):
    """
    SummarySection model
        Individual section in summary.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    count : int = Field(validation_alias="count" )
    
    summary : str = Field(validation_alias="summary" )
    
    tasks : List[str] = Field(validation_alias="tasks" )
    
    items : Optional[Union[List[str],None]] = Field(validation_alias="items" , default = None )
    