from typing import *
from pydantic import BaseModel, Field
from .AttemptResponse import AttemptResponse

class AttemptListResponse_Output(BaseModel):
    """
    AttemptListResponse model
        Response for paginated attempt list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[AttemptResponse] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    