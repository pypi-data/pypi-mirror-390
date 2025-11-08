"""
Basic usage example for Bigconsole SDK Python

This example demonstrates how to:
1. Initialize the SDK
2. Register a new user
3. Verify user
4. Perform authenticated operations
"""

import asyncio

from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig
from bigconsole_sdk.types.common import UserRegisterInput


async def main():
    # Initialize the SDK
    config = BigconsoleSDKConfig(
        endpoint="https://api.example.com/graphql",
        api_key="your-api-key-here",  # Optional
    )

    sdk = BigconsoleSDK(config)

    try:
        # Example 1: Register a new user
        print("Registering a new user...")
        user_input = UserRegisterInput(
            email="user@example.com", name="John Doe", password="secure_password"
        )

        user = await sdk.auth.register(user_input)
        print(f"User registered: {user.name} ({user.email})")

        # Example 2: Verify user (assuming you have a verification token)
        # verification_token = "your-verification-token"
        # auth_response = await sdk.auth.verify_user(verification_token)
        # print(f"User verified! Token: {auth_response.token[:20]}...")

        # Example 3: Set tokens manually if you have them
        sdk.set_tokens(
            access_token="your-access-token", refresh_token="your-refresh-token"
        )

        # Example 4: Get current user (requires authentication)
        # current_user = await sdk.users.get_current_user()
        # print(f"Current user: {current_user.name}")

        # Example 5: List users (requires appropriate permissions)
        # users = await sdk.users.list_users(limit=10)
        # print(f"Found {len(users)} users")

        # Example 6: Forgot password
        forgot_response = await sdk.auth.forgot_password("user@example.com")
        print(f"Password reset email sent: {forgot_response.success}")

        # Example 7: Logout
        sdk.auth.logout()
        print("Logged out successfully")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Always close the client when done
        await sdk.client.close()


# Synchronous wrapper example
def sync_example():
    """
    Example of using the SDK in a synchronous context
    """
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
