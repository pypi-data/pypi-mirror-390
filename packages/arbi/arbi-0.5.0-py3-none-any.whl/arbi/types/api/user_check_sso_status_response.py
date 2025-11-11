# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["UserCheckSSOStatusResponse"]


class UserCheckSSOStatusResponse(BaseModel):
    email: str

    status: str

    last_name: Optional[str] = None

    name: Optional[str] = None
