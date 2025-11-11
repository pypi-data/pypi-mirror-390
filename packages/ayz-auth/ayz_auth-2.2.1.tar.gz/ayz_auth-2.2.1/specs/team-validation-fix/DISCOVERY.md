# Discovery: Team Validation Already Implemented

## Status: ✅ Feature Already Exists

## Key Finding

The team context validation fix we planned to implement **already exists** in the codebase! However, users are still experiencing authentication errors, indicating a different root cause.

## What Already Exists (v2.1.1)

### 1. Organization-Scoped User Lookup
**File:** `src/ayz_auth/db/mongo_client.py` (lines 147-248)
- `get_user_by_membership()` - Looks up users via `user_organization_memberships` collection
- Uses org-specific `stytch_member_id` (not the stale `users.stytch_member_id`)

### 2. Team Validation Logic
**File:** `src/ayz_auth/db/entitlements_loader.py` (lines 138-166)
- `_validate_team_belongs_to_org()` - Validates team belongs to current organization
- `_get_first_team_in_org()` - Finds valid team in current organization
- `_update_user_current_team()` - Auto-corrects stale MongoDB value

### 3. Organization-Scoped Caching
**File:** `src/ayz_auth/cache/redis_client.py`
- Cache keys include org_id: `user_context:{member_id}:org:{org_id}`
- Prevents cache pollution across organizations

## The Real Problem

Despite having all the validation logic, users are still getting errors:

```
mongo_user_id not available for member member-live-025c296a-927b-4ebb-803e-2aed7946a1fd
```

This error occurs BEFORE team validation runs. The issue is that `get_user_by_membership()` returns `None`, which means:

**Root Cause:** The `user_organization_memberships` collection is missing entries for affected users.

## Data Quality Issue

The `user_organization_memberships` collection is not properly populated for all users. This is likely because:

1. **Historical Users**: Users created before this collection existed
2. **Sync Issue**: Stytch → MongoDB sync is incomplete
3. **Multi-Org Users**: Users with memberships in multiple orgs may have missing entries

## Required Fix

Instead of implementing new code, we need to:

1. **Add Fallback Logic**: When `get_user_by_membership()` returns `None`, fall back to:
   - Direct `users.stytch_member_id` lookup (already exists as deprecated method)
   - This ensures ALL users can authenticate, even with incomplete data

2. **Data Migration**: Backfill `user_organization_memberships` collection (separate task)

3. **Monitoring**: Add detailed logging to identify which users are missing org memberships

## Implementation Strategy

The `get_user()` method in `mongo_client.py` already exists and does direct lookup as a deprecated fallback. We just need to ensure `EntitlementsLoader` uses it when `get_user_by_membership()` fails.

**Current flow:**
```python
user_doc = await mongo_client.get_user_by_membership(stytch_member_id, stytch_org_id)
if not user_doc:
    return None  # ❌ Authentication fails
```

**Required flow:**
```python
user_doc = await mongo_client.get_user_by_membership(stytch_member_id, stytch_org_id)
if not user_doc:
    # Fallback to direct lookup for users missing org membership
    user_doc = await mongo_client.get_user(stytch_member_id)
    if not user_doc:
        return None
    logger.warning(
        f"User {stytch_member_id} found via fallback lookup. "
        f"Missing entry in user_organization_memberships for org {stytch_org_id}"
    )
```

This is exactly what our v2.2.0 branch (fix/multi-org-team-context-validation) implements!

## Implementation Comparison

### v2.1.1 (main branch) - Two Separate Methods
```python
# DEPRECATED method - direct lookup
async def get_user(self, stytch_member_id: str) -> Optional[Dict[str, Any]]:
    user = await db.users.find_one({"stytch_member_id": stytch_member_id})
    return user

# NEW method - org membership lookup
async def get_user_by_membership(
    self, stytch_member_id: str, stytch_org_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    membership = await db.user_organization_memberships.find_one({...})
    if not membership:
        return None  # ❌ NO FALLBACK - authentication fails
    user = await db.users.find_one({"_id": membership["user_id"]})
    return user
```

**Problem**: `get_user_by_membership()` has **no fallback** when org membership is missing. Returns `None`, causing auth to fail.

### v2.2.0 (fix/multi-org-team-context-validation) - Unified Method with Fallback
```python
async def get_user(
    self,
    stytch_member_id: str,
    organization_id: Optional[str] = None  # NEW parameter
) -> Optional[Dict[str, Any]]:
    if organization_id:
        # Try org membership lookup first
        org_membership = await db.user_organization_memberships.find_one({...})
        if org_membership:
            user = await db.users.find_one({"_id": org_membership["user_id"]})
            if user:
                return user

        # ✅ FALLBACK when org membership missing
        logger.warning(f"No org membership found, falling back to direct lookup")

    # Fallback: direct user lookup (backwards compatible)
    return await self._fallback_user_lookup(db, stytch_member_id)
```

**Benefit**: Graceful fallback ensures ALL users can authenticate, even with incomplete `user_organization_memberships` data.

## Recommendation

**Merge the existing fix/multi-org-team-context-validation branch** which already has:
1. ✅ Fallback logic when org membership not found
2. ✅ Better error logging
3. ✅ Comprehensive tests
4. ✅ Documentation
5. ✅ Cleaner API design (single unified method vs two separate methods)

This is commit `67fe3fd` which was never merged to main.

## Next Steps

1. Review the `fix/multi-org-team-context-validation` branch
2. Merge to main if tests pass
3. Publish as v2.2.0
4. Separately: Investigate and fix data quality in `user_organization_memberships`
