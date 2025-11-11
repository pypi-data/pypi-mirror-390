# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["HealthCheckAppResponse"]


class HealthCheckAppResponse(BaseModel):
    status: str

    backend_git_hash: Optional[str] = None

    frontend_docker_version: Optional[str] = None
