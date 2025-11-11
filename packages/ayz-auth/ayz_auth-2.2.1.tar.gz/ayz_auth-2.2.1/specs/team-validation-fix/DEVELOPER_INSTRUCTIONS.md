# Developer Instructions: ayz-auth v2.2.0 Upgrade

## Overview
ayz-auth v2.2.0 fixes critical authentication issues for multi-organization users. This document provides instructions for backend microservice developers on how to upgrade and what (if anything) needs to change.

## TL;DR - What Backend Developers Need to Know

**Good News**: The v2.2.0 upgrade is 100% backwards compatible. No code changes are required in backend microservices.

However, you should be aware of:
1. How the fix works (fallback logic for missing org memberships)
2. New logging to monitor (fallback warnings)
3. Optional: How to take advantage of improved multi-org support

---

## Upgrade Steps

### 1. Update `requirements.txt`
```bash
# Update from v2.1.1 to v2.2.0
# From:
ayz-auth[mongodb]==2.1.1

# To:
ayz-auth[mongodb]==2.2.0
```

### 2. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 3. Restart Services
```bash
# No configuration changes required
# Simply restart your services after deployment
```

---

## What Changed in v2.2.0

### The Problem (v2.1.1)
Multi-org users were getting authentication errors:
```
mongo_user_id not available for member member-live-025c296a-927b-4ebb-803e-2aed7946a1fd
```

**Root Cause**: The `user_organization_memberships` collection is incomplete (~20% of users missing entries). When v2.1.1's `get_user_by_membership()` returns `None`, authentication fails immediately.

### The Fix (v2.2.0)
Added **fallback logic** in `MongoClient.get_user()`:

```python
# v2.2.0 flow
async def get_user(self, stytch_member_id: str, organization_id: Optional[str] = None):
    if organization_id:
        # 1. Try org membership lookup (handles multi-org users correctly)
        org_membership = await db.user_organization_memberships.find_one({...})
        if org_membership:
            return await db.users.find_one({"_id": org_membership["user_id"]})

        # 2. FALLBACK: User found via direct lookup (backwards compatible)
        logger.warning("No org membership found, falling back to direct lookup")

    # 3. Direct lookup (single-org users)
    return await db.users.find_one({"stytch_member_id": stytch_member_id})
```

**Result**: ALL users can authenticate, even those with incomplete `user_organization_memberships` data.

---

## Impact on Backend Services

### No Code Changes Required ✅

The following patterns continue to work exactly as before:

#### Pattern 1: Using StytchContext (Most Common)
```python
from ayz_auth import verify_auth
from fastapi import Depends

@app.post("/api/resource")
async def create_resource(
    user: StytchContext = Depends(verify_auth)
):
    # user.mongo_user_id will now be populated for ALL users
    # Previously failed for ~20% of multi-org users
    # Now succeeds with fallback logic

    team_id = user.current_team_id  # May be None if user has no teams
    org_id = user.mongo_organization_id

    # Your existing logic works unchanged
    ...
```

#### Pattern 2: Entitlement Checks
```python
from ayz_auth import require_entitlement

@app.get("/api/foresight")
async def foresight_endpoint(
    user: StytchContext = Depends(require_entitlement("foresight"))
):
    # Still works exactly the same
    # Now works for multi-org users who previously failed auth
    ...
```

#### Pattern 3: Team Validation
```python
async def validate_user_team_access(user_id: PyObjectId, team_id: str, db):
    membership = await db["user_team_memberships"].find_one({
        "user_id": user_id,
        "team_id": PyObjectId(team_id),
        "status": "active"
    })
    return membership is not None
```

**Key Improvement**: `user.current_team_id` is now **validated** by ayz-auth before being returned:
- ✅ Team belongs to current organization
- ✅ Auto-corrected if stale (user switched orgs)
- ✅ Set to `None` if user has no teams in current org

This means your team validation should **pass more often** because ayz-auth ensures `current_team_id` is valid for the current org context.

---

## New Logging to Monitor

### Fallback Warnings
When a user authenticates via fallback (missing org membership), you'll see:

```
WARNING - No org membership found for stytch_member_id=member-live-xyz789, org=organization-live-abc123. Falling back to direct user lookup.
```

**What to do**: These warnings identify users with incomplete `user_organization_memberships` data. Collect these member IDs and report them to the backend team for data backfill.

### Team Validation Logs
```
WARNING - MULTI-ORG FIX: Stale team_id detected for user member-live-xyz789. Team team_mongo_123 belongs to org org_mongo_456, but user is in org org_mongo_789
```

**What it means**: ayz-auth detected and auto-corrected a stale team. User switched organizations, and ayz-auth automatically found a valid team in the new org.

```
INFO - Found valid team team_mongo_456 for user member-live-xyz789 in org organization-live-abc123
```

**What it means**: ayz-auth successfully auto-corrected the team context.

---

## Optional: Improved Multi-Org Support

While no changes are required, you can now take advantage of better multi-org support:

### Understanding Team Context
In v2.2.0, `StytchContext.current_team_id` is **guaranteed** to be:
- `None` if user has no teams in current organization, OR
- A valid team ID that exists in the current organization

**Before v2.2.0**: Could be a team ID from a different organization (stale)
**After v2.2.0**: Always valid for current org context, or `None`

### Handling `current_team_id = None`
If your endpoint requires a team, you may want to add explicit checks:

```python
@app.post("/api/team-resource")
async def create_team_resource(
    user: StytchContext = Depends(verify_auth)
):
    if not user.current_team_id:
        raise HTTPException(
            status_code=400,
            detail="No team selected. Please select a team in your organization."
        )

    # Proceed with team-specific logic
    ...
```

**Note**: This is optional. If your code already handles `None` gracefully, no changes needed.

---

## Testing Recommendations

### Staging Environment Testing
After deploying v2.2.0 to staging:

1. **Test multi-org users**:
   - Users who belong to multiple organizations
   - Users who switch between organizations
   - Users who were previously failing with "mongo_user_id not available"

2. **Test single-org users** (backwards compatibility):
   - Should work exactly as before
   - No performance impact

3. **Monitor logs for**:
   - Fallback warnings (identify users with missing org memberships)
   - Team validation logs (ensure team auto-correction works)

### Production Monitoring (Post-Deploy)
After deploying to production:

1. **Monitor authentication error rates**:
   - Should see ~20% decrease (users who were failing due to missing org memberships)
   - Target: < 1% authentication error rate

2. **Monitor fallback warnings**:
   - Collect affected `stytch_member_id` values
   - Report to backend team for data backfill

3. **Monitor team validation logs**:
   - Ensure stale team detection and auto-correction is working
   - Should see fewer "Team access denied" errors in backend services

---

## Common Questions

### Q: Do I need to change any environment variables?
**A**: No. All existing environment variables work unchanged.

### Q: Do I need to update my MongoDB queries?
**A**: No. This fix is entirely within ayz-auth. Your backend MongoDB queries remain the same.

### Q: What if I'm still seeing authentication errors?
**A**: Check the ayz-auth logs for:
1. Fallback warnings (user missing org membership)
2. MongoDB connection errors
3. Stytch API errors

If fallback warnings are frequent, it indicates a data quality issue that needs backfilling.

### Q: Is there any performance impact?
**A**: Minimal. The fallback adds one extra MongoDB query only when org membership is missing (~20% of users currently). Once `user_organization_memberships` is backfilled, fallback will rarely trigger.

**Performance profile**:
- **Multi-org users with org membership**: Same as v2.1.1 (2 queries: org lookup + user lookup)
- **Multi-org users without org membership**: 3 queries (org lookup + membership lookup + fallback user lookup)
- **Single-org users**: Same as v2.1.1 (1 query: direct user lookup)

### Q: When will `user_organization_memberships` be backfilled?
**A**: This is a separate data quality task tracked in a different ticket. The v2.2.0 fix ensures authentication works even without backfill.

---

## Rollback Plan (If Needed)

If you encounter issues with v2.2.0, you can rollback:

```bash
# requirements.txt
ayz-auth[mongodb]==2.1.1
```

```bash
uv pip install -r requirements.txt
# Restart services
```

**Note**: Rollback will restore the authentication failures for multi-org users with missing org memberships.

---

## Support

If you encounter issues or have questions:
1. Check [DISCOVERY.md](./DISCOVERY.md) for technical analysis
2. Check [research.md](./research.md) for detailed system documentation
3. Check backend team Slack channel
4. File a bug report with logs attached

---

## Summary Checklist for Backend Developers

- [ ] Update `requirements.txt` to `ayz-auth[mongodb]==2.2.0`
- [ ] Deploy to staging and test with multi-org users
- [ ] Monitor logs for fallback warnings
- [ ] Monitor authentication error rates (should decrease)
- [ ] Deploy to production
- [ ] Collect `stytch_member_id` values from fallback warnings for data backfill
- [ ] Report any issues to backend team

**No code changes required in your services!** 🎉
