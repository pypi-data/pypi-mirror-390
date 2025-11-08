from typing import *
from pydantic import BaseModel, Field

class OrganizationChange(BaseModel):
    """
    OrganizationChange model
        Individual change suggested by organizer.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    field : str = Field(validation_alias="field" )
    
    before : Union[Dict[str, Any],List[Any],str] = Field(validation_alias="before" )
    
    after : Union[Dict[str, Any],List[Any],str] = Field(validation_alias="after" )
    
    reason : str = Field(validation_alias="reason" )
    