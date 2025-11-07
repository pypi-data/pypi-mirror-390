from typing import *
from pydantic import BaseModel, Field

class PaginationMeta(BaseModel):
    """
    PaginationMeta model
        Pagination metadata.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    total : int = Field(validation_alias="total" )
    
    page : int = Field(validation_alias="page" )
    
    per_page : int = Field(validation_alias="per_page" )
    
    total_pages : int = Field(validation_alias="total_pages" )
    
    has_next : bool = Field(validation_alias="has_next" )
    
    has_prev : bool = Field(validation_alias="has_prev" )
    