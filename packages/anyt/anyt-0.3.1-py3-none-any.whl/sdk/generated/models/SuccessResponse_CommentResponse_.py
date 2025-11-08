from typing import *
from pydantic import BaseModel, Field
from .CommentResponse import CommentResponse

class SuccessResponse_CommentResponse_(BaseModel):
    """
    SuccessResponse[CommentResponse] model
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    success : Optional[bool] = Field(validation_alias="success" , default = None )
    
    data : CommentResponse = Field(validation_alias="data" )
    
    message : Optional[Union[str,None]] = Field(validation_alias="message" , default = None )
    
    request_id : Optional[Union[str,None]] = Field(validation_alias="request_id" , default = None )
    