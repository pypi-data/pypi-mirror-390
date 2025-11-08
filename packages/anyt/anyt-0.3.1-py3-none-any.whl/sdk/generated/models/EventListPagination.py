from typing import *
from pydantic import BaseModel, Field

class EventListPagination(BaseModel):
    """
    EventListPagination model
        Pagination metadata for event lists.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    total : int = Field(validation_alias="total" )
    
    limit : int = Field(validation_alias="limit" )
    
    offset : int = Field(validation_alias="offset" )
    
    has_more : bool = Field(validation_alias="has_more" )
    