from typing import *
from pydantic import BaseModel, Field

class SuccessResponse_dict_str__Any__(BaseModel):
    """
    SuccessResponse[dict[str, Any]] model
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    success : Optional[bool] = Field(validation_alias="success" , default = None )
    
    data : Dict[str, Any] = Field(validation_alias="data" )
    
    message : Optional[Union[str,None]] = Field(validation_alias="message" , default = None )
    
    request_id : Optional[Union[str,None]] = Field(validation_alias="request_id" , default = None )
    