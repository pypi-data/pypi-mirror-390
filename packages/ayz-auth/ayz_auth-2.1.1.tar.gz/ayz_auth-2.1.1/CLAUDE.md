# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ayz-auth` is a FastAPI middleware library for Stytch B2B authentication with Redis caching and optional MongoDB entitlements. Version 2.0.0 introduced organization entitlements, team context, and MongoDB integration while maintaining 100% backwards compatibility with v1.x.

**Key Architecture Pattern**: Multi-tier caching strategy with graceful fallback (Redis cache → Stytch API → optional MongoDB).

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ayz_auth

# Run specific test file
pytest tests/test_middleware.py

# Run tests in verbose mode
pytest -v
```

### Code Quality
```bash
# Format code (run both)
black src/ tests/
isort src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Building and Publishing
```bash
# Install dependencies
uv sync --dev

# Build package
python -m build

# See DEPLOYMENT.md for full publishing workflow
```

## Architecture Overview

### Core Authentication Flow
1. **Token Extraction** ([auth/token_extractor.py](src/ayz_auth/auth/token_extractor.py)) - Extracts Bearer token from Authorization header
2. **Token Verification** ([auth/stytch_verifier.py](src/ayz_auth/auth/stytch_verifier.py)) - Verifies token with Stytch API, checks Redis cache first
3. **Context Building** ([models/context.py](src/ayz_auth/models/context.py)) - Builds StytchContext with session data and optional entitlements
4. **Middleware** ([middleware.py](src/ayz_auth/middleware.py)) - FastAPI dependency that orchestrates the flow

### Entitlements System (v2.0.0+)
The entitlements system is **optional** and only activates when `STYTCH_MONGODB_URI` is configured:

- **Entitlements Loader** ([db/entitlements_loader.py](src/ayz_auth/db/entitlements_loader.py)) - Orchestrates loading of org entitlements and user context with caching
- **MongoDB Client** ([db/mongo_client.py](src/ayz_auth/db/mongo_client.py)) - Read-only access to three collections: `organizations`, `users`, `teams`
- **Authorization Decorators** ([decorators.py](src/ayz_auth/decorators.py)) - `require_entitlement`, `require_any_entitlement`, `require_all_entitlements`

### Caching Strategy
Two-tier caching with different TTLs:
- **Session tokens**: Cached in Redis until session expiration (managed by [cache/redis_client.py](src/ayz_auth/cache/redis_client.py))
- **Organization entitlements**: 1-hour TTL (changes infrequently)
- **User context**: 5-minute TTL (team changes may occur)

All cache keys use prefix from `STYTCH_CACHE_PREFIX` (default: `ayz_auth`).

### Configuration
All configuration via [utils/config.py](src/ayz_auth/utils/config.py) using pydantic-settings with `STYTCH_` prefix. Critical: If `mongodb_uri` is None, entitlements features are gracefully disabled.

### Error Handling
Custom exception hierarchy in [utils/exceptions.py](src/ayz_auth/utils/exceptions.py):
- `AuthenticationError` (base)
  - `TokenExtractionError` - Missing/invalid token format
  - `TokenVerificationError` - Token verification failed
  - `StytchAPIError` - Stytch service issues
  - `ConfigurationError` - Invalid configuration

## Key Design Patterns

### Backwards Compatibility
When adding features that depend on MongoDB:
1. Check if `user.entitlements is None` to detect if MongoDB is configured
2. Return appropriate error messages mentioning MongoDB configuration
3. Never break existing v1.x usage (authentication without MongoDB)

### Testing with External Dependencies
- **Stytch API**: Mock with `pytest-mock` (see [tests/test_middleware.py](tests/test_middleware.py))
- **Redis**: Use `fakeredis` library for in-memory testing
- **MongoDB**: Use `mongomock-motor` for async MongoDB mocking

### Logger Usage
Use structured logging from [utils/logger.py](src/ayz_auth/utils/logger.py):
```python
logger.info("Message", extra={"member_id": user.member_id})
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```
Sensitive data logging controlled by `STYTCH_LOG_SENSITIVE_DATA` (default: False).

## Common Development Tasks

### Adding a New Entitlement Decorator
1. Add function to [decorators.py](src/ayz_auth/decorators.py)
2. Export in [__init__.py](src/ayz_auth/__init__.py) `__all__` list
3. Add tests to [tests/test_entitlements.py](tests/test_entitlements.py)
4. Update docstring with usage examples

### Adding New StytchContext Fields
1. Update [models/context.py](src/ayz_auth/models/context.py) with Pydantic field
2. Update context building in [auth/stytch_verifier.py](src/ayz_auth/auth/stytch_verifier.py)
3. Add tests for the new field
4. If MongoDB-dependent, ensure it defaults to `None`

### Modifying Cache Behavior
1. Update [cache/redis_client.py](src/ayz_auth/cache/redis_client.py)
2. Test with `fakeredis` to ensure async operations work
3. Consider TTL implications (session cache expires with token, entitlements cache has fixed TTL)

## Project-Specific Guidelines

From [.clinerules](.clinerules):
- Consult [docs/](docs/) directory early and often
- When adding functionality, look for existing patterns to maintain consistency
- Update documentation after completing tasks
- Create simple tests for new functionality and run them before completion
- Use the logger utility instead of print/console.log
- Never use `write_to_file` for long files - prefer `replace_in_file`
- Follow DRY and Single Responsibility principles
- Files over 800 lines may overload context windows

## Important Files

- [README.md](README.md) - User-facing documentation
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Import patterns and examples for end users
- [DEPLOYMENT.md](DEPLOYMENT.md) - PyPI publishing workflow
- [docs/entitlements.md](docs/entitlements.md) - Deep dive on entitlements features
- [docs/migration-v2.md](docs/migration-v2.md) - v1.x to v2.0.0 migration guide
- [example_usage.py](example_usage.py) - Complete example application

## MongoDB Schema (v2.0.0+)

The system expects these MongoDB collections:

**organizations**:
```python
{
    "_id": ObjectId,
    "stytch_organization_id": str,
    "entitlements": List[str],  # e.g., ["foresight", "byod"]
    "subscription_tier": str,    # e.g., "free", "standard", "premium"
    "subscription_limits": Dict[str, int]
}
```

**users**:
```python
{
    "_id": ObjectId,
    "stytch_member_id": str,
    "current_team": ObjectId  # Reference to teams collection
}
```

**teams**:
```python
{
    "_id": ObjectId,
    "name": str
}
```
