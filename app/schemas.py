from pydantic import BaseModel
from typing import Dict, List, Optional


class HealthResponse(BaseModel):
    status: str
    service: str


class ScheduleItem(BaseModel):
    task_id: str
    asset_id: str
    task_name: str
    technician_id: str
    start: int
    end: int
    priority: int


class Diagnostics(BaseModel):
    num_tasks: int
    num_technicians: int
    num_decision_variables: int
    time_limit_seconds: int
    scheduled_tasks: Optional[int] = None
    technician_workload_hours: Optional[Dict[str, int]] = None
    scenario_name: Optional[str] = None
    scenario_description: Optional[str] = None


class OptimizationResponse(BaseModel):
    status: str
    objective_value: Optional[float] = None
    runtime_seconds: float
    schedule: List[ScheduleItem]
    diagnostics: Diagnostics
    errors: Optional[List[str]] = None