from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class IdentifierInput(BaseModel):
    """Identifier structure for JWT generation"""

    type: Literal["email", "sms"]
    value: str


class GroupInput(BaseModel):
    """Group structure for JWT generation (input)"""

    type: str
    id: Optional[str] = None  # Legacy field (deprecated, use groupId)
    groupId: Optional[str] = Field(
        None, alias="group_id", serialization_alias="groupId"
    )  # Preferred: Customer's group ID
    name: str

    class Config:
        populate_by_name = True


class InvitationGroup(BaseModel):
    """
    Invitation group from API responses
    This matches the MemberGroups table structure from the API
    """

    id: str  # Vortex internal UUID
    account_id: str = Field(alias="accountId")  # Vortex account ID
    group_id: str = Field(alias="groupId")  # Customer's group ID
    type: str  # Group type (e.g., "workspace", "team")
    name: str  # Group name
    created_at: str = Field(alias="createdAt")  # ISO 8601 timestamp

    class Config:
        # Allow both snake_case (Python) and camelCase (JSON) field names
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "accountId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                "groupId": "workspace-123",
                "type": "workspace",
                "name": "My Workspace",
                "createdAt": "2025-01-27T12:00:00.000Z",
            }
        }


class AuthenticatedUser(BaseModel):
    user_id: str
    identifiers: List[IdentifierInput]
    groups: Optional[List[GroupInput]] = None
    role: Optional[str] = None


class JwtPayload(BaseModel):
    user_id: str
    identifiers: List[IdentifierInput]
    groups: Optional[List[GroupInput]] = None
    role: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class InvitationTarget(BaseModel):
    type: Literal["email", "username", "phoneNumber"]
    value: str


class Invitation(BaseModel):
    id: str
    target: Union[InvitationTarget, List[InvitationTarget]]  # API returns list or single
    groups: Optional[List[Optional[InvitationGroup]]] = None  # Full group information, can contain None
    status: str
    created_at: Optional[str] = Field(None, alias="createdAt")  # API uses camelCase
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    expires_at: Optional[str] = Field(None, alias="expiresAt")
    metadata: Optional[Dict[str, Union[str, int, bool]]] = None

    class Config:
        populate_by_name = True


class CreateInvitationRequest(BaseModel):
    target: InvitationTarget
    group_type: Optional[str] = None
    group_id: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Union[str, int, bool]]] = None


class AcceptInvitationsRequest(BaseModel):
    invitation_ids: List[str]
    target: InvitationTarget


class ApiResponse(BaseModel):
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: int = 200


class VortexApiError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
