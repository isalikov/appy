import asyncio
import time
from enum import StrEnum

import structlog
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from appy_api.api.deps import ProbesDep, SettingsDep
from appy_api.resources import Probe

router = APIRouter(tags=["health"])
log = structlog.get_logger(__name__)


class CheckStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class CheckResult(BaseModel):
    status: CheckStatus
    latency_ms: float = Field(description="Probe round-trip time in milliseconds.")
    error: str | None = None


class HealthResponse(BaseModel):
    status: CheckStatus
    version: str
    checks: dict[str, CheckResult]


async def _run_probe(name: str, probe: Probe, limit_seconds: float) -> CheckResult:
    started = time.perf_counter()
    try:
        async with asyncio.timeout(limit_seconds):
            await probe()
    except Exception as exc:  # noqa: BLE001 - every failure is reported, never raised
        log.warning("health_probe_failed", probe=name, error=repr(exc))
        return CheckResult(
            status=CheckStatus.ERROR,
            latency_ms=(time.perf_counter() - started) * 1000,
            error=type(exc).__name__,
        )
    return CheckResult(status=CheckStatus.OK, latency_ms=(time.perf_counter() - started) * 1000)


@router.get(
    "/health",
    summary="Service health",
    description="Pings every backing service. Returns 503 when any of them is unavailable.",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse}},
)
async def health(probes: ProbesDep, settings: SettingsDep, response: Response) -> HealthResponse:
    names = list(probes)
    results = await asyncio.gather(
        *(_run_probe(name, probes[name], settings.health_timeout_seconds) for name in names)
    )
    checks = dict(zip(names, results, strict=True))
    healthy = all(check.status is CheckStatus.OK for check in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status=CheckStatus.OK if healthy else CheckStatus.ERROR,
        version=settings.version,
        checks=checks,
    )
