from typing import TYPE_CHECKING, List, Optional

from ..types.common import User

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class UserModule:
    def __init__(self, client: "BaseGraphQLClient") -> None:
        self.client = client

    async def get_current_user(self) -> User:
        query = """
        query GetCurrentUser {
            currentUser {
                id
                email
                name
                status
                createdAt
                updatedAt
            }
        }
        """

        response = await self.client.request(query)
        user_data = response["currentUser"]

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status=user_data["status"],
            created_at=user_data.get("createdAt"),
            updated_at=user_data.get("updatedAt"),
        )

    async def get_user_by_id(self, user_id: str) -> User:
        query = """
        query GetUserById($id: ID!) {
            user(id: $id) {
                id
                email
                name
                status
                createdAt
                updatedAt
            }
        }
        """

        variables = {"id": user_id}
        response = await self.client.request(query, variables)
        user_data = response["user"]

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status=user_data["status"],
            created_at=user_data.get("createdAt"),
            updated_at=user_data.get("updatedAt"),
        )

    async def list_users(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[User]:
        query = """
        query ListUsers($limit: Int, $offset: Int) {
            users(limit: $limit, offset: $offset) {
                id
                email
                name
                status
                createdAt
                updatedAt
            }
        }
        """

        variables = {"limit": limit, "offset": offset}
        response = await self.client.request(query, variables)
        users_data = response["users"]

        return [
            User(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                status=user["status"],
                created_at=user.get("createdAt"),
                updated_at=user.get("updatedAt"),
            )
            for user in users_data
        ]

    async def update_user(
        self, user_id: str, name: Optional[str] = None, email: Optional[str] = None
    ) -> User:
        mutation = """
        mutation UpdateUser($id: ID!, $name: String, $email: String) {
            updateUser(id: $id, name: $name, email: $email) {
                id
                email
                name
                status
                updatedAt
            }
        }
        """

        variables = {"id": user_id}
        if name is not None:
            variables["name"] = name
        if email is not None:
            variables["email"] = email

        response = await self.client.request(mutation, variables)
        user_data = response["updateUser"]

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status=user_data["status"],
            updated_at=user_data.get("updatedAt"),
        )
