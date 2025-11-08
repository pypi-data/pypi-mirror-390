from typing import *
from pydantic import BaseModel, Field
from .UserSetupResponse_Output import UserSetupResponse_Output

class SuccessResponse_UserSetupResponse_(BaseModel):
    """
    SuccessResponse[UserSetupResponse] model
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    success : Optional[bool] = Field(validation_alias="success" , default = None )
    
    data : UserSetupResponse_Output = Field(validation_alias="data" )
    
    message : Optional[Union[str,None]] = Field(validation_alias="message" , default = None )
    
    request_id : Optional[Union[str,None]] = Field(validation_alias="request_id" , default = None )
    