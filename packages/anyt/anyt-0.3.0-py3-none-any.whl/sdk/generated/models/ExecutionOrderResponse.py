from typing import *
from pydantic import BaseModel, Field
from .CriticalPath import CriticalPath
from .ExecutionPhase import ExecutionPhase
from .Bottleneck import Bottleneck
from .ParallelOpportunity import ParallelOpportunity

class ExecutionOrderResponse(BaseModel):
    """
    ExecutionOrderResponse model
        Response schema for execution order endpoint.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    critical_path : CriticalPath = Field(validation_alias="critical_path" )
    
    execution_phases : List[ExecutionPhase] = Field(validation_alias="execution_phases" )
    
    bottlenecks : List[Bottleneck] = Field(validation_alias="bottlenecks" )
    
    parallel_opportunities : List[ParallelOpportunity] = Field(validation_alias="parallel_opportunities" )
    
    total_estimate : float = Field(validation_alias="total_estimate" )
    
    estimated_completion_date : Optional[Union[str,None]] = Field(validation_alias="estimated_completion_date" , default = None )
    
    num_runners : int = Field(validation_alias="num_runners" )
    