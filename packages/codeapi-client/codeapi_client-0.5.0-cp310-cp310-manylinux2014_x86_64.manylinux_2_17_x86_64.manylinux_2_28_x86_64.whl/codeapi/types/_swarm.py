from __future__ import annotations

from typing import Literal

import psutil
from pydantic import BaseModel, Field


class HiveHeartbeat(BaseModel):
    hostname: str
    host: str
    timestamp: float
    status: Literal["alive", "busy", "idle", "dead"]

    cpu_count: int = Field(description="Number of CPU cores")
    cpu_usage: float = Field(description="Current CPU usage percentage")

    memory_total: float = Field(description="Total RAM in GB")
    memory_used: float = Field(description="Used RAM in GB")
    memory_free: float = Field(description="Free RAM in GB")
    memory_usage: float = Field(description="Memory usage percentage")

    disk_total: float = Field(description="Total disk space in GB")
    disk_used: float = Field(description="Used disk space in GB")
    disk_free: float = Field(description="Free disk space in GB")
    disk_usage: float = Field(description="Disk usage percentage")

    load_avg_1min: float | None = Field(
        default=None, description="1-minute load average"
    )
    load_avg_5min: float | None = Field(
        default=None, description="5-minute load average"
    )
    load_avg_15min: float | None = Field(
        default=None, description="15-minute load average"
    )

    @classmethod
    def create(
        cls,
        hostname: str,
        host: str,
        timestamp: float,
        status: Literal["alive", "busy", "idle", "dead"],
    ) -> HiveHeartbeat:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        try:
            load_avg = psutil.getloadavg()
            load_1, load_5, load_15 = load_avg
        except (AttributeError, OSError):
            load_1 = load_5 = load_15 = None

        return cls(
            hostname=hostname,
            host=host,
            timestamp=timestamp,
            status=status,
            cpu_count=psutil.cpu_count(),
            cpu_usage=cpu_usage,
            memory_total=memory.total / (1024**3),
            memory_used=memory.used / (1024**3),
            memory_free=memory.available / (1024**3),
            memory_usage=memory.percent,
            disk_total=disk.total / (1024**3),
            disk_used=disk.used / (1024**3),
            disk_free=disk.free / (1024**3),
            disk_usage=disk.percent,
            load_avg_1min=load_1,
            load_avg_5min=load_5,
            load_avg_15min=load_15,
        )


class SwarmStats(BaseModel):
    total_hives: int = 0
    active_hives: int = 0
    busy_hives: int = 0
    idle_hives: int = 0
    total_cpu_cores: int = 0
    avg_cpu_usage: float = 0.0
    total_memory: float = 0.0
    avg_memory_usage: float = 0.0
