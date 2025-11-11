# Research: Team Context Validation for Multi-Organization Users

## Objective
Fix authentication failures for multi-organization users by ensuring `current_team_id` returned in `StytchContext` is validated against the current organization context. Users switching between organizations currently receive stale team IDs from different organizations, causing 400/403 errors in backend services.

## Problem Statement

### Current Behavior (v2.1.1)
When a user belongs to multiple organizations (e.g., Ayzenberg + Mercury):
1. User logs into **Org A** (Ayzenberg), selects **Team X**
2. MongoDB `users.current_team_id` = Team X ObjectId
3. User logs out, then logs into **Org B** (Mercury)
4. MongoDB `users.current_team_id` still = Team X (STALE!)
5. ayz-auth returns `current_team_id = Team X` in `StytchContext`
6. Backend validates: "Does user have membership in Team X within Org B?"
7. Validation FAILS → 400/403 error

### Root Cause
The `users.current_team_id` field stores a **single global value** across all organizations. When users switch organizations, this field becomes stale because it references a team from a different organization context.

## System Analysis

### Relevant Components

#### 1. MongoDB Collections

**`users` Collection**
```python
# src/ayz_auth/db/mongo_client.py (lines 132-226)
{
    "_id": ObjectId,
    "email": str,
    "stytch_member_id": str,  # May be stale for multi-org users
    "current_team_id": ObjectId,  # ❌ SINGLE global value - root of the problem
    # ... other fields
}
```

**`user_organization_memberships` Collection** (v2.1.1 addition)
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,  # Reference to users._id
    "organization_id": ObjectId,  # Reference to organizations._id
    "stytch_member_id": str,  # Org-specific member ID (CURRENT)
    "status": str,  # "active", "inactive"
}
```

**`user_team_memberships` Collection**
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,  # Reference to users._id
    "team_id": ObjectId,  # Reference to teams._id
    "organization_id": ObjectId,  # Reference to organizations._id
    "status": str,  # "active", "inactive"
}
```

**`teams` Collection**
```python
{
    "_id": ObjectId,
    "name": str,
    "organization_id": ObjectId,  # Team belongs to ONE organization
}
```

#### 2. MongoClient User Lookup (v2.1.1)

**File:** `src/ayz_auth/db/mongo_client.py` (lines 147-222)

**Current Implementation:**
```python
async def get_user_by_membership(
    self, stytch_member_id: str, stytch_org_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get user data by looking up through user_organization_memberships collection.

    Lookup flow:
    1. Query user_organization_memberships for active membership by stytch_member_id
    2. Extract user_id from the membership
    3. Query users collection by _id
    """
    # Step 1: Find active membership
    membership_query = {
        "stytch_member_id": stytch_member_id,
        "status": "active",
    }

    if stytch_org_id:
        org_doc = await self.get_organization(stytch_org_id)
        if org_doc and org_doc.get("_id"):
            membership_query["organization_id"] = org_doc["_id"]

    membership = await db.user_organization_memberships.find_one(membership_query)

    if not membership:
        return None

    user_id = membership.get("user_id")

    # Step 2: Get user document
    user = await db.users.find_one({"_id": user_id})

    # ❌ Returns user with potentially STALE current_team_id
    return user
```

**Key Finding:** This method correctly finds the user via org membership, but returns `user.current_team_id` WITHOUT validating it belongs to the current organization.

#### 3. EntitlementsLoader Team Context Loading

**File:** `src/ayz_auth/db/entitlements_loader.py` (lines 246-283)

**Current Implementation:**
```python
async def _load_user_context(
    self,
    stytch_member_id: str,
    stytch_org_id: str,
    redis_client: RedisClient,
    mongo_client: MongoClient,
) -> Optional[Dict[str, Any]]:
    """Load user-specific context from MongoDB."""

    # Step 1: Get user via org membership lookup (v2.1.1)
    user_doc = await mongo_client.get_user_by_membership(
        stytch_member_id, stytch_org_id
    )

    if not user_doc:
        return None

    user_id = user_doc.get("_id")
    current_team_id = user_doc.get("current_team_id")  # ❌ May be from different org

    user_context = {
        "current_team_id": str(current_team_id) if current_team_id else None,
        "current_team_name": None,
        "mongo_user_id": str(user_id) if user_id else None,
    }

    # Step 2: Load team name if team ID present
    if current_team_id:
        team_name = await self._load_team_name(current_team_id)
        user_context["current_team_name"] = team_name

    # ❌ No validation that current_team_id belongs to current organization
    # ❌ No check if user has active membership in this team
    # ❌ No auto-correction when team_id is stale

    return user_context
```

**Key Finding:** The code loads team name but never validates the team belongs to the current organization.

#### 4. Team Validation in Backend Services

**File:** `app/core/team_validation.py` (lines 14-35)
**Context:** soulmates-app-backend repository

```python
async def validate_user_team_access(
    user_id: PyObjectId,
    team_id: str,
    db
) -> bool:
    """
    Validate that user has active membership in specified team.

    This is where 403 errors originate!
    """
    team_object_id = PyObjectId(team_id)

    # Query user_team_memberships collection
    memberships_collection = db["user_team_memberships"]
    membership = await memberships_collection.find_one({
        "user_id": user_id,
        "team_id": team_object_id,
        "status": "active"
    })

    is_valid = membership is not None

    if not is_valid:
        logger.warning(
            f"TEAM_ACCESS_DENIED: user {user_id} attempted access to team {team_id}"
        )

    return is_valid
```

**Key Finding:** Backend correctly validates team membership, but ayz-auth provides stale team_id, causing legitimate requests to fail.

## Data Flow

### Current Flow (v2.1.1 - BROKEN)

```
1. User switches from Org A to Org B
   MongoDB: users.current_team_id = Team X (from Org A) ❌

2. Frontend makes request to backend
   Headers: Authorization: Bearer <jwt_with_org_b_context>

3. ayz-auth validates token
   ✅ Stytch validates JWT successfully
   ✅ Extracts organization_id = "Org B" from token
   ✅ Looks up user via user_organization_memberships (v2.1.1 fix)
   ❌ Returns user.current_team_id = Team X (from Org A)

4. Backend receives StytchContext
   context.organization_id = "Org B" ✅
   context.current_team_id = "Team X" ❌ (belongs to Org A)

5. Backend validates team access
   Query: user_team_memberships.find({
     user_id: <user>,
     team_id: Team X,
     status: "active"
   })
   Result: None (user has NO membership in Team X within Org B context)

6. Validation fails → 403 Forbidden error
```

### Required Flow (FIXED)

```
1. User switches from Org A to Org B
   MongoDB: users.current_team_id = Team X (from Org A) ❌ (still stale)

2. Frontend makes request to backend
   Headers: Authorization: Bearer <jwt_with_org_b_context>

3. ayz-auth validates token
   ✅ Stytch validates JWT successfully
   ✅ Extracts organization_id = "Org B" from token
   ✅ Looks up user via user_organization_memberships
   ✅ Gets user.current_team_id = Team X

   🆕 VALIDATE team belongs to current organization:
   - Query teams collection: teams.find({ _id: Team X })
   - Check: team.organization_id == mongo_org_id (Org B)?
   - Result: NO → Team X belongs to Org A

   🆕 FIND valid team for current organization:
   - Query user_team_memberships for active membership in Org B
   - Get first active team membership
   - Update current_team_id to valid team in Org B
   - OR set current_team_id = None if no team memberships

4. Backend receives StytchContext
   context.organization_id = "Org B" ✅
   context.current_team_id = "Team Y" ✅ (valid team in Org B)
   OR context.current_team_id = None (user has no teams in Org B)

5. Backend validates team access
   Query: user_team_memberships.find({
     user_id: <user>,
     team_id: Team Y,  # Valid team in Org B
     status: "active"
   })
   Result: Found! ✅

6. Request succeeds ✅
```

## Current Limitations

### v2.1.1 Fixes User Lookup But Not Team Validation
- ✅ **Fixed:** User lookup now uses `user_organization_memberships` (correct member ID)
- ❌ **Not Fixed:** `current_team_id` validation against current organization
- ❌ **Not Fixed:** Auto-correction of stale team IDs
- ❌ **Not Fixed:** Fallback to valid team when stale team detected

### Performance Implications
- Current: 1 DB query to get user
- Required: 3 DB queries total:
  1. Get user via org membership (existing)
  2. Validate team belongs to org (new)
  3. Find valid team if current is stale (new, conditional)

### Caching Considerations
- Current: User context cached for 5 minutes (v2.0.1)
- Impact: Team validation must run on every auth check (can't cache stale team)
- Solution: Cache validation result separately with org-specific key

## External Dependencies

### MongoDB Collections Required
- `users` (existing)
- `user_organization_memberships` (existing, v2.1.1)
- `teams` (existing)
- `user_team_memberships` (existing)
- `organizations` (existing)

### Stytch API
- No changes required
- Organization ID comes from JWT token claims

### Redis Caching
- File: `src/ayz_auth/cache/redis_client.py`
- Current cache keys: `user_context:{stytch_member_id}`
- Required: Org-scoped caching (future optimization)

## Key Findings

### 1. The Real Problem
v2.1.1 fixed HOW we look up users but didn't fix WHAT we return. The `current_team_id` field in the `users` collection is inherently flawed for multi-org scenarios because it's a single global value.

### 2. Required Changes
We need to add **team validation and auto-correction** in `EntitlementsLoader._load_user_context()`:
- Validate `current_team_id` belongs to current organization
- Auto-correct to a valid team if stale
- Set to `None` if user has no teams in current org

### 3. MongoDB Schema Insight
The `user_team_memberships` collection already has `organization_id` field! We can use this to find valid teams for the current organization.

### 4. Backwards Compatibility
Single-org users will be unaffected:
- Their `current_team_id` will always be valid (only one org)
- Validation will pass immediately
- No performance impact

### 5. Production Impact
Current errors in logs:
```
mongo_user_id not available for member member-live-025c296a-927b-4ebb-803e-2aed7946a1fd
```

This suggests user lookup is failing, which may be a separate issue from team validation. We should investigate if `user_organization_memberships` is properly populated.

## Questions for Implementation

1. **What if user has NO teams in current organization?**
   - Return `current_team_id = None`
   - Backend should handle this gracefully

2. **Which team should we auto-select if multiple teams exist?**
   - Option A: First active team (alphabetically by name)
   - Option B: Most recently accessed team (requires tracking)
   - **Recommendation:** Option A for simplicity

3. **Should we update `users.current_team_id` in MongoDB?**
   - No - it's a global field that will break on next org switch
   - Yes - but only as a performance hint (not source of truth)
   - **Recommendation:** No, don't update MongoDB (minimize side effects)

4. **How to handle validation failures?**
   - Log warning with detailed context
   - Return corrected team_id in StytchContext
   - Don't fail authentication (graceful degradation)

## Testing Requirements

### Unit Tests Needed
1. Team belongs to current organization → use as-is
2. Team belongs to different organization → find valid team
3. User has no teams in current organization → return None
4. User has multiple teams in current org → pick first active
5. Team validation query fails → graceful fallback

### Integration Tests Needed
1. Multi-org user switches orgs → receives correct team
2. Single-org user → unaffected by validation
3. New user with no teams → handles gracefully
4. Performance: Validation adds <50ms latency

### Production Validation
1. Monitor logs for "team validation" warnings
2. Track 400/403 error rates (should decrease)
3. Monitor authentication latency (should remain <100ms uncached)

## Related Files
- `/Users/mmarina/Projects/ayz-auth/src/ayz_auth/db/mongo_client.py` (lines 132-226)
- `/Users/mmarina/Projects/ayz-auth/src/ayz_auth/db/entitlements_loader.py` (lines 114-283)
- `/Users/mmarina/Projects/ayz-auth/tests/test_mongo_client.py`
- `/Users/mmarina/Projects/ayz-auth/tests/test_entitlements_loader.py`

## Next Steps
1. Create detailed implementation plan (plan.md)
2. Implement team validation logic in EntitlementsLoader
3. Add comprehensive tests
4. Verify in production with multi-org test users
