from enum import Enum

class AgentType(str, Enum):
    
        ASSISTANT = 'assistant'
        
        CODE_REVIEWER = 'code_reviewer'
        
        QA_BOT = 'qa_bot'
        
        CUSTOM = 'custom'
        