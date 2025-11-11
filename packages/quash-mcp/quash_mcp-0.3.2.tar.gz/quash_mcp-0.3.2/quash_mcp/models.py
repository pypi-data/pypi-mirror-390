from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TokensInfo(BaseModel):
    prompt: int
    completion: int
    total: int

class ConfigInfo(BaseModel):
    model: str
    temperature: float
    vision: bool = False
    reasoning: bool = False
    reflection: bool = False
    debug: bool = False

class UIStateInfo(BaseModel):
    a11y_tree: List[Dict[str, Any]]
    phone_state: Dict[str, Any]

class ChatHistoryMessage(BaseModel):
    role: str
    content: str

class AgentStepDTO(BaseModel):
    step_number: int
    reasoning: Optional[str] = None
    code: Optional[str] = None
    tokens_used: TokensInfo
    cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ReflectionInfo(BaseModel):
    """Information about a reflection step."""
    goal_achieved: bool
    advice: Optional[str] = None
    summary: Optional[str] = None

class SessionDTO(BaseModel):
    session_id: str
    api_key: str
    task: str
    device_serial: str
    config: ConfigInfo
    chat_history: List[ChatHistoryMessage] = []
    steps: List[AgentStepDTO] = []
    current_plan: Optional[List[str]] = None
    current_task_index: int = 0
    ui_state: Optional[UIStateInfo] = None
    last_reflection: Optional[ReflectionInfo] = None # Store the last reflection for the session

    last_action_completed: Optional[bool] = None
