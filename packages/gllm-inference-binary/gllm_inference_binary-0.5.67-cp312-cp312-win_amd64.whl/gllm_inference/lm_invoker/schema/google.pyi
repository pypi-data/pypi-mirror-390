class Key:
    """Defines valid keys in Google."""
    ARGS: str
    CONTENT: str
    FINISH_MESSAGE: str
    FINISH_REASON: str
    FUNCTION: str
    FUNCTION_CALL: str
    HTTP_OPTIONS: str
    ID: str
    NAME: str
    RETRY_OPTIONS: str
    STATUS: str
    SYSTEM_INSTRUCTION: str
    THINKING_CONFIG: str
    TIMEOUT: str
    TOOLS: str
    RESPONSE_SCHEMA: str
    RESPONSE_MIME_TYPE: str
    VERTEXAI: str
    CUSTOM_REQUEST_IDS: str

class InputType:
    """Defines valid input types in Google."""
    APPLICATION_JSON: str
    MODEL: str
    USER: str

class JobState:
    """Defines valid output types in Google."""
    JOB_STATE_CANCELLED: str
    JOB_STATE_EXPIRED: str
    JOB_STATE_FAILED: str
    JOB_STATE_PENDING: str
    JOB_STATE_RUNNING: str
    JOB_STATE_SUCCEEDED: str
