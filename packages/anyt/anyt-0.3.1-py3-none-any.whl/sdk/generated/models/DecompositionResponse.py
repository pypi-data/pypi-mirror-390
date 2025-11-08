from typing import *
from pydantic import BaseModel, Field
from .DecomposedTask import DecomposedTask

class DecompositionResponse(BaseModel):
    """
    DecompositionResponse model
        Response from goal decomposition.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    goal_id : int = Field(validation_alias="goal_id" )
    
    tasks : List[DecomposedTask] = Field(validation_alias="tasks" )
    
    dependencies : List[Dict[str, Any]] = Field(validation_alias="dependencies" )
    
    summary : str = Field(validation_alias="summary" )
    
    cost_tokens : Optional[Union[int,None]] = Field(validation_alias="cost_tokens" , default = None )
    
    cache_hit : Optional[bool] = Field(validation_alias="cache_hit" , default = None )
    