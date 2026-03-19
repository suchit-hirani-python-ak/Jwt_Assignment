from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TaskRequest(BaseModel):
    name: str
    description: str
    task_status: str = "pending"
    
class TaskResponse(BaseModel):
    id : int
    name: str
    description: str
    task_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class TaskByIdResponse(BaseModel):
    name: str
    task_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class TaskUpdateStatus(TaskRequest):
    model_config = ConfigDict(from_attributes=True)
    
