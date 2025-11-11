# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentViewParams"]


class DocumentViewParams(TypedDict, total=False):
    page: Optional[int]
    """Optional page to open on load"""

    workspace_key: Annotated[str, PropertyInfo(alias="workspace-key")]
