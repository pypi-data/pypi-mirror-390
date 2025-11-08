"""
Collaboration Module for BigConsole SDK.

This module provides real-time collaboration functionality including:
- Creating and managing collaboration sessions
- Joining and leaving sessions
- Adding and managing comments
- Sending messages within sessions
- Viewing collaboration history
"""

from typing import TYPE_CHECKING, List, Optional

from ..types.collaboration import (
    ActiveUser,
    AddCollaborationCommentInput,
    CollaborationChange,
    CollaborationComment,
    CollaborationHistoryResponse,
    CollaborationMessage,
    CollaborationMessagesResponse,
    CollaborationSession,
    CreateCollaborationSessionInput,
    CreateCollaborationSessionResponse,
    JoinCollaborationSessionResponse,
    LeaveCollaborationSessionResponse,
    ResolveCollaborationCommentResponse,
    SendCollaborationMessageInput,
    SendCollaborationMessageResponse,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class CollaborationModule:
    """
    Collaboration Module for BigConsole SDK.

    Provides real-time collaboration features for dashboards including
    sessions, comments, messages, and collaborative editing.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize collaboration module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def create_session(
        self, input_data: CreateCollaborationSessionInput
    ) -> CreateCollaborationSessionResponse:
        """
        Create a new collaboration session for a dashboard.

        Initiates a collaboration session that allows multiple users to
        work together on a dashboard in real-time.

        Args:
            input_data: Session creation input with dashboard ID.

        Returns:
            CreateCollaborationSessionResponse with session details.

        Example:
            >>> input_data = CreateCollaborationSessionInput(
            ...     dashboard_id="dashboard-123"
            ... )
            >>> result = await sdk.collaboration.create_session(input_data)
            >>> print(f"Session created: {result.session.id}")
        """
        mutation = """
        mutation CreateCollaborationSession($input: CreateCollaborationSessionInput!) {
            createCollaborationSession(input: $input) {
                success
                message
                session {
                    id
                    dashboardId
                }
            }
        }
        """

        variables = {
            "input": {
                "dashboardId": input_data.dashboard_id,
            }
        }

        response = await self.client.request(mutation, variables)
        data = response["createCollaborationSession"]

        session_data = data.get("session", {})
        session = CollaborationSession(
            id=session_data.get("id", ""),
            dashboard_id=session_data.get("dashboardId", ""),
            active_users=[],
            created_at=None,
        )

        return CreateCollaborationSessionResponse(
            success=data["success"],
            message=data.get("message"),
            session=session,
        )

    async def join_session(self, session_id: str) -> JoinCollaborationSessionResponse:
        """
        Join an existing collaboration session.

        Allows a user to join an active collaboration session and
        participate in real-time editing and communication.

        Args:
            session_id: The ID of the session to join.

        Returns:
            JoinCollaborationSessionResponse with user details.

        Example:
            >>> result = await sdk.collaboration.join_session("session-123")
            >>> if result.success:
            ...     print(f"Joined as: {result.user.user_name}")
        """
        mutation = """
        mutation JoinCollaborationSession($sessionId: String!) {
            joinCollaborationSession(sessionId: $sessionId) {
                success
                message
                user {
                    userId
                    userName
                }
            }
        }
        """

        variables = {"sessionId": session_id}
        response = await self.client.request(mutation, variables)
        data = response["joinCollaborationSession"]

        user_data = data.get("user", {})
        user = ActiveUser(
            user_id=user_data.get("userId", ""),
            user_name=user_data.get("userName", ""),
            cursor=None,
            selection=None,
        )

        return JoinCollaborationSessionResponse(
            success=data["success"],
            message=data.get("message"),
            user=user,
        )

    async def leave_session(self, session_id: str) -> LeaveCollaborationSessionResponse:
        """
        Leave a collaboration session.

        Removes the current user from an active collaboration session.

        Args:
            session_id: The ID of the session to leave.

        Returns:
            LeaveCollaborationSessionResponse with success status.

        Example:
            >>> result = await sdk.collaboration.leave_session("session-123")
            >>> if result.success:
            ...     print("Left session successfully")
        """
        mutation = """
        mutation LeaveCollaborationSession($sessionId: String!) {
            leaveCollaborationSession(sessionId: $sessionId) {
                success
                message
            }
        }
        """

        variables = {"sessionId": session_id}
        response = await self.client.request(mutation, variables)
        data = response["leaveCollaborationSession"]

        return LeaveCollaborationSessionResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def add_comment(self, input_data: AddCollaborationCommentInput) -> CollaborationComment:
        """
        Add a comment to a dashboard.

        Creates a new comment on a dashboard or specific widget for
        collaborative discussion and feedback.

        Args:
            input_data: Comment input with dashboard ID, content, and optional widget ID.

        Returns:
            CollaborationComment with the created comment details.

        Example:
            >>> input_data = AddCollaborationCommentInput(
            ...     dashboard_id="dashboard-123",
            ...     content="This chart needs more context",
            ...     widget_id="widget-456"
            ... )
            >>> comment = await sdk.collaboration.add_comment(input_data)
            >>> print(f"Comment added: {comment.id}")
        """
        mutation = """
        mutation AddCollaborationComment($input: AddCollaborationCommentInput!) {
            addCollaborationComment(input: $input) {
                success
                message
                comment {
                    id
                    content
                    createdAt
                }
            }
        }
        """

        variables = {
            "input": {
                "dashboardId": input_data.dashboard_id,
                "content": input_data.content,
            }
        }

        if input_data.widget_id:
            variables["input"]["widgetId"] = input_data.widget_id

        response = await self.client.request(mutation, variables)
        data = response["addCollaborationComment"]
        comment_data = data.get("comment", {})

        return CollaborationComment(
            id=comment_data.get("id", ""),
            user_id="",  # Not returned in mutation response
            user_name="",  # Not returned in mutation response
            content=comment_data.get("content", ""),
            position=None,
            widget_id=input_data.widget_id,
            resolved=False,
            created_at=comment_data.get("createdAt"),
        )

    async def resolve_comment(self, comment_id: str) -> ResolveCollaborationCommentResponse:
        """
        Resolve a collaboration comment.

        Marks a comment as resolved, typically after addressing the
        feedback or completing a discussion.

        Args:
            comment_id: The ID of the comment to resolve.

        Returns:
            ResolveCollaborationCommentResponse with success status.

        Example:
            >>> result = await sdk.collaboration.resolve_comment("comment-123")
            >>> if result.success:
            ...     print("Comment resolved")
        """
        mutation = """
        mutation ResolveCollaborationComment($commentId: String!) {
            resolveCollaborationComment(commentId: $commentId) {
                success
                message
            }
        }
        """

        variables = {"commentId": comment_id}
        response = await self.client.request(mutation, variables)
        data = response["resolveCollaborationComment"]

        return ResolveCollaborationCommentResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def send_message(
        self, input_data: SendCollaborationMessageInput
    ) -> SendCollaborationMessageResponse:
        """
        Send a message in a collaboration session.

        Sends a real-time message to all participants in an active
        collaboration session.

        Args:
            input_data: Message input with dashboard ID and message content.

        Returns:
            SendCollaborationMessageResponse with success status.

        Example:
            >>> input_data = SendCollaborationMessageInput(
            ...     dashboard_id="dashboard-123",
            ...     message="Updated the sales chart with Q4 data"
            ... )
            >>> result = await sdk.collaboration.send_message(input_data)
            >>> if result.success:
            ...     print("Message sent")
        """
        mutation = """
        mutation SendCollaborationMessage($input: SendCollaborationMessageInput!) {
            sendCollaborationMessage(input: $input) {
                success
                message
            }
        }
        """

        variables = {
            "input": {
                "dashboardId": input_data.dashboard_id,
                "message": input_data.message,
            }
        }

        response = await self.client.request(mutation, variables)
        data = response["sendCollaborationMessage"]

        return SendCollaborationMessageResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def get_session(self, dashboard_id: str) -> CollaborationSession:
        """
        Get collaboration session details for a dashboard.

        Retrieves information about an active collaboration session
        including active users and their cursor positions.

        Args:
            dashboard_id: The ID of the dashboard.

        Returns:
            CollaborationSession with session details and active users.

        Example:
            >>> session = await sdk.collaboration.get_session("dashboard-123")
            >>> print(f"Active users: {len(session.active_users)}")
            >>> for user in session.active_users:
            ...     print(f"- {user.user_name}")
        """
        query = """
        query CollaborationSession($dashboardId: String!) {
            collaborationSession(dashboardId: $dashboardId) {
                id
                dashboardId
                activeUsers {
                    userId
                    userName
                    cursor
                    selection
                }
                createdAt
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(query, variables)
        data = response["collaborationSession"]

        active_users = [
            ActiveUser(
                user_id=user["userId"],
                user_name=user["userName"],
                cursor=user.get("cursor"),
                selection=user.get("selection"),
            )
            for user in data.get("activeUsers", [])
        ]

        return CollaborationSession(
            id=data["id"],
            dashboard_id=data["dashboardId"],
            active_users=active_users,
            created_at=data.get("createdAt"),
        )

    async def get_history(
        self, dashboard_id: str, limit: Optional[int] = None, skip: Optional[int] = None
    ) -> CollaborationHistoryResponse:
        """
        Get collaboration history for a dashboard.

        Retrieves the history of collaborative changes made to a dashboard
        including edits, additions, and deletions.

        Args:
            dashboard_id: The ID of the dashboard.
            limit: Optional maximum number of changes to return.
            skip: Optional number of changes to skip for pagination.

        Returns:
            CollaborationHistoryResponse with changes and total count.

        Example:
            >>> history = await sdk.collaboration.get_history(
            ...     "dashboard-123",
            ...     limit=10
            ... )
            >>> print(f"Total changes: {history.total}")
            >>> for change in history.changes:
            ...     print(f"{change.type} by {change.user_id} at {change.timestamp}")
        """
        query = """
        query CollaborationHistory($dashboardId: String!, $limit: Int, $skip: Int) {
            collaborationHistory(dashboardId: $dashboardId, limit: $limit, skip: $skip) {
                changes {
                    id
                    type
                    userId
                    payload
                    timestamp
                }
                total
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        if limit is not None:
            variables["limit"] = limit
        if skip is not None:
            variables["skip"] = skip

        response = await self.client.request(query, variables)
        data = response["collaborationHistory"]

        changes = [
            CollaborationChange(
                id=change["id"],
                type=change["type"],
                user_id=change["userId"],
                payload=change.get("payload"),
                timestamp=change.get("timestamp"),
            )
            for change in data.get("changes", [])
        ]

        return CollaborationHistoryResponse(
            changes=changes,
            total=data.get("total", 0),
        )

    async def get_messages(
        self, session_id: str, limit: Optional[int] = None, skip: Optional[int] = None
    ) -> CollaborationMessagesResponse:
        """
        Get messages from a collaboration session.

        Retrieves all messages sent within a collaboration session,
        useful for reviewing discussion history.

        Args:
            session_id: The ID of the collaboration session.
            limit: Optional maximum number of messages to return.
            skip: Optional number of messages to skip for pagination.

        Returns:
            CollaborationMessagesResponse with messages and total count.

        Example:
            >>> messages = await sdk.collaboration.get_messages(
            ...     "session-123",
            ...     limit=20
            ... )
            >>> for msg in messages.messages:
            ...     print(f"{msg.user_name}: {msg.message}")
        """
        query = """
        query CollaborationMessages($sessionId: String!, $limit: Int, $skip: Int) {
            collaborationMessages(sessionId: $sessionId, limit: $limit, skip: $skip) {
                messages {
                    id
                    userId
                    userName
                    message
                    timestamp
                }
                total
            }
        }
        """

        variables = {"sessionId": session_id}
        if limit is not None:
            variables["limit"] = limit
        if skip is not None:
            variables["skip"] = skip

        response = await self.client.request(query, variables)
        data = response["collaborationMessages"]

        messages = [
            CollaborationMessage(
                id=msg["id"],
                user_id=msg["userId"],
                user_name=msg["userName"],
                message=msg["message"],
                timestamp=msg.get("timestamp"),
            )
            for msg in data.get("messages", [])
        ]

        return CollaborationMessagesResponse(
            messages=messages,
            total=data.get("total", 0),
        )

    async def list_comments(
        self, dashboard_id: str, widget_id: Optional[str] = None, resolved: Optional[bool] = None
    ) -> List[CollaborationComment]:
        """
        List comments for a dashboard.

        Retrieves all comments on a dashboard, optionally filtered by
        widget or resolution status.

        Args:
            dashboard_id: The ID of the dashboard.
            widget_id: Optional widget ID to filter comments.
            resolved: Optional filter for resolved/unresolved comments.

        Returns:
            List of CollaborationComment objects.

        Example:
            >>> # Get all unresolved comments
            >>> comments = await sdk.collaboration.list_comments(
            ...     "dashboard-123",
            ...     resolved=False
            ... )
            >>> for comment in comments:
            ...     print(f"{comment.user_name}: {comment.content}")

            >>> # Get comments for a specific widget
            >>> widget_comments = await sdk.collaboration.list_comments(
            ...     "dashboard-123",
            ...     widget_id="widget-456"
            ... )
        """
        query = """
        query CollaborationComments(
            $dashboardId: String!,
            $widgetId: String,
            $resolved: Boolean
        ) {
            collaborationComments(
                dashboardId: $dashboardId,
                widgetId: $widgetId,
                resolved: $resolved
            ) {
                id
                userId
                userName
                content
                position
                widgetId
                resolved
                createdAt
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        if widget_id is not None:
            variables["widgetId"] = widget_id
        if resolved is not None:
            variables["resolved"] = resolved

        response = await self.client.request(query, variables)
        comments_data = response["collaborationComments"]

        return [
            CollaborationComment(
                id=comment["id"],
                user_id=comment["userId"],
                user_name=comment["userName"],
                content=comment["content"],
                position=comment.get("position"),
                widget_id=comment.get("widgetId"),
                resolved=comment.get("resolved", False),
                created_at=comment.get("createdAt"),
            )
            for comment in comments_data
        ]
