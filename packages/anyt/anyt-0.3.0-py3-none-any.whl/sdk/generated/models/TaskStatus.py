from enum import Enum

class TaskStatus(str, Enum):
    
        BACKLOG = 'backlog'
        
        TODO = 'todo'
        
        INPROGRESS = 'inprogress'
        
        BLOCKED = 'blocked'
        
        CANCELED = 'canceled'
        
        DONE = 'done'
        
        ARCHIVED = 'archived'
        