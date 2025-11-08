"""InsSubs resource module."""

from .client import InsSubsClient
from .models import (
    InsSub,
    CreateInsSubRequest,
    UpdateInsSubRequest,
    InsSubListResponse
)
from .types import AuthorizationType

__all__ = [
    "InsSubsClient",
    "InsSub",
    "CreateInsSubRequest",
    "UpdateInsSubRequest",
    "InsSubListResponse",
    "AuthorizationType",
]

