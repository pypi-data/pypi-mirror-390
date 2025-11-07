from pydantic import BaseModel, Field
from typing import List
from datetime import time

class ScheduleCollaboratorDTO(BaseModel):
    
    available_schedules: List[time] = Field(default_factory=list)
    busy_schedules: List[time] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            time: lambda v: v.strftime('%H:%M')
        }