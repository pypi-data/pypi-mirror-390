# Bigconsole SDK - Module Reference

## Overview

The Bigconsole SDK provides a comprehensive Python interface for the Bigconsole API. This document describes all available modules and their current implementation status.

## Package Information

- **Package Name**: `bigconsole-sdk`
- **Version**: `2025.11.0`
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **License**: Proprietary (Burdenoff Consultancy Services Pvt. Ltd.)

## Installation

```bash
pip install bigconsole-sdk
```

## Quick Start

```python
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig

# Initialize SDK
config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    api_key="your-api-key"
)
sdk = BigconsoleSDK(config)

# Use SDK modules
user = await sdk.auth.register(...)
current_user = await sdk.users.get_current_user()
```

## Module Overview

The SDK contains 21 modules organized by functionality:

### Implemented Modules (4)

- **auth** - Authentication and user registration
- **users** - User management operations
- **client** - GraphQL client and configuration
- **types** - Type definitions and data classes

### Placeholder Modules (17)

- **workspaces** - Workspace management
- **rbac** - Role-based access control
- **teams** - Team operations
- **projects** - Project management
- **organizations** - Organization management
- **billing** - Billing account management
- **payments** - Payment processing
- **plans** - Subscription plans
- **addons** - Add-on management
- **quotas** - Quota management
- **store** - Store/marketplace functionality
- **support** - Support ticket management
- **usage** - Usage analytics
- **utils** - Utility functions
- **products** - Product management
- **config** - Configuration management
- **resources** - Resource management

## Detailed Module Reference

### Authentication Module (`sdk.auth`)

**Status**: Fully Implemented

The authentication module handles user registration, verification, password management, and workspace/project switching.

**Methods:**

- `register(input_data: UserRegisterInput) -> User` - Register new user
- `verify_user(verification_token: str) -> AuthResponse` - Verify user email
- `forgot_password(email: str) -> ForgotPasswordResponse` - Request password reset
- `reset_password(new_password: str, token: str) -> ResetPasswordResponse` - Reset password
- `change_password(id: str, new_password: str) -> User` - Change user password
- `switch_workspace(workspace_id: str) -> str` - Switch active workspace
- `switch_project(proj_id: str) -> str` - Switch active project
- `logout() -> None` - Clear authentication tokens

**Example:**

```python
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig
from bigconsole_sdk.types.common import UserRegisterInput

# Initialize SDK
config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    api_key="your-api-key"
)
sdk = BigconsoleSDK(config)

# Register new user
user_input = UserRegisterInput(
    email="user@example.com",
    name="John Doe",
    password="secure_password"
)
user = await sdk.auth.register(user_input)
print(f"Registered user: {user.email}")

# Verify email
auth_response = await sdk.auth.verify_user("verification_token_here")
print(f"Logged in as: {auth_response.user.name}")

# Request password reset
forgot_response = await sdk.auth.forgot_password("user@example.com")
print(f"Password reset email sent: {forgot_response.success}")

# Reset password with token
reset_response = await sdk.auth.reset_password("new_password", "reset_token")
print(f"Password reset successful: {reset_response.success}")

# Change password
updated_user = await sdk.auth.change_password("user_id", "new_password")
print(f"Password changed for: {updated_user.email}")

# Switch workspace
result = await sdk.auth.switch_workspace("workspace_id")
print(f"Switched to workspace: {result}")

# Switch project
result = await sdk.auth.switch_project("project_id")
print(f"Switched to project: {result}")

# Logout
sdk.auth.logout()
```

### User Module (`sdk.users`)

**Status**: Fully Implemented

User management operations for retrieving and updating user information.

**Methods:**

- `get_current_user() -> User` - Get currently authenticated user
- `get_user_by_id(user_id: str) -> User` - Get user by ID
- `list_users(limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]` - List all users
- `update_user(user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> User` - Update user information

**Example:**

```python
# Get current user
current_user = await sdk.users.get_current_user()
print(f"Current user: {current_user.name} ({current_user.email})")

# Get specific user
user = await sdk.users.get_user_by_id("user_id_here")
print(f"User: {user.name}")

# List all users
users = await sdk.users.list_users(limit=10, offset=0)
for user in users:
    print(f"- {user.name} ({user.email})")

# Update user
updated_user = await sdk.users.update_user(
    user_id="user_id_here",
    name="Jane Doe",
    email="jane.doe@example.com"
)
print(f"Updated user: {updated_user.name}")
```

### Client Module (`sdk.client`)

**Status**: Fully Implemented

GraphQL client and configuration management for making API requests.

**Classes:**

- `BaseGraphQLClient` - Async HTTP client for GraphQL operations
- `BigconsoleSDKConfig` - SDK configuration dataclass
- `AuthTokens` - Authentication token storage

**Configuration Options:**

- `endpoint: str` - GraphQL API endpoint (required)
- `api_key: str` - API key for authentication (optional)
- `access_token: str` - JWT access token (optional)
- `refresh_token: str` - JWT refresh token (optional)
- `timeout: float` - Request timeout in seconds (default: 30.0)

**Client Methods:**

- `request(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]` - Execute GraphQL request
- `set_tokens(access_token: str, refresh_token: str) -> None` - Set authentication tokens
- `get_tokens() -> Optional[AuthTokens]` - Get current authentication tokens
- `clear_tokens() -> None` - Clear authentication tokens
- `set_endpoint(endpoint: str) -> None` - Update API endpoint
- `get_endpoint() -> str` - Get current API endpoint
- `close() -> None` - Close HTTP client connection

**Example:**

```python
from bigconsole_sdk import BigconsoleSDKConfig
from bigconsole_sdk.client import BaseGraphQLClient

# Configuration with API key
config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    api_key="your-api-key",
    timeout=60.0
)

# Configuration with tokens
config_with_tokens = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    access_token="your-access-token",
    refresh_token="your-refresh-token"
)

# Direct client usage
client = BaseGraphQLClient(config)
query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
"""
result = await client.request(query, {"id": "user_id"})
await client.close()

# Using as context manager
async with BaseGraphQLClient(config) as client:
    result = await client.request(query, {"id": "user_id"})
```

### Types Module (`sdk.types`)

**Status**: Fully Implemented

Type definitions and data classes for API operations.

**Types:**

- `User` - User data structure
  - `id: str` - User ID
  - `email: str` - User email address
  - `name: str` - User display name
  - `status: str` - User account status
  - `created_at: Optional[datetime]` - Account creation timestamp
  - `updated_at: Optional[datetime]` - Last update timestamp

- `AuthResponse` - Authentication response
  - `default_org_name: Optional[str]` - Default organization name
  - `token: str` - Access token
  - `user: User` - User object
  - `workspaces_and_tenants: Optional[List[Dict[str, Any]]]` - Available workspaces

- `UserRegisterInput` - User registration input
  - `email: str` - User email
  - `name: str` - User name
  - `password: str` - User password

- `ForgotPasswordResponse` - Password reset response
  - `success: bool` - Operation success status

- `ResetPasswordResponse` - Password reset confirmation
  - `success: bool` - Operation success status

- `RegisterResponse` - Registration response
  - `user: User` - Registered user object

**Example:**

```python
from bigconsole_sdk.types.common import (
    User,
    AuthResponse,
    UserRegisterInput,
    ForgotPasswordResponse,
    ResetPasswordResponse
)

# Create user registration input
register_input = UserRegisterInput(
    email="user@example.com",
    name="John Doe",
    password="secure_password"
)

# User object
user = User(
    id="user_123",
    email="user@example.com",
    name="John Doe",
    status="active"
)
```

---

## Placeholder Modules

The following modules have basic structure in place but are not yet fully implemented. Each module contains placeholder methods with TODO comments.

### Workspace Module (`sdk.workspaces`)

**Status**: Placeholder

Workspace management operations (to be implemented).

**Planned Methods:**
- `list_workspaces()` - List all workspaces
- `get_workspace(workspace_id: str)` - Get workspace by ID
- `create_workspace(name: str, description: str)` - Create new workspace

### RBAC Module (`sdk.rbac`)

**Status**: Placeholder

Role-based access control operations (to be implemented).

**Planned Functionality:**
- Role management
- Permission management
- Access control policies

### Team Module (`sdk.teams`)

**Status**: Placeholder

Team management operations (to be implemented).

**Planned Functionality:**
- Team creation and management
- Team member management
- Team permissions

### Project Module (`sdk.projects`)

**Status**: Placeholder

Project management operations (to be implemented).

**Planned Functionality:**
- Project creation and management
- Project configuration
- Project member management

### Organization Module (`sdk.organizations`)

**Status**: Placeholder

Organization management operations (to be implemented).

**Planned Functionality:**
- Organization creation and management
- Organization settings
- Organization member management

### Billing Module (`sdk.billing`)

**Status**: Placeholder

Billing account management (to be implemented).

**Planned Functionality:**
- Billing account management
- Invoice management
- Billing history

### Payment Module (`sdk.payments`)

**Status**: Placeholder

Payment processing operations (to be implemented).

**Planned Functionality:**
- Payment method management
- Payment processing
- Payment history

### Plan Module (`sdk.plans`)

**Status**: Placeholder

Subscription plan management (to be implemented).

**Planned Functionality:**
- Plan listing and details
- Plan subscription
- Plan upgrades/downgrades

### AddOn Module (`sdk.addons`)

**Status**: Placeholder

Add-on management operations (to be implemented).

**Planned Functionality:**
- Add-on listing
- Add-on subscription
- Add-on management

### Quota Module (`sdk.quotas`)

**Status**: Placeholder

Quota management operations (to be implemented).

**Planned Functionality:**
- Quota monitoring
- Quota limits
- Usage tracking

### Store Module (`sdk.store`)

**Status**: Placeholder

Store/marketplace functionality (to be implemented).

**Planned Functionality:**
- Product browsing
- Purchase management
- License management

### Support Module (`sdk.support`)

**Status**: Placeholder

Support ticket management (to be implemented).

**Planned Functionality:**
- Ticket creation
- Ticket management
- Support history

### Usage Module (`sdk.usage`)

**Status**: Placeholder

Usage analytics and reporting (to be implemented).

**Planned Functionality:**
- Usage metrics
- Analytics reporting
- Resource consumption tracking

### Utils Module (`sdk.utils`)

**Status**: Placeholder

Utility functions and helpers (to be implemented).

**Planned Functionality:**
- Common utilities
- Helper functions
- Data transformations

### Product Module (`sdk.products`)

**Status**: Placeholder

Product management operations (to be implemented).

**Planned Functionality:**
- Product catalog management
- Product configuration
- Product lifecycle management

### Config Module (`sdk.config`)

**Status**: Placeholder

Configuration management operations (to be implemented).

**Planned Functionality:**
- Configuration management
- Settings management
- Environment configuration

### Resources Module (`sdk.resources`)

**Status**: Placeholder

Resource management operations (to be implemented).

**Planned Functionality:**
- Resource allocation
- Resource monitoring
- Resource lifecycle management

---

## Module Status Summary

| Module | Status | Methods | Description |
|--------|--------|---------|-------------|
| auth | Implemented | 8 | User authentication and registration |
| users | Implemented | 4 | User management operations |
| client | Implemented | 8 | GraphQL client and configuration |
| types | Implemented | 6 | Type definitions and data classes |
| workspaces | Placeholder | 0 | Workspace management |
| rbac | Placeholder | 0 | Role-based access control |
| teams | Placeholder | 0 | Team operations |
| projects | Placeholder | 0 | Project management |
| organizations | Placeholder | 0 | Organization management |
| billing | Placeholder | 0 | Billing management |
| payments | Placeholder | 0 | Payment processing |
| plans | Placeholder | 0 | Subscription plans |
| addons | Placeholder | 0 | Add-on management |
| quotas | Placeholder | 0 | Quota management |
| store | Placeholder | 0 | Store functionality |
| support | Placeholder | 0 | Support tickets |
| usage | Placeholder | 0 | Usage analytics |
| utils | Placeholder | 0 | Utility functions |
| products | Placeholder | 0 | Product management |
| config | Placeholder | 0 | Configuration |
| resources | Placeholder | 0 | Resource management |

**Total:** 21 modules (4 implemented, 17 placeholder)

---

## SDK Initialization

The SDK uses a centralized initialization pattern where all modules are instantiated through the main `BigconsoleSDK` class:

```python
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig

# Create configuration
config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    api_key="your-api-key"
)

# Initialize SDK (all modules initialized automatically)
sdk = BigconsoleSDK(config)

# Access modules through SDK instance
sdk.auth          # AuthModule
sdk.users         # UserModule
sdk.workspaces    # WorkspaceModule
sdk.rbac          # RBACModule
sdk.teams         # TeamModule
sdk.projects      # ProjectModule
sdk.resources     # ResourceModule
sdk.billing       # BillingModule
sdk.organizations # OrganizationModule
sdk.payments      # PaymentModule
sdk.quotas        # QuotaModule
sdk.store         # StoreModule
sdk.support       # SupportModule
sdk.usage         # UsageModule
sdk.utils         # SDKUtils
sdk.addons        # AddOnModule
sdk.plans         # PlanModule
sdk.products      # ProductModule
sdk.config        # ConfigModule
```

## SDK-Level Methods

The `BigconsoleSDK` class provides convenient methods for token and endpoint management:

**Token Management:**
- `set_tokens(access_token: str, refresh_token: str) -> None` - Set authentication tokens
- `get_tokens() -> Optional[dict]` - Get current tokens as dictionary
- `clear_tokens() -> None` - Clear all authentication tokens

**Endpoint Management:**
- `set_endpoint(endpoint: str) -> None` - Update the API endpoint
- `get_endpoint() -> str` - Get current API endpoint

**Example:**

```python
# Set tokens after login
sdk.set_tokens(
    access_token="your-access-token",
    refresh_token="your-refresh-token"
)

# Get current tokens
tokens = sdk.get_tokens()
print(f"Access token: {tokens['access_token']}")

# Change endpoint
sdk.set_endpoint("https://new-api.example.com/graphql")

# Clear tokens on logout
sdk.clear_tokens()
```

---

## Development Roadmap

The following modules are planned for future implementation:

### Phase 1 - Core Features
1. Workspace operations
2. Project management
3. Team management
4. RBAC system

### Phase 2 - Business Features
5. Organization management
6. Billing and payment integration
7. Subscription plans
8. Add-on management

### Phase 3 - Advanced Features
9. Usage analytics
10. Resource management
11. Quota management
12. Support system

### Phase 4 - Additional Features
13. Store/marketplace functionality
14. Configuration management
15. Product management
16. Utility enhancements

---

## Error Handling

The SDK uses exception-based error handling. All errors are raised as Python exceptions:

```python
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig

config = BigconsoleSDKConfig(
    endpoint="https://api.example.com/graphql",
    api_key="your-api-key"
)
sdk = BigconsoleSDK(config)

try:
    user = await sdk.users.get_current_user()
except Exception as e:
    print(f"Error: {e}")
```

Common error scenarios:
- **GraphQL Errors**: Returned when the API returns errors in the response
- **HTTP Errors**: Network or HTTP status errors (401, 404, 500, etc.)
- **Request Errors**: Connection timeouts, invalid requests, etc.

---

## Async/Await Pattern

All SDK methods are asynchronous and must be called with `await`:

```python
import asyncio
from bigconsole_sdk import BigconsoleSDK, BigconsoleSDKConfig

async def main():
    config = BigconsoleSDKConfig(
        endpoint="https://api.example.com/graphql",
        api_key="your-api-key"
    )
    sdk = BigconsoleSDK(config)

    # All methods must be awaited
    user = await sdk.users.get_current_user()
    print(f"User: {user.name}")

    # Close client when done
    await sdk.client.close()

# Run async code
asyncio.run(main())
```

For context manager usage:

```python
async def main():
    config = BigconsoleSDKConfig(
        endpoint="https://api.example.com/graphql",
        api_key="your-api-key"
    )

    async with BigconsoleSDK(config).client as client:
        # Client automatically closed after block
        pass
```

---

## Support & Resources

- **Documentation**: `/docs/`
- **Publishing Guide**: `/docs/PUBLISHING_GUIDE.md`
- **Examples**: `/examples/`
- **Test Scripts**: `/scripts/examples/`
- **Issues**: https://github.com/Algoshred/bigconsole-sdk-python/issues
- **PyPI**: https://pypi.org/project/bigconsole-sdk/

---

Last Updated: 2025-11-03
Version: 2025.11.0
SDK Modules: 21 (4 implemented, 17 placeholder)
