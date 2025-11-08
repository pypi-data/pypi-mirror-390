"""
Advanced usage example for Bigconsole SDK Python

This example demonstrates:
1. Context manager usage
2. Error handling
3. Token management
4. Custom configurations
"""

import asyncio

from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig


async def advanced_example():
    # Custom configuration
    config = BigconsoleSDKConfig(
        endpoint="https://api.example.com/graphql",
        api_key="your-api-key",
        timeout=60.0,  # Custom timeout
    )

    # Using context manager for automatic cleanup
    async with BigconsoleSDK(config).client:
        sdk = BigconsoleSDK(config)

        try:
            # Token management
            existing_tokens = sdk.get_tokens()
            if existing_tokens:
                print(
                    f"Using existing tokens: {existing_tokens['access_token'][:20]}..."
                )
            else:
                print("No existing tokens found")

            # Custom error handling
            try:
                # This might fail if not authenticated
                current_user = await sdk.users.get_current_user()
                print(f"Authenticated as: {current_user.name}")
            except Exception as auth_error:
                print(f"Authentication required: {auth_error}")
                # Handle authentication flow here

            # Workspace operations (placeholder)
            try:
                workspaces = await sdk.workspaces.list_workspaces()
                print(f"Available workspaces: {len(workspaces) if workspaces else 0}")
            except Exception as ws_error:
                print(f"Workspace access error: {ws_error}")

            # Change endpoint dynamically
            sdk.set_endpoint("https://api-staging.example.com/graphql")
            print(f"Switched to: {sdk.get_endpoint()}")

        except Exception as e:
            print(f"Unexpected error: {e}")


async def token_refresh_example():
    """
    Example showing how to handle token refresh
    """
    config = BigconsoleSDKConfig(endpoint="https://api.example.com/graphql")

    sdk = BigconsoleSDK(config)

    try:
        # Simulate token expiry and refresh
        sdk.set_tokens("expired_token", "refresh_token")

        # In a real scenario, you would implement refresh logic
        # when you receive 401 responses

        # Example of clearing tokens on logout
        sdk.clear_tokens()
        print("Tokens cleared")

    finally:
        await sdk.client.close()


if __name__ == "__main__":
    print("Running advanced example...")
    asyncio.run(advanced_example())

    print("\nRunning token refresh example...")
    asyncio.run(token_refresh_example())
