from typing import *
from pydantic import BaseModel, Field
from .TaskStatus import TaskStatus
from .AssigneeType import AssigneeType

class TaskUpdate(BaseModel):
    """
    TaskUpdate model
        Fields that can be updated (all optional).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : Optional[Union[str,None]] = Field(validation_alias="title" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    phase : Optional[Union[str,None]] = Field(validation_alias="phase" , default = None )
    
    status : Optional[Union[TaskStatus,None]] = Field(validation_alias="status" , default = None )
    
    priority : Optional[Union[int,None]] = Field(validation_alias="priority" , default = None )
    
    owner_id : Optional[Union[str,None]] = Field(validation_alias="owner_id" , default = None )
    
    assignee_type : Optional[Union[AssigneeType,None]] = Field(validation_alias="assignee_type" , default = None )
    
    project_id : Optional[Union[int,None]] = Field(validation_alias="project_id" , default = None )
    
    labels : Optional[Union[List[str],None]] = Field(validation_alias="labels" , default = None )
    
    estimate : Optional[Union[float,None]] = Field(validation_alias="estimate" , default = None )
    
    parent_id : Optional[Union[int,None]] = Field(validation_alias="parent_id" , default = None )
    
    goal_id : Optional[Union[int,None]] = Field(validation_alias="goal_id" , default = None )
    