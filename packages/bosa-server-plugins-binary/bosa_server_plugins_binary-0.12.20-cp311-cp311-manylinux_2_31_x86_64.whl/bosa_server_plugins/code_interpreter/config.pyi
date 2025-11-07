from pydantic import BaseModel

class CodeInterpreterConfig(BaseModel):
    """Configuration for Code Interpreter integration.
    
    Attributes:
        user_identifier (str): The user identifier for the integration.
        api_key (str): The API key for authentication with the Code Interpreter service.
    """
    user_identifier: str
    api_key: str
