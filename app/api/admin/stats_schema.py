from pydantic import BaseModel, Field
from typing import Optional


class EndpointStats(BaseModel):
    endpoint: str
    request_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    avg_response_time_ms: float = 0.0


class UserStats(BaseModel):
    user_id: str
    user_name: str = ""
    request_count: int = 0
    last_active: Optional[str] = None


class TimeSeriesPoint(BaseModel):
    timestamp: str
    count: int = 0


class DashboardStats(BaseModel):
    total_users: int = 0
    active_api_keys: int = 0
    expired_api_keys: int = 0
    total_requests_24h: int = 0
    total_requests_7d: int = 0
    total_requests_30d: int = 0
    success_rate_24h: float = 0.0
    avg_response_time_ms: float = 0.0
    requests_per_endpoint: list[EndpointStats] = Field(default_factory=list)
    top_users: list[UserStats] = Field(default_factory=list)
    requests_over_time: list[TimeSeriesPoint] = Field(default_factory=list)
    status_code_distribution: dict[str, int] = Field(default_factory=dict)
