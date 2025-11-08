from typing import TYPE_CHECKING

from ..types.common import (
    AuthResponse,
    ForgotPasswordResponse,
    ResetPasswordResponse,
    User,
    UserRegisterInput,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class AuthModule:
    def __init__(self, client: "BaseGraphQLClient") -> None:
        self.client = client

    async def register(self, input_data: UserRegisterInput) -> User:
        mutation = """
        mutation Register($input: userRegisterInput!) {
            register(input: $input) {
                id
                email
                name
                status
                createdAt
                updatedAt
            }
        }
        """

        variables = {
            "input": {
                "email": input_data.email,
                "name": input_data.name,
                "password": input_data.password,
            }
        }

        response = await self.client.request(mutation, variables)
        user_data = response["register"]

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status=user_data["status"],
            created_at=user_data.get("createdAt"),
            updated_at=user_data.get("updatedAt"),
        )

    async def verify_user(self, verification_token: str) -> AuthResponse:
        mutation = """
        mutation VerifyUser($verificationToken: String!) {
            verifyUser(verificationToken: $verificationToken) {
                defaultOrgName
                token
                user {
                    id
                    email
                    name
                    status
                }
                workspacesAndTenants {
                    tenantID
                    tenantName
                    workspaceID
                    workspaceName
                }
            }
        }
        """

        variables = {"verificationToken": verification_token}
        response = await self.client.request(mutation, variables)
        verify_data = response["verifyUser"]

        # Set tokens after successful verification
        if verify_data["token"]:
            self.client.set_tokens(
                access_token=verify_data["token"],
                # Backend doesn't provide refresh token in this response
                refresh_token="",  # nosec B106
            )

        user_data = verify_data["user"]
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status=user_data["status"],
        )

        return AuthResponse(
            default_org_name=verify_data.get("defaultOrgName"),
            token=verify_data["token"],
            user=user,
            workspaces_and_tenants=verify_data.get("workspacesAndTenants"),
        )

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        mutation = """
        mutation ForgotPassword($email: String!) {
            forgotPassword(email: $email) {
                success
            }
        }
        """

        variables = {"email": email}
        response = await self.client.request(mutation, variables)

        return ForgotPasswordResponse(success=response["forgotPassword"]["success"])

    async def reset_password(self, new_password: str, token: str) -> ResetPasswordResponse:
        mutation = """
        mutation ResetPassword($newPassword: String!, $token: String!) {
            resetPassword(newPassword: $newPassword, token: $token) {
                success
            }
        }
        """

        variables = {"newPassword": new_password, "token": token}
        response = await self.client.request(mutation, variables)

        return ResetPasswordResponse(success=response["resetPassword"]["success"])

    async def change_password(self, id: str, new_password: str) -> User:
        mutation = """
        mutation ChangePassword($id: ID!, $newPassword: String!) {
            changePassword(id: $id, newPassword: $newPassword) {
                id
                email
                name
                updatedAt
            }
        }
        """

        variables = {"id": id, "newPassword": new_password}
        response = await self.client.request(mutation, variables)
        user_data = response["changePassword"]

        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            status="",  # Not returned in this mutation
            updated_at=user_data.get("updatedAt"),
        )

    async def switch_workspace(self, workspace_id: str) -> str:
        mutation = """
        mutation SwitchWorkspace($workspaceID: ID!) {
            switchWorkspace(workspaceID: $workspaceID)
        }
        """

        variables = {"workspaceID": workspace_id}
        response = await self.client.request(mutation, variables)

        return str(response["switchWorkspace"])

    async def switch_project(self, proj_id: str) -> str:
        mutation = """
        mutation SwitchProject($projID: ID!) {
            switchProject(projID: $projID)
        }
        """

        variables = {"projID": proj_id}
        response = await self.client.request(mutation, variables)

        return str(response["switchProject"])

    def logout(self) -> None:
        self.client.clear_tokens()
