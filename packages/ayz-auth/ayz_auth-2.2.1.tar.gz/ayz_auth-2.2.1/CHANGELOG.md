# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.1] - 2025-11-10

### Fixed
- **Critical: Multi-org team context on cached requests**: Fixed missing team context for multi-organization users on cached authentication requests.
  - `StytchVerifier._build_context_from_cache()` now correctly passes `organization_id` to `load_user_context()`
  - Ensures team validation works correctly for users who belong to multiple organizations
  - Resolves "No team selected" errors that occurred only on second and subsequent requests (after caching)
  - First request worked (loaded from Stytch with org context), but cached requests failed due to missing org parameter

### Impact
This fix is critical for multi-org deployments where users switch between organizations. Without this fix:
- First authentication request: ✅ Works (loads fresh from Stytch)
- Subsequent requests (cached): ❌ Returns wrong/missing team context
- Result: "No team selected. Please select a team to view sessions." errors

## [2.2.0] - 2025-11-08

### Fixed
- **Multi-organization user authentication with fallback**: Fixed authentication failures for users who belong to multiple organizations with different Stytch member IDs per organization.
  - `MongoClient.get_user()` now accepts an optional `organization_id` parameter for org-scoped lookups
  - When `organization_id` is provided, user lookup goes through `user_organization_memberships` collection to find the correct user
  - **Critical fix**: Falls back to direct `users.stytch_member_id` lookup when `user_organization_memberships` entry is missing, ensuring ALL users can authenticate
  - Resolves "mongo_user_id not available" errors and "Authentication failed" errors when switching between organizations
  - Handles data quality issues gracefully (missing org membership entries) without breaking authentication

### Changed
- **EntitlementsLoader**: Updated to pass `organization_id` to `get_user()` calls for multi-org support
- **User lookup flow**: Enhanced to support users with different Stytch member IDs across organizations

### Added
- **MongoClient**: New `_fallback_user_lookup()` helper method for backwards-compatible user lookups
- **Test coverage**: Added 5 new comprehensive tests for multi-org user scenarios:
  - Multi-org user lookup via organization memberships
  - Organization not found fallback
  - Missing org membership fallback
  - Single-org user backwards compatibility
  - Membership with missing user_id handling

### Impact
- Fixes authentication for ~20% of production users (18+ users with multi-org memberships)
- 100% backwards compatible - single-org users unaffected
- Graceful fallback ensures no breaking changes

## [2.0.1] - 2025-10-16

### Changed

#### Caching Improvements
- **Team Context**: `current_team_id` and `current_team_name` are no longer cached and are always loaded fresh from MongoDB on every request
  - Ensures team membership changes are reflected immediately
  - Fixes issue where team context could be stale for up to 5 minutes
- **User ID Caching**: `mongo_user_id` is now cached separately with 1-hour TTL for better performance
  - Faster user ID lookups while maintaining fresh team context

#### MongoDB Configuration
- **New Environment Variable**: `MONGODB_DB` - Explicitly specify MongoDB database name
  - Takes priority over database name in URI
  - Better integration with other repos using explicit db variables
  - Example: `MONGODB_URI=mongodb://localhost:27017` + `MONGODB_DB=myapp`
- **Backward Compatible**: Database name still extracted from URI if `MONGODB_DB` not set

### Fixed
- Fixed `if not db` checks to use `if db is None` for proper None checking (4 occurrences in `mongo_client.py`)
- Token verification cache now correctly excludes team context to ensure freshness

### Performance
- **Cached Requests**: Still <10ms with improved team freshness
- **Team Context Loading**: Always fresh from MongoDB (fast local query)
- **User ID Lookups**: Now cached for 1 hour (previously fetched on every request)

## [2.0.0] - 2025-10-08

### Breaking Changes
- **Removed `STYTCH_ORGANIZATION_ID` environment variable**: For multi-tenant applications, the organization ID is now always obtained from the authenticated user's session context. The `get_member_by_email()` method now requires `organization_id` as a parameter instead of reading it from config. This change ensures proper multi-tenant isolation.
  ```python
  # Before (v1.x):
  member = await stytch_verifier.get_member_by_email(email)

  # After (v2.0.0):
  member = await stytch_verifier.get_member_by_email(email, user.organization_id)
  ```

### Added

#### Entitlements System
- **MongoDB Integration**: Optional MongoDB support for organization entitlements and user team context
  - New optional dependency group: `pip install 'ayz-auth[mongodb]'`
  - Automatic graceful degradation if MongoDB is not configured
  - Read-only access to `organizations`, `users`, and `teams` collections

#### StytchContext Enhancements
- **Entitlements Fields** (all optional, None if MongoDB not configured):
  - `entitlements: List[str]` - Organization feature entitlements
  - `subscription_tier: str` - Subscription tier (free, standard, premium, enterprise)
  - `subscription_limits: Dict[str, int]` - Subscription limits (max_projects, max_users, etc.)

- **Team Context Fields**:
  - `current_team_id: str` - User's current team ID (MongoDB ObjectId as string)
  - `current_team_name: str` - User's current team name

- **MongoDB Identifiers**:
  - `mongo_user_id: str` - MongoDB user document ID
  - `mongo_organization_id: str` - MongoDB organization document ID

#### Authorization Decorators
- `@require_entitlement(entitlement)` - Require a specific entitlement
- `@require_any_entitlement(*entitlements)` - Require at least one entitlement
- `@require_all_entitlements(*entitlements)` - Require all specified entitlements

#### Caching Enhancements
- Organization entitlements caching with 1-hour TTL
- User context caching with 5-minute TTL
- Separate cache keys for organization and user data
- Enhanced token cache to include entitlements data

#### Configuration
- New optional environment variable: `STYTCH_MONGODB_URI`
- MongoDB URI can point to any database (default: `soulmates`)

### Changed
- **Version**: Bumped to 2.0.0 (major version for new features)
- **Package Description**: Updated to mention entitlements and MongoDB features
- **Development Status**: Upgraded from Alpha to Beta
- **Token Caching**: Now includes entitlements and team context data

### Performance
- **Cached Requests**: <10ms (Stytch validation + Redis entitlements/context lookups)
- **Uncached Requests**: <100ms (Stytch validation + MongoDB queries + Redis writes)
- **Parallel Loading**: Organization and user data loaded concurrently

### Backwards Compatibility
- ✅ **100% backwards compatible** with v1.x
- All new StytchContext fields default to `None`
- MongoDB dependencies are optional
- Existing implementations work without any changes
- No breaking changes to existing APIs

### Documentation
- Updated `README.md` with entitlements features
- Added `CHANGELOG.md` (this file)
- Added `docs/entitlements.md` - Detailed entitlements guide
- Added `docs/migration-v2.md` - Migration guide from v1.x
- Updated `example_usage.py` with entitlements examples

### Security
- MongoDB connections are read-only
- Graceful error handling prevents authentication bypass
- Entitlements failures log warnings but don't break authentication
- No sensitive data in error responses

## [1.0.0] - 2025-07-22

### Added
- Initial stable release
- Stytch B2B session token verification
- Redis caching for session tokens
- FastAPI middleware integration
- `verify_auth` dependency for authentication
- `verify_auth_optional` for optional authentication
- `create_auth_dependency` for custom auth requirements
- StytchContext model with session data
- Comprehensive error handling
- Type-safe configuration with Pydantic
- Full test coverage

### Documentation
- Complete README with usage examples
- API documentation
- Development setup guide

## [0.1.0] - 2025-06-18

### Added
- Initial alpha release
- Basic Stytch B2B integration
- Redis caching support
- FastAPI middleware

---

[2.0.0]: https://github.com/brandsoulmates/ayz-auth/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/brandsoulmates/ayz-auth/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/brandsoulmates/ayz-auth/releases/tag/v0.1.0
