from typing import *
from pydantic import BaseModel, Field
from .TestItem import TestItem
from .PaginationMeta import PaginationMeta

class PaginatedResponse_TestItem_(BaseModel):
    """
    PaginatedResponse[TestItem] model
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    success : Optional[bool] = Field(validation_alias="success" , default = None )
    
    data : List[TestItem] = Field(validation_alias="data" )
    
    pagination : PaginationMeta = Field(validation_alias="pagination" )
    
    request_id : Optional[Union[str,None]] = Field(validation_alias="request_id" , default = None )
    