from typing import *
from pydantic import BaseModel, Field
from .DuplicateSuggestion import DuplicateSuggestion

class SuccessResponse_list_DuplicateSuggestion__(BaseModel):
    """
    SuccessResponse[list[DuplicateSuggestion]] model
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    success : Optional[bool] = Field(validation_alias="success" , default = None )
    
    data : List[DuplicateSuggestion] = Field(validation_alias="data" )
    
    message : Optional[Union[str,None]] = Field(validation_alias="message" , default = None )
    
    request_id : Optional[Union[str,None]] = Field(validation_alias="request_id" , default = None )
    