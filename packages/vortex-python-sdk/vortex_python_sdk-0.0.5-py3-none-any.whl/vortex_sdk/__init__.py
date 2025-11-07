"""
Vortex Python SDK

A Python SDK for Vortex invitation management and JWT generation.
"""

from .types import (
    AcceptInvitationsRequest,
    ApiResponse,
    AuthenticatedUser,
    CreateInvitationRequest,
    GroupInput,
    IdentifierInput,
    Invitation,
    InvitationTarget,
    JwtPayload,
    VortexApiError,
)
from .vortex import Vortex

__version__ = "0.0.5"
__author__ = "TeamVortexSoftware"
__email__ = "support@vortexsoftware.com"

__all__ = [
    "Vortex",
    "AuthenticatedUser",
    "JwtPayload",
    "IdentifierInput",
    "GroupInput",
    "InvitationTarget",
    "Invitation",
    "CreateInvitationRequest",
    "AcceptInvitationsRequest",
    "ApiResponse",
    "VortexApiError",
]
