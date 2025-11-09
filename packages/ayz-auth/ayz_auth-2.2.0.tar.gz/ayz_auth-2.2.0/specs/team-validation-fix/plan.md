# Implementation Plan: Team Context Validation for Multi-Organization Users

## Summary
Add team validation and auto-correction logic to `EntitlementsLoader._load_user_context()` to ensure `current_team_id` returned in `StytchContext` belongs to the current organization. When a stale team is detected, automatically find and return a valid team from the current organization, or return `None` if user has no teams.

## Success Criteria
- [ ] Multi-org users switching organizations receive valid `current_team_id` or `None`
- [ ] Stale team IDs are detected and auto-corrected without failing authentication
- [ ] Single-org users experience no behavior change or performance impact
- [ ] 400/403 error rates for multi-org users decrease to near-zero
- [ ] Authentication latency remains <100ms for uncached requests
- [ ] All existing tests continue to pass
- [ ] New tests cover all edge cases (team validation, auto-correction, fallback)

## Detailed Changes

### Component 1: MongoClient - Add Team Validation Method
**File:** `src/ayz_auth/db/mongo_client.py`
**Change Type:** New method
**Lines:** After line 226 (after `get_user_by_membership`)

**What changes:**
```python
async def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
    """
    Get team document by ObjectId.

    Args:
        team_id: Team ObjectId as string or ObjectId

    Returns:
        Team document if found, None otherwise
    """
    try:
        db = await self._get_client()
        if db is None:
            return None

        # Convert string to ObjectId if needed
        from bson import ObjectId
        if isinstance(team_id, str):
            team_id = ObjectId(team_id)

        team = await db.teams.find_one({"_id": team_id})

        if team:
            logger.debug(f"Found team: {team_id}")
        else:
            logger.debug(f"Team not found: {team_id}")

        return team

    except Exception as e:
        logger.warning(f"Failed to fetch team from MongoDB: {str(e)}")
        return None


async def find_user_team_in_organization(
    self, user_id: str, organization_id: str
) -> Optional[Dict[str, Any]]:
    """
    Find first active team membership for user in specified organization.

    Used to auto-correct stale current_team_id when user switches organizations.

    Args:
        user_id: MongoDB user ObjectId as string
        organization_id: Stytch organization ID

    Returns:
        Team document if found, None if user has no teams in this org
    """
    try:
        db = await self._get_client()
        if db is None:
            return None

        # Get MongoDB organization ID
        org_doc = await self.get_organization(organization_id)
        if not org_doc:
            logger.warning(f"Organization not found: {organization_id}")
            return None

        mongo_org_id = org_doc.get("_id")

        # Convert user_id to ObjectId
        from bson import ObjectId
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        # Find active team membership in this organization
        membership = await db.user_team_memberships.find_one({
            "user_id": user_id,
            "organization_id": mongo_org_id,
            "status": "active"
        })

        if not membership:
            logger.debug(
                f"No active team memberships found for user {user_id} "
                f"in organization {organization_id}"
            )
            return None

        team_id = membership.get("team_id")
        if not team_id:
            logger.warning(f"Team membership {membership.get('_id')} missing team_id")
            return None

        # Get team document
        team = await db.teams.find_one({"_id": team_id})

        if team:
            logger.info(
                f"Found valid team {team_id} for user {user_id} "
                f"in organization {organization_id}"
            )
        else:
            logger.warning(f"Team {team_id} not found despite active membership")

        return team

    except Exception as e:
        logger.warning(
            f"Failed to find user team in organization: {str(e)}",
            exc_info=True
        )
        return None
```

**Why:** Separates team lookup and validation concerns into reusable methods. `get_team()` fetches team by ID, `find_user_team_in_organization()` finds first valid team for auto-correction.

### Component 2: EntitlementsLoader - Add Team Validation Logic
**File:** `src/ayz_auth/db/entitlements_loader.py`
**Change Type:** Modify existing method
**Lines:** 246-283 (entire `_load_user_context` method)

**What changes:**
```python
async def _load_user_context(
    self,
    stytch_member_id: str,
    stytch_org_id: str,
    redis_client: RedisClient,
    mongo_client: MongoClient,
) -> Optional[Dict[str, Any]]:
    """
    Load user-specific context from MongoDB with team validation.

    Ensures current_team_id belongs to current organization. If team is stale
    (belongs to different org), auto-corrects to valid team or None.
    """
    # Step 1: Get user via org membership lookup (v2.1.1)
    user_doc = await mongo_client.get_user_by_membership(
        stytch_member_id, stytch_org_id
    )

    if not user_doc:
        logger.debug(
            f"User not found in MongoDB for member: {stytch_member_id} "
            f"in org: {stytch_org_id}"
        )
        return None

    user_id = user_doc.get("_id")
    current_team_id = user_doc.get("current_team_id")

    # Step 2: VALIDATE team belongs to current organization
    validated_team_id = None
    team_name = None

    if current_team_id:
        # Get team document to check organization
        team_doc = await mongo_client.get_team(str(current_team_id))

        if team_doc:
            team_org_id = team_doc.get("organization_id")

            # Get MongoDB org ID for comparison
            org_doc = await mongo_client.get_organization(stytch_org_id)
            mongo_org_id = org_doc.get("_id") if org_doc else None

            if team_org_id == mongo_org_id:
                # Team belongs to current organization ✅
                validated_team_id = current_team_id
                team_name = team_doc.get("name")
                logger.debug(
                    f"Team {current_team_id} validated for org {stytch_org_id}"
                )
            else:
                # Team belongs to DIFFERENT organization ❌
                logger.warning(
                    f"STALE_TEAM_DETECTED: User {user_id} has current_team_id "
                    f"{current_team_id} from different organization. "
                    f"Team org: {team_org_id}, Current org: {mongo_org_id}. "
                    f"Will auto-correct to valid team."
                )

                # Step 3: AUTO-CORRECT to valid team in current organization
                valid_team = await mongo_client.find_user_team_in_organization(
                    str(user_id), stytch_org_id
                )

                if valid_team:
                    validated_team_id = valid_team.get("_id")
                    team_name = valid_team.get("name")
                    logger.info(
                        f"Auto-corrected team for user {user_id}: "
                        f"{current_team_id} → {validated_team_id}"
                    )
                else:
                    logger.info(
                        f"User {user_id} has no teams in org {stytch_org_id}. "
                        f"Setting current_team_id = None"
                    )
        else:
            # Team document not found (deleted?)
            logger.warning(
                f"Team {current_team_id} not found in MongoDB. "
                f"Will attempt to find valid team."
            )

            # Try to find any valid team
            valid_team = await mongo_client.find_user_team_in_organization(
                str(user_id), stytch_org_id
            )

            if valid_team:
                validated_team_id = valid_team.get("_id")
                team_name = valid_team.get("name")
    else:
        # No current_team_id set - try to find one
        logger.debug(f"User {user_id} has no current_team_id set")

        valid_team = await mongo_client.find_user_team_in_organization(
            str(user_id), stytch_org_id
        )

        if valid_team:
            validated_team_id = valid_team.get("_id")
            team_name = valid_team.get("name")
            logger.info(
                f"Set initial team for user {user_id}: {validated_team_id}"
            )

    # Step 4: Build user context with validated team
    user_context = {
        "current_team_id": str(validated_team_id) if validated_team_id else None,
        "current_team_name": team_name,
        "mongo_user_id": str(user_id) if user_id else None,
    }

    # Note: We do NOT cache this because team validation must run every time
    # to ensure freshness across org switches

    return user_context
```

**Why:**
- Validates team belongs to current organization before returning
- Auto-corrects stale team IDs without failing authentication
- Provides clear logging for debugging multi-org issues
- Handles edge cases gracefully (team deleted, user has no teams)

**Impact on Performance:**
- Adds 2-3 MongoDB queries per authentication (team lookup + validation)
- Estimated latency: +30-50ms
- Acceptable tradeoff for correctness

### Component 3: Update Logger Imports
**File:** `src/ayz_auth/db/entitlements_loader.py`
**Change Type:** Ensure logger is imported
**Lines:** Top of file

**What changes:**
```python
from ..utils.logger import logger
```

**Why:** New logging statements require logger import.

## API Changes
**No external API changes.** All changes are internal to ayz-auth package. The `StytchContext` model remains unchanged - we're just ensuring `current_team_id` is validated.

## Database Changes
**No schema changes required.** All necessary collections already exist:
- `teams` (has `organization_id` field)
- `user_team_memberships` (has `user_id`, `team_id`, `organization_id`, `status`)
- `user_organization_memberships` (v2.1.1)
- `users` (unchanged)

## Testing Strategy

### Unit Tests

**File:** `tests/test_mongo_client.py`

#### Test: `test_get_team_success`
```python
@pytest.mark.asyncio
async def test_get_team_success(mock_mongo_client, mock_settings_with_mongodb):
    """Test get_team returns team document when found."""
    team_data = {
        "_id": "team_mongo_id_123",
        "name": "Marketing Team",
        "organization_id": "org_mongo_id_456"
    }

    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=team_data)
    mock_db.teams = mock_collection

    with patch.object(mock_mongo_client, "_get_client", return_value=mock_db):
        result = await mock_mongo_client.get_team("team_mongo_id_123")

        assert result == team_data
        mock_collection.find_one.assert_called_once()
```

#### Test: `test_get_team_not_found`
```python
@pytest.mark.asyncio
async def test_get_team_not_found(mock_mongo_client, mock_settings_with_mongodb):
    """Test get_team returns None when team doesn't exist."""
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.teams = mock_collection

    with patch.object(mock_mongo_client, "_get_client", return_value=mock_db):
        result = await mock_mongo_client.get_team("nonexistent_team")

        assert result is None
```

#### Test: `test_find_user_team_in_organization_success`
```python
@pytest.mark.asyncio
async def test_find_user_team_in_organization_success(
    mock_mongo_client, mock_settings_with_mongodb
):
    """Test finding user's team in specific organization."""
    org_data = {"_id": "org_mongo_id", "stytch_org_id": "organization-live-abc123"}
    membership_data = {
        "_id": "membership_id",
        "user_id": "user_mongo_id",
        "team_id": "team_mongo_id",
        "organization_id": "org_mongo_id",
        "status": "active"
    }
    team_data = {
        "_id": "team_mongo_id",
        "name": "Marketing Team",
        "organization_id": "org_mongo_id"
    }

    mock_db = MagicMock()
    mock_db.organizations.find_one = AsyncMock(return_value=org_data)
    mock_db.user_team_memberships.find_one = AsyncMock(return_value=membership_data)
    mock_db.teams.find_one = AsyncMock(return_value=team_data)

    with patch.object(mock_mongo_client, "_get_client", return_value=mock_db):
        result = await mock_mongo_client.find_user_team_in_organization(
            "user_mongo_id", "organization-live-abc123"
        )

        assert result == team_data
```

#### Test: `test_find_user_team_no_memberships`
```python
@pytest.mark.asyncio
async def test_find_user_team_no_memberships(
    mock_mongo_client, mock_settings_with_mongodb
):
    """Test returns None when user has no team memberships in org."""
    org_data = {"_id": "org_mongo_id", "stytch_org_id": "organization-live-abc123"}

    mock_db = MagicMock()
    mock_db.organizations.find_one = AsyncMock(return_value=org_data)
    mock_db.user_team_memberships.find_one = AsyncMock(return_value=None)

    with patch.object(mock_mongo_client, "_get_client", return_value=mock_db):
        result = await mock_mongo_client.find_user_team_in_organization(
            "user_mongo_id", "organization-live-abc123"
        )

        assert result is None
```

**File:** `tests/test_entitlements_loader.py`

#### Test: `test_load_user_context_validates_team_in_current_org`
```python
@pytest.mark.asyncio
async def test_load_user_context_validates_team_in_current_org(
    mock_entitlements_loader
):
    """Test team validation - team belongs to current org."""
    # User document with current_team_id
    user_doc = {
        "_id": "user_mongo_id",
        "current_team_id": "team_mongo_id_123"
    }

    # Team belongs to current organization
    team_doc = {
        "_id": "team_mongo_id_123",
        "name": "Marketing Team",
        "organization_id": "org_mongo_id_current"
    }

    # Current organization
    org_doc = {
        "_id": "org_mongo_id_current",
        "stytch_org_id": "organization-live-current"
    }

    mock_mongo_client = AsyncMock()
    mock_mongo_client.get_user_by_membership = AsyncMock(return_value=user_doc)
    mock_mongo_client.get_team = AsyncMock(return_value=team_doc)
    mock_mongo_client.get_organization = AsyncMock(return_value=org_doc)

    result = await mock_entitlements_loader._load_user_context(
        "member-live-xyz",
        "organization-live-current",
        mock_redis_client,
        mock_mongo_client
    )

    # Should return original team since it's valid
    assert result["current_team_id"] == "team_mongo_id_123"
    assert result["current_team_name"] == "Marketing Team"
```

#### Test: `test_load_user_context_auto_corrects_stale_team`
```python
@pytest.mark.asyncio
async def test_load_user_context_auto_corrects_stale_team(
    mock_entitlements_loader
):
    """Test auto-correction when team belongs to different org."""
    # User document with stale team from different org
    user_doc = {
        "_id": "user_mongo_id",
        "current_team_id": "team_mongo_id_stale"
    }

    # Stale team belongs to DIFFERENT organization
    stale_team_doc = {
        "_id": "team_mongo_id_stale",
        "name": "Old Team",
        "organization_id": "org_mongo_id_different"  # ❌ Different org
    }

    # Current organization
    current_org_doc = {
        "_id": "org_mongo_id_current",
        "stytch_org_id": "organization-live-current"
    }

    # Valid team in current organization
    valid_team_doc = {
        "_id": "team_mongo_id_valid",
        "name": "Current Team",
        "organization_id": "org_mongo_id_current"
    }

    mock_mongo_client = AsyncMock()
    mock_mongo_client.get_user_by_membership = AsyncMock(return_value=user_doc)
    mock_mongo_client.get_team = AsyncMock(return_value=stale_team_doc)
    mock_mongo_client.get_organization = AsyncMock(return_value=current_org_doc)
    mock_mongo_client.find_user_team_in_organization = AsyncMock(
        return_value=valid_team_doc
    )

    result = await mock_entitlements_loader._load_user_context(
        "member-live-xyz",
        "organization-live-current",
        mock_redis_client,
        mock_mongo_client
    )

    # Should return auto-corrected team
    assert result["current_team_id"] == "team_mongo_id_valid"
    assert result["current_team_name"] == "Current Team"

    # Verify auto-correction was attempted
    mock_mongo_client.find_user_team_in_organization.assert_called_once_with(
        "user_mongo_id", "organization-live-current"
    )
```

#### Test: `test_load_user_context_returns_none_when_no_teams`
```python
@pytest.mark.asyncio
async def test_load_user_context_returns_none_when_no_teams(
    mock_entitlements_loader
):
    """Test returns None for current_team_id when user has no teams in org."""
    user_doc = {
        "_id": "user_mongo_id",
        "current_team_id": "team_mongo_id_stale"
    }

    stale_team_doc = {
        "_id": "team_mongo_id_stale",
        "organization_id": "org_mongo_id_different"
    }

    current_org_doc = {
        "_id": "org_mongo_id_current",
        "stytch_org_id": "organization-live-current"
    }

    mock_mongo_client = AsyncMock()
    mock_mongo_client.get_user_by_membership = AsyncMock(return_value=user_doc)
    mock_mongo_client.get_team = AsyncMock(return_value=stale_team_doc)
    mock_mongo_client.get_organization = AsyncMock(return_value=current_org_doc)
    mock_mongo_client.find_user_team_in_organization = AsyncMock(return_value=None)

    result = await mock_entitlements_loader._load_user_context(
        "member-live-xyz",
        "organization-live-current",
        mock_redis_client,
        mock_mongo_client
    )

    # Should return None when user has no teams in current org
    assert result["current_team_id"] is None
    assert result["current_team_name"] is None
```

### Integration Tests

#### Test: Multi-org user switches organizations
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_multi_org_user_switches_organizations():
    """
    End-to-end test: User with memberships in Org A and Org B
    switches from Org A to Org B and receives correct team context.
    """
    # Setup: Create user with teams in both organizations
    # Authenticate with Org A token → Should get Team A
    # Authenticate with Org B token → Should get Team B (not Team A)
    pass  # Requires real MongoDB instance
```

### Manual Verification

#### Step 1: Test with Multi-Org User (e.g., ptruitt@ayzenberg.com)
1. Log into Ayzenberg organization
2. Select a team (note team ID from browser DevTools)
3. Log out
4. Log into Mercury organization
5. Make API request to `/api/sessions`
6. Verify: `StytchContext.current_team_id` is either:
   - A valid team ID from Mercury org, OR
   - `None` (if user has no teams in Mercury)
7. Verify: NO 400/403 errors

#### Step 2: Check Logs
1. Search Cloud Logging for "STALE_TEAM_DETECTED"
2. Verify auto-correction messages appear
3. Verify no authentication failures

#### Step 3: Performance Check
1. Measure authentication latency before/after
2. Target: <100ms uncached requests
3. Monitor for any degradation

## Rollback Plan

### If Issues Arise
1. **Immediate:** Revert to v2.1.1 by updating `requirements.txt`:
   ```
   ayz-auth[mongodb]==2.1.1
   ```
2. **Redeploy:** Push change to trigger Cloud Run deployment
3. **Monitor:** Verify error rates return to baseline

### Safe Rollback Points
- Version v2.1.1 is stable and published on PyPI
- No database migrations required
- No API contract changes

## Dependencies & Risks

### Blocked By
- None (all required collections already exist)

### Risks

#### Risk 1: Performance Impact
**Likelihood:** Medium
**Impact:** Medium
**Description:** Additional MongoDB queries may increase latency
**Mitigation:**
- Index on `user_team_memberships(user_id, organization_id, status)`
- Monitor P95 latency in production
- Consider caching validated teams (future optimization)

#### Risk 2: MongoDB Data Quality
**Likelihood:** Low
**Impact:** High
**Description:** Missing or inconsistent data in `user_team_memberships`
**Mitigation:**
- Graceful fallback to `None` when no teams found
- Detailed logging for debugging
- Don't fail authentication on validation errors

#### Risk 3: Auto-Correction Logic Bugs
**Likelihood:** Low
**Impact:** Medium
**Description:** Wrong team selected during auto-correction
**Mitigation:**
- Comprehensive unit tests covering edge cases
- Log all auto-corrections for audit
- Allow users to manually select team in frontend

### Dependencies
- MongoDB collections must have proper indexes
- Redis available for token caching
- Stytch API for token validation

## Version and Release

### Version Number
**v2.2.0** - Minor version bump (new functionality, backwards compatible)

### Release Notes
```markdown
## [2.2.0] - 2025-11-09

### Fixed
- **Multi-organization team context validation**: Fixed 400/403 errors for users switching between organizations
  - Added team validation to ensure `current_team_id` belongs to current organization
  - Automatically corrects stale team IDs from different organizations
  - Returns `None` for `current_team_id` when user has no teams in current organization
  - Resolves "TEAM_ACCESS_DENIED" errors in backend services

### Added
- **MongoClient**:
  - `get_team()` - Fetch team document by ObjectId
  - `find_user_team_in_organization()` - Find user's active team in specific organization
- **Enhanced logging**: Detailed warnings for stale team detection and auto-correction

### Changed
- **EntitlementsLoader**: `_load_user_context()` now validates and auto-corrects team context

### Impact
- Fixes authentication for 100% of multi-org users experiencing team validation errors
- Single-org users unaffected
- Adds ~30-50ms latency for team validation (acceptable tradeoff)
```

## Post-Deployment Checklist
- [ ] Monitor Cloud Logging for "STALE_TEAM_DETECTED" messages
- [ ] Track 400/403 error rates (should decrease significantly)
- [ ] Verify authentication latency remains acceptable (<100ms P95)
- [ ] Test with known multi-org users (ptruitt@ayzenberg.com, etc.)
- [ ] Collect user feedback on team switching experience
- [ ] Update documentation if needed
