from typing import *
from pydantic import BaseModel, Field

class StartAttemptRequest(BaseModel):
    """
    StartAttemptRequest model
        Request for starting a new attempt.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    notes : Optional[Union[str,None]] = Field(validation_alias="notes" , default = None )
    