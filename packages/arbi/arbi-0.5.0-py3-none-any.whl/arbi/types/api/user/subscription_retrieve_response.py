# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["SubscriptionRetrieveResponse"]


class SubscriptionRetrieveResponse(BaseModel):
    status: str

    amount: Optional[int] = None

    budget_reset_at: Optional[int] = None

    cancel_at_period_end: Optional[bool] = None

    currency: Optional[str] = None

    current_period_end: Optional[int] = None

    days_remaining: Optional[int] = None

    max_budget: Optional[float] = None

    plan: Optional[str] = None

    portal_url: Optional[str] = None

    price_id: Optional[str] = None

    spend: Optional[float] = None

    storage_quota_mb: Optional[int] = None

    total_files_mb: Optional[float] = None

    trial_expires: Optional[int] = None
