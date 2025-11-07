from enum import Enum

class AttemptStatus(str, Enum):
    
        RUNNING = 'running'
        
        SUCCESS = 'success'
        
        FAILED = 'failed'
        
        ABORTED = 'aborted'
        