"""
ayz-auth: FastAPI middleware for Stytch B2B authentication with Redis caching.

This package provides a clean, reusable authentication middleware for FastAPI
applications using Stytch B2B authentication services with Redis caching for
optimal performance.

Version 2.0.0 adds support for:
- Organization entitlements and subscription tiers
- User team context
- MongoDB integration for entitlements data
- Entitlement-based authorization decorators

Version 2.1.1 fixes:
- User lookup now uses user_organization_memberships collection (fixes stale stytch_member_id issue)
- current_team_id now correctly populated in StytchContext
"""

from .decorators import (
    require_all_entitlements,
    require_any_entitlement,
    require_entitlement,
)
from .middleware import create_auth_dependency, verify_auth, verify_auth_optional
from .models.context import StytchContext
from .utils.exceptions import (
    AuthenticationError,
    StytchAPIError,
    TokenExtractionError,
    TokenVerificationError,
)

__version__ = "2.1.1"
__all__ = [
    # Core authentication
    "verify_auth",
    "verify_auth_optional",
    "create_auth_dependency",
    # Entitlement decorators (v2.0.0+)
    "require_entitlement",
    "require_any_entitlement",
    "require_all_entitlements",
    # Models
    "StytchContext",
    # Exceptions
    "AuthenticationError",
    "TokenExtractionError",
    "TokenVerificationError",
    "StytchAPIError",
]
