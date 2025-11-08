"""Type definitions for Collaboration module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ActiveUser:
    """Active user in a collaboration session."""

    user_id: str
    user_name: str
    cursor: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None


@dataclass
class CollaborationSession:
    """Collaboration session details."""

    id: str
    dashboard_id: str
    active_users: List[ActiveUser]
    created_at: Optional[str] = None


@dataclass
class CreateCollaborationSessionInput:
    """Input for creating a collaboration session."""

    dashboard_id: str


@dataclass
class CreateCollaborationSessionResponse:
    """Response from creating a collaboration session."""

    success: bool
    message: Optional[str] = None
    session: Optional[CollaborationSession] = None


@dataclass
class JoinCollaborationSessionResponse:
    """Response from joining a collaboration session."""

    success: bool
    message: Optional[str] = None
    user: Optional[ActiveUser] = None


@dataclass
class LeaveCollaborationSessionResponse:
    """Response from leaving a collaboration session."""

    success: bool
    message: Optional[str] = None


@dataclass
class AddCollaborationCommentInput:
    """Input for adding a collaboration comment."""

    dashboard_id: str
    content: str
    widget_id: Optional[str] = None


@dataclass
class CollaborationComment:
    """Collaboration comment details."""

    id: str
    user_id: str
    user_name: str
    content: str
    position: Optional[Dict[str, Any]] = None
    widget_id: Optional[str] = None
    resolved: bool = False
    created_at: Optional[str] = None


@dataclass
class ResolveCollaborationCommentResponse:
    """Response from resolving a comment."""

    success: bool
    message: Optional[str] = None


@dataclass
class SendCollaborationMessageInput:
    """Input for sending a collaboration message."""

    dashboard_id: str
    message: str


@dataclass
class SendCollaborationMessageResponse:
    """Response from sending a message."""

    success: bool
    message: Optional[str] = None


@dataclass
class CollaborationChange:
    """Collaboration change entry in history."""

    id: str
    type: str
    user_id: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@dataclass
class CollaborationHistoryResponse:
    """Response from collaboration history query."""

    changes: List[CollaborationChange]
    total: int


@dataclass
class CollaborationMessage:
    """Collaboration message details."""

    id: str
    user_id: str
    user_name: str
    message: str
    timestamp: Optional[str] = None


@dataclass
class CollaborationMessagesResponse:
    """Response from collaboration messages query."""

    messages: List[CollaborationMessage]
    total: int
