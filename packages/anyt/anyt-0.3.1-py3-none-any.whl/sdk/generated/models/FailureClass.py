from enum import Enum

class FailureClass(str, Enum):
    
        TEST_FAIL = 'test_fail'
        
        TOOL_ERROR = 'tool_error'
        
        CONTEXT_LIMIT = 'context_limit'
        
        RATE_LIMIT = 'rate_limit'
        
        PERMISSION = 'permission'
        
        TIMEOUT = 'timeout'
        
        UNKNOWN = 'unknown'
        