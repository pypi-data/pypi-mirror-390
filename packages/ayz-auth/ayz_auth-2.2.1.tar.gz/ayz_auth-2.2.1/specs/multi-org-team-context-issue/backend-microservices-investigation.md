# Backend Microservices Authentication Issue - Root Cause Analysis

## Executive Summary

Users with access to multiple organizations experience **persistent 400 Bad Request errors** when loading chat sessions, even after frontend fixes have been deployed. This document provides a comprehensive analysis of the root cause, which lies in the **ayz-auth authentication package** used by backend microservices.

### The Core Problem

The `ayz-auth` package reads `User.current_team_id` directly from MongoDB and caches it in Redis **without validating it belongs to the user's current organization**. This stale team_id is then passed to backend microservices, which reject requests with 403 Forbidden errors when they validate team membership.

### Impact

- **400/403 errors** when fetching sessions, projects, or personas after switching organizations
- **False security warnings** in logs about unauthorized team access
- **Degraded user experience** for multi-org users
- **Cache pollution** - stale team_ids cached for 5 minutes in Redis

### Recommended Solution

Fix the `ayz-auth` package to validate team_id against organization context before returning it in the authentication context.

---

## Background: Multi-Organization Architecture

### User Model Design

The application uses a **single-tenant-per-session** model for multi-org support:

```typescript
// app/models/User.ts
interface User {
  _id: ObjectId
  email: string
  stytch_member_id: string
  current_team_id: ObjectId  // ❌ SINGLE value across ALL organizations
  // ... other fields
}
```

**Key Design Decision**: Users can belong to multiple organizations, but the `current_team_id` field stores only ONE team across all organizations. This creates stale state when users switch between organizations.

### Organization Switching Flow

```
User logged into Org A with Team X
  ↓
User logs out
  ↓
User logs into Org B
  ↓
MongoDB User.current_team_id = Team X (STALE - belongs to Org A!)
  ↓
Backend reads Team X from MongoDB
  ↓
Backend validates: "Does user have access to Team X in Org B?"
  ↓
Validation FAILS - Team X belongs to Org A, not Org B
  ↓
400/403 Error returned to frontend
```

### Authentication Stack

The application uses a multi-layer authentication architecture:

```
┌─────────────────────────────────────────────────────────┐
│ Frontend (soulmates-app)                                │
│ - React Router v7                                       │
│ - Stytch B2B authentication                             │
│ - Session JWT tokens                                    │
└─────────────────────────────────────────────────────────┘
                        ↓ HTTP requests with JWT
┌─────────────────────────────────────────────────────────┐
│ Backend Microservices                                   │
│ - soulmates-app-backend (FastAPI)                       │
│ - soulmates-file-management (FastAPI)                   │
│ - Uses ayz-auth package for authentication              │
└─────────────────────────────────────────────────────────┘
                        ↓ Calls ayz-auth
┌─────────────────────────────────────────────────────────┐
│ ayz-auth Package (Python)                               │
│ - Validates Stytch JWT tokens                           │
│ - Loads user context from MongoDB                       │
│ - Caches context in Redis (5 min TTL)                   │
│ - Returns StytchContext with current_team_id            │
└─────────────────────────────────────────────────────────┘
                        ↓ Queries
┌─────────────────────────────────────────────────────────┐
│ MongoDB                                                 │
│ - users collection (User.current_team_id)               │
│ - teams collection                                      │
│ - user_team_memberships collection                      │
└─────────────────────────────────────────────────────────┘
```

---

## Deep Dive: The Authentication Flow

### Step 1: Frontend Authentication (soulmates-app)

When a user logs in, the frontend:

1. Authenticates with Stytch B2B
2. Receives a JWT session token
3. Stores token in session storage
4. Includes token in all API requests via `Authorization: Bearer <token>`

**Code Location**: [app/lib/services/server/auth/auth-utils.server.ts](../../app/lib/services/server/auth/auth-utils.server.ts)

### Step 2: Backend Request Handling (soulmates-app-backend)

When the frontend makes a request to `/api/sessions?team_id=xxx`:

```python
# app/api/sessions.py
@router.get("/")
async def list_sessions(
    request: Request,
    team_id: str = Query(...),
    auth_context: AuthContext = Depends(get_auth_context),  # ← ayz-auth validates token
    db = Depends(get_db)
):
    # Extract user's MongoDB ObjectId
    user_object_id = get_user_object_id_from_auth(auth_context)

    # Validate user has access to the requested team
    has_team_access = await validate_user_team_access(user_object_id, team_id, db)

    if not has_team_access:
        raise HTTPException(status_code=403, detail="Access denied")

    # Fetch sessions...
```

**Key Files**:
- [app/api/sessions.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/api/sessions.py) - Sessions endpoint
- [app/core/stytch_auth.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/core/stytch_auth.py) - AuthContext model
- [app/core/team_validation.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/core/team_validation.py) - Team access validation

### Step 3: ayz-auth Token Validation

The `ayz-auth` package handles JWT validation and context loading:

```python
# ayz-auth/src/ayz_auth/auth/verify.py (conceptual)
async def verify_auth(request: Request) -> StytchContext:
    # Extract JWT from Authorization header
    token = extract_bearer_token(request)

    # Validate token with Stytch API
    session = await stytch_client.sessions.authenticate(token)

    # Load additional context from MongoDB
    context_data = await entitlements_loader.load_complete_session_data(
        stytch_org_id=session.organization_id,
        stytch_member_id=session.member_id
    )

    # Build StytchContext with team information
    return StytchContext(
        member_id=session.member_id,
        organization_id=session.organization_id,
        current_team_id=context_data["current_team_id"],  # ❌ STALE VALUE
        # ... other fields
    )
```

**Key Files**:
- [src/ayz_auth/db/entitlements_loader.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/db/entitlements_loader.py) - Loads user context
- [src/ayz_auth/db/mongo_client.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/db/mongo_client.py) - MongoDB queries
- [src/ayz_auth/models/context.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/models/context.py) - StytchContext model

### Step 4: Team Context Loading (The Problem!)

```python
# ayz-auth/src/ayz_auth/db/entitlements_loader.py
async def load_user_context(self, stytch_member_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user context with team information (5-minute caching).

    ❌ PROBLEM: No organization validation!
    """
    # Try cache first
    cached_data = await redis_client.get_cached_user_context(stytch_member_id)
    if cached_data:
        return cached_data  # Returns cached team_id regardless of current org

    # Fallback to MongoDB
    user_doc = await mongo_client.get_user(stytch_member_id)
    if not user_doc:
        return None

    # Extract user context
    current_team_id = user_doc.get("current_team_id")  # ❌ Raw MongoDB value
    user_context = {
        "current_team_id": str(current_team_id) if current_team_id else None,
        "current_team_name": None,
        "mongo_user_id": str(user_id) if user_id is not None else None,
    }

    # Load team details if team ID is present
    if current_team_id:
        team_name = await self._load_team_name(current_team_id)
        user_context["current_team_name"] = team_name

    # Cache for 5 minutes (no org validation!)
    await redis_client.cache_user_context(stytch_member_id, user_context)

    return user_context
```

**What's Missing**:
1. ❌ No validation that `current_team_id` belongs to the current organization
2. ❌ No organization context passed to this function
3. ❌ Redis cache key doesn't include organization: `user_context:{stytch_member_id}`
4. ❌ No auto-correction when team_id is stale

### Step 5: Team Access Validation (Where It Fails)

```python
# app/core/team_validation.py
async def validate_user_team_access(user_id: PyObjectId, team_id: str, db) -> bool:
    """
    Validate that the authenticated user has access to the specified team.

    This is where the 403 error originates!
    """
    try:
        # Convert team_id to ObjectId
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
                f"TEAM_ACCESS_DENIED: user {user_id} attempted access to team {team_id} "
                f"- no valid membership found"
            )

        return is_valid

    except Exception as e:
        logger.error(f"SECURITY: Error validating team access: {e}")
        return False  # Fail secure
```

**Why This Fails**:
- User is logged into **Org B** (Riot)
- ayz-auth returns `current_team_id = "68a4ac950d61e34b54b19866"` (Team from **Org A** - Ayzenberg)
- Backend queries: "Does user have active membership in team 68a4ac950d61e34b54b19866?"
- MongoDB returns `None` - user has NO membership for this team in the context of Org B
- Validation returns `False`
- Backend raises 403 Forbidden error

---

## The Complete Data Flow (With Problem Points)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Switches Organizations                                  │
│    - User logs out of Org A                                     │
│    - User logs into Org B                                       │
│    - MongoDB User.current_team_id still = Team X (Org A) ❌      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Frontend Makes Request                                       │
│    GET /api/sessions?team_id=68a4ac950d61e34b54b19866           │
│    Authorization: Bearer <jwt_token>                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. ayz-auth Validates Token                                     │
│    - Validates JWT with Stytch ✅                                │
│    - Loads user context from MongoDB ❌                          │
│    - Returns current_team_id = "68a4ac..." (Team X from Org A)  │
│    - Caches in Redis for 5 minutes ❌                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Backend Receives AuthContext                                 │
│    auth_context.current_team_id = "68a4ac..." ❌                 │
│    auth_context.organization_id = "Org B" ✅                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Backend Validates Team Access                                │
│    Query: user_team_memberships.find_one({                      │
│      user_id: "user123",                                        │
│      team_id: "68a4ac...",  ← Team X from Org A                 │
│      status: "active"                                           │
│    })                                                           │
│    Result: None ❌ (User has no membership in this team         │
│                    in the context of Org B)                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Backend Returns Error                                        │
│    HTTP 403 Forbidden                                           │
│    "Access denied: User not authorized for this team"           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Frontend Receives Error                                      │
│    - User sees "Failed to load sessions"                        │
│    - Console shows 403 error                                    │
│    - User experience degraded                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why Frontend Fixes Didn't Work

### PR #393: Frontend TeamContext Priority Logic

**What it fixed**:
- Updated team selection logic to prefer server-provided `current_team_id`
- Added localStorage validation against organization context
- Auto-cleared stale localStorage when org mismatch detected

**Why it didn't solve the problem**:
- Frontend correctly selects the right team from the server response
- BUT the server response itself contains a stale team_id from MongoDB
- The validation happens AFTER ayz-auth has already loaded the stale value
- Frontend has no way to "correct" what the backend is sending

### PR #397: Backend Service Layer Validation

**What it fixed**:
- Added validation in `membershipService.buildUserPermissionContextForOrg()`
- Auto-corrects stale team_id when building permission context
- Updates MongoDB with correct team_id

**Why it didn't solve the problem**:
- This validation only happens in the **soulmates-app** backend (Node.js/TypeScript)
- The **soulmates-app-backend** microservice (Python/FastAPI) uses **ayz-auth**
- ayz-auth bypasses this validation entirely
- Two separate backends with two separate authentication flows

### PR #398: Frontend Loader Validation

**What it fixed**:
- Updated [app-layout.tsx](../../app/routes/app-layout.tsx) to use validated `current_team_id` from permission context
- Removed direct reads of `User.current_team_id` from MongoDB in the loader

**Why it didn't solve the problem**:
- This only affects the app-layout loader in soulmates-app
- When frontend makes requests to `/api/sessions`, it goes to **soulmates-app-backend** (different service)
- soulmates-app-backend uses ayz-auth for authentication
- ayz-auth still loads the stale team_id and returns it in the auth context

---

## The Real Root Cause: ayz-auth Architecture

### Problem 1: No Organization Context

```python
# Current implementation
async def load_user_context(self, stytch_member_id: str) -> Optional[Dict[str, Any]]:
    """
    ❌ PROBLEM: Only accepts stytch_member_id, no organization context!
    """
    user_doc = await mongo_client.get_user(stytch_member_id)
    current_team_id = user_doc.get("current_team_id")  # Could belong to ANY org
    return {"current_team_id": str(current_team_id) if current_team_id else None}
```

**What's needed**:
```python
# Fixed implementation
async def load_user_context(
    self,
    stytch_member_id: str,
    stytch_org_id: str  # ✅ Add organization context
) -> Optional[Dict[str, Any]]:
    """
    Load user context with organization-scoped team validation.
    """
    user_doc = await mongo_client.get_user(stytch_member_id)
    current_team_id = user_doc.get("current_team_id")

    # ✅ NEW: Validate team belongs to current organization
    if current_team_id:
        team_doc = await mongo_client.get_team(current_team_id)
        if team_doc:
            team_org_id = team_doc.get("organization")
            mongo_org = await mongo_client.get_organization(stytch_org_id)

            # Check if team's organization matches current organization
            if str(team_org_id) != str(mongo_org.get("_id")):
                # Team belongs to different org - need to fix this
                logger.warning(
                    f"Stale current_team_id detected: team {current_team_id} "
                    f"belongs to different org than {stytch_org_id}"
                )
                # Auto-correct to first team in current org
                current_team_id = await self._get_first_team_in_org(
                    stytch_member_id,
                    stytch_org_id
                )

    return {"current_team_id": str(current_team_id) if current_team_id else None}
```

### Problem 2: Cache Pollution

```python
# Current cache key structure
cache_key = f"user_context:{stytch_member_id}"  # ❌ No org context!

# Cache contents
{
  "current_team_id": "68a4ac950d61e34b54b19866",  # Could be from ANY org
  "current_team_name": "a.digital",
  "mongo_user_id": "690ba9fbc002e6138c895eef"
}
```

**What's needed**:
```python
# Fixed cache key structure
cache_key = f"user_context:{stytch_member_id}:org:{stytch_org_id}"  # ✅ Org-scoped

# This ensures different orgs have separate cached contexts
```

### Problem 3: No Auto-Correction

When ayz-auth detects a stale team_id, it should:
1. ✅ Log a warning
2. ✅ Query for user's teams in the current organization
3. ✅ Default to the first available team
4. ✅ Update MongoDB `User.current_team_id` to fix the stale state
5. ✅ Return the corrected team_id

Currently, ayz-auth does **none of this** - it just returns whatever is in MongoDB.

---

## Recommended Solution

### Option 1: Fix ayz-auth Package (RECOMMENDED)

This is the most robust solution that fixes the issue at the source.

#### Changes Required in ayz-auth

**File: `src/ayz_auth/db/entitlements_loader.py`**

```python
async def load_user_context(
    self,
    stytch_member_id: str,
    stytch_org_id: str  # ✅ NEW: Add organization context
) -> Optional[Dict[str, Any]]:
    """
    Load user context with organization-scoped team validation (5-minute caching).

    Args:
        stytch_member_id: Stytch member identifier
        stytch_org_id: Stytch organization identifier (for validation)

    Returns:
        Dict containing:
            - current_team_id: str (MongoDB ObjectId as string) or None
            - current_team_name: str or None
            - mongo_user_id: str (MongoDB ObjectId as string)
        Returns None if MongoDB is not configured or user not found
    """
    try:
        # ✅ NEW: Include org in cache key
        cache_key = f"user_context:{stytch_member_id}:org:{stytch_org_id}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            logger.debug(
                f"Using cached user context for member: {stytch_member_id} "
                f"in org: {stytch_org_id}"
            )
            return cached_data

        # Fallback to MongoDB
        user_doc = await mongo_client.get_user(stytch_member_id)
        if not user_doc:
            logger.debug(f"User not found in MongoDB for member: {stytch_member_id}")
            return None

        # Extract user context
        current_team_id = user_doc.get("current_team_id")
        user_id = user_doc.get("_id")

        # ✅ NEW: Validate team belongs to current organization
        validated_team_id = None
        team_name = None

        if current_team_id:
            validated_team_id = await self._validate_team_belongs_to_org(
                current_team_id,
                stytch_org_id,
                stytch_member_id
            )

            if validated_team_id:
                team_name = await self._load_team_name(validated_team_id)

        # If no valid team found, get first team in current org
        if not validated_team_id:
            validated_team_id = await self._get_first_team_in_org(
                stytch_member_id,
                stytch_org_id
            )
            if validated_team_id:
                team_name = await self._load_team_name(validated_team_id)

                # ✅ NEW: Auto-correct stale MongoDB value
                await self._update_user_current_team(user_id, validated_team_id)

        user_context = {
            "current_team_id": str(validated_team_id) if validated_team_id else None,
            "current_team_name": team_name,
            "mongo_user_id": str(user_id) if user_id is not None else None,
        }

        # Cache for 5 minutes with org-scoped key
        await redis_client.setex(cache_key, 300, user_context)

        logger.debug(
            f"Loaded user context from MongoDB for member: {stytch_member_id} "
            f"in org: {stytch_org_id}"
        )
        return user_context

    except Exception as e:
        logger.warning(
            f"Failed to load user context: {str(e)}. "
            f"Continuing without user context data."
        )
        return None

async def _validate_team_belongs_to_org(
    self,
    team_id: Any,
    stytch_org_id: str,
    stytch_member_id: str
) -> Optional[str]:
    """
    Validate that a team belongs to the specified organization.

    Args:
        team_id: MongoDB ObjectId of the team
        stytch_org_id: Stytch organization identifier
        stytch_member_id: Stytch member identifier (for logging)

    Returns:
        Team ID as string if valid, None if team doesn't belong to org
    """
    try:
        # Load team document
        team_doc = await mongo_client.get_team(team_id)
        if not team_doc:
            logger.warning(f"Team {team_id} not found in MongoDB")
            return None

        # Load organization document to get MongoDB ObjectId
        org_doc = await mongo_client.get_organization(stytch_org_id)
        if not org_doc:
            logger.warning(f"Organization {stytch_org_id} not found in MongoDB")
            return None

        # Compare team's organization with current organization
        team_org_id = team_doc.get("organization")
        current_org_id = org_doc.get("_id")

        if str(team_org_id) == str(current_org_id):
            # Team belongs to current org - valid!
            logger.debug(
                f"Team {team_id} validated for org {stytch_org_id}"
            )
            return str(team_id)
        else:
            # Team belongs to different org - stale!
            logger.warning(
                f"MULTI-ORG FIX: Stale team_id detected for user {stytch_member_id}. "
                f"Team {team_id} belongs to org {team_org_id}, "
                f"but user is in org {current_org_id}"
            )
            return None

    except Exception as e:
        logger.error(f"Error validating team belongs to org: {e}")
        return None

async def _get_first_team_in_org(
    self,
    stytch_member_id: str,
    stytch_org_id: str
) -> Optional[str]:
    """
    Get the first team the user belongs to in the specified organization.

    Args:
        stytch_member_id: Stytch member identifier
        stytch_org_id: Stytch organization identifier

    Returns:
        Team ID as string if found, None otherwise
    """
    try:
        # Get user document
        user_doc = await mongo_client.get_user(stytch_member_id)
        if not user_doc:
            return None

        user_id = user_doc.get("_id")

        # Get organization document
        org_doc = await mongo_client.get_organization(stytch_org_id)
        if not org_doc:
            return None

        org_mongo_id = org_doc.get("_id")

        # Query user_team_memberships for teams in this org
        db = await mongo_client._get_client()
        if not db:
            return None

        # Find all active team memberships for this user
        memberships = await db["user_team_memberships"].find({
            "user_id": user_id,
            "status": "active"
        }).to_list(length=100)

        # Check each team to see if it belongs to current org
        for membership in memberships:
            team_id = membership.get("team_id")
            if not team_id:
                continue

            team_doc = await mongo_client.get_team(team_id)
            if not team_doc:
                continue

            team_org_id = team_doc.get("organization")
            if str(team_org_id) == str(org_mongo_id):
                # Found a team in current org!
                logger.info(
                    f"Found first team {team_id} for user {stytch_member_id} "
                    f"in org {stytch_org_id}"
                )
                return str(team_id)

        # No teams found in current org
        logger.warning(
            f"No teams found for user {stytch_member_id} in org {stytch_org_id}"
        )
        return None

    except Exception as e:
        logger.error(f"Error getting first team in org: {e}")
        return None

async def _update_user_current_team(
    self,
    user_id: Any,
    team_id: str
) -> None:
    """
    Update the user's current_team_id in MongoDB.

    Args:
        user_id: MongoDB ObjectId of the user
        team_id: Team ID string to set as current
    """
    try:
        from bson import ObjectId

        db = await mongo_client._get_client()
        if not db:
            return

        team_object_id = ObjectId(team_id)

        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"current_team_id": team_object_id}}
        )

        logger.info(
            f"✅ Auto-corrected User.current_team_id in MongoDB: "
            f"user {user_id} -> team {team_id}"
        )

    except Exception as e:
        logger.error(
            f"Failed to update User.current_team_id in MongoDB: {e}. "
            f"Continuing with validated team_id in memory."
        )
```

**File: `src/ayz_auth/auth/verify.py`** (update to pass org context)

```python
async def verify_auth(request: Request) -> StytchContext:
    """
    Main authentication function that validates JWT and loads user context.
    """
    # Extract and validate JWT
    token = extract_bearer_token(request)
    session = await stytch_client.sessions.authenticate(token)

    # Load complete session data with organization context
    context_data = await entitlements_loader.load_complete_session_data(
        stytch_org_id=session.organization_id,
        stytch_member_id=session.member_id
    )

    # Build StytchContext with validated team information
    return StytchContext(
        member_id=session.member_id,
        organization_id=session.organization_id,
        current_team_id=context_data["current_team_id"],  # ✅ Now validated!
        current_team_name=context_data["current_team_name"],
        mongo_user_id=context_data["mongo_user_id"],
        # ... other fields
    )
```

**File: `src/ayz_auth/db/entitlements_loader.py`** (update public method)

```python
async def load_complete_session_data(
    self,
    stytch_org_id: str,
    stytch_member_id: str
) -> Dict[str, Any]:
    """
    Load both organization entitlements and user context in one call.

    Args:
        stytch_org_id: Stytch organization identifier
        stytch_member_id: Stytch member identifier

    Returns:
        Dict containing all entitlements and user context data.
        Returns empty dict values if MongoDB is not configured.
    """
    import asyncio

    org_data_task = self.load_organization_entitlements(stytch_org_id)
    user_data_task = self.load_user_context(
        stytch_member_id,
        stytch_org_id  # ✅ NOW passing org context
    )

    org_data, user_data = await asyncio.gather(
        org_data_task, user_data_task, return_exceptions=True
    )

    # Handle exceptions...
    if isinstance(org_data, Exception):
        logger.warning(f"Exception loading organization data: {org_data}")
        org_data = None

    if isinstance(user_data, Exception):
        logger.warning(f"Exception loading user data: {user_data}")
        user_data = None

    # Combine results
    return {
        "entitlements": org_data.get("entitlements") if org_data else None,
        "subscription_tier": org_data.get("subscription_tier") if org_data else None,
        "subscription_limits": org_data.get("subscription_limits") if org_data else None,
        "mongo_organization_id": org_data.get("mongo_organization_id") if org_data else None,
        "current_team_id": user_data.get("current_team_id") if user_data else None,  # ✅ Validated
        "current_team_name": user_data.get("current_team_name") if user_data else None,
        "mongo_user_id": user_data.get("mongo_user_id") if user_data else None,
    }
```

#### Benefits of This Approach

✅ **Fixes the Root Cause**: Validation happens at the authentication layer, before any backend logic runs

✅ **Self-Healing**: Automatically corrects stale MongoDB values

✅ **Cache Efficiency**: Org-scoped cache keys prevent cross-org pollution

✅ **Transparent**: No changes needed in soulmates-app-backend or other services using ayz-auth

✅ **Backward Compatible**: Can keep old behavior for services that don't care about org context

✅ **Comprehensive Logging**: Clear audit trail of when auto-correction happens

#### Rollout Plan for Option 1

1. **Week 1**: Implement changes in ayz-auth package
   - Add organization validation logic
   - Update cache key structure
   - Add auto-correction functionality
   - Write unit tests

2. **Week 2**: Test in development environment
   - Deploy updated ayz-auth to dev
   - Test multi-org scenarios
   - Verify cache behavior
   - Monitor logs for auto-correction events

3. **Week 3**: Deploy to staging
   - Deploy to staging environment
   - QA testing with real multi-org users
   - Performance testing (cache hit rates)
   - Monitor error rates

4. **Week 4**: Production rollout
   - Deploy to production (10% of traffic)
   - Monitor metrics closely
   - Expand to 50%, then 100%
   - Document behavior for other teams

---

### Option 2: Frontend Query Parameter Override (WORKAROUND)

If fixing ayz-auth is not feasible immediately, implement a workaround in the frontend and backend.

#### Frontend Changes

**File: `app/lib/services/client/sessionService.ts`**

```typescript
static async getSessionsPaginated(
  page = 1,
  pageSize = 20,
  signal?: AbortSignal
): Promise<PaginatedResponse<Session>> {
  // Get VALIDATED team_id from TeamContext (not from stale source)
  const { currentTeam } = useTeam()

  if (!currentTeam?.team_id) {
    throw new Error('No team selected')
  }

  // ✅ Pass validated team_id from frontend (already org-scoped)
  const params = new URLSearchParams({
    team_id: currentTeam.team_id,  // This is validated by /api/teams/user/:userId
    page: page.toString(),
    page_size: pageSize.toString(),
  })

  const response = await authFetch<PaginatedResponse<Session>>(
    SessionServiceClient.buildEndpoint(`?${params}`),
    { signal }
  )
  return response
}
```

#### Backend Changes

**File: `app/api/sessions.py` (soulmates-app-backend)**

```python
@router.get("/")
async def list_sessions(
    request: Request,
    team_id: str = Query(...),  # Still require team_id
    auth_context: AuthContext = Depends(get_auth_context),
    db = Depends(get_db)
):
    """
    List sessions for a team.

    ✅ WORKAROUND: Accept team_id from query param (validated by frontend)
    instead of trusting auth_context.current_team_id (which may be stale)
    """
    user_object_id = get_user_object_id_from_auth(auth_context)

    # Validate user has access to the requested team
    has_team_access = await validate_user_team_access(user_object_id, team_id, db)

    if not has_team_access:
        logger.warning(
            f"Team access denied: user {user_object_id} attempted to access team {team_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied")

    # Use the validated team_id from query param (NOT auth_context.current_team_id)
    # This way, even if auth_context has stale team_id, the query param wins
    team_object_id = PyObjectId(team_id)

    # Fetch sessions...
```

#### Pros and Cons

**Pros**:
- ✅ Can implement quickly without changing ayz-auth
- ✅ Works with existing validation in `/api/teams/user/:userId`
- ✅ Frontend controls team selection

**Cons**:
- ❌ Workaround, not a real fix
- ❌ Still leaves auth_context.current_team_id stale
- ❌ Other services using ayz-auth still have the problem
- ❌ Technical debt - "why don't we use the auth context?"

---

### Option 3: Clear Cache on Organization Switch (TEMPORARY)

Implement a cache-clearing mechanism when users switch organizations.

#### Frontend Changes

**File: `app/routes/auth/logout.tsx`**

```typescript
export async function action({ request }: Route.ActionArgs) {
  try {
    // Clear Stytch session
    await clearSession(request)

    // ✅ NEW: Clear ayz-auth Redis cache
    const { clearAyzAuthCache } = await import('~/lib/services/server/cache')
    const sessionData = await getSession(request)
    if (sessionData?.memberId) {
      await clearAyzAuthCache(sessionData.memberId)
    }

    // Clear local session storage
    return redirect('/auth/login', {
      headers: {
        'Set-Cookie': await sessionStorage.destroySession(session),
      },
    })
  } catch (error) {
    logger.error('Logout error:', error)
    return redirect('/auth/login')
  }
}
```

**File: `app/lib/services/server/cache.ts`** (NEW)

```typescript
import { createClient } from 'redis'

export async function clearAyzAuthCache(stytchMemberId: string): Promise<void> {
  try {
    const redis = createClient({
      url: process.env.REDIS_URL
    })

    await redis.connect()

    // Clear user context cache (all orgs)
    const pattern = `user_context:${stytchMemberId}*`
    const keys = await redis.keys(pattern)

    if (keys.length > 0) {
      await redis.del(keys)
      logger.info(`Cleared ${keys.length} ayz-auth cache entries for user ${stytchMemberId}`)
    }

    await redis.quit()
  } catch (error) {
    logger.error('Failed to clear ayz-auth cache:', error)
    // Don't fail logout if cache clear fails
  }
}
```

#### Pros and Cons

**Pros**:
- ✅ Quick to implement
- ✅ No changes to ayz-auth needed
- ✅ Clears stale cache on every logout

**Cons**:
- ❌ Doesn't fix the underlying problem
- ❌ Relies on users logging out/in
- ❌ Cache could become stale again during session
- ❌ Adds Redis dependency to frontend
- ❌ Performance impact (cache miss on every org switch)

---

## Recommended Implementation: Option 1

**Fix ayz-auth package** is the best long-term solution because:

1. **Fixes Root Cause**: Addresses the problem at the source
2. **Self-Healing**: Automatically corrects stale state
3. **Transparent**: No changes needed in services using ayz-auth
4. **Comprehensive**: Fixes the issue for ALL backend microservices
5. **Maintainable**: Clear separation of concerns

### Success Criteria

After implementing Option 1, verify:

- ✅ Zero 400/403 errors when loading sessions after org switch
- ✅ Redis cache hit rate remains >90%
- ✅ Auto-correction logs appear when stale team_id detected
- ✅ MongoDB `User.current_team_id` updates automatically
- ✅ All backend microservices work correctly

### Monitoring

Add the following monitoring after deployment:

```python
# In ayz-auth logging
logger.info("ayz_auth.team_validation", {
    "event": "stale_team_detected",
    "stytch_member_id": stytch_member_id,
    "stale_team_id": current_team_id,
    "corrected_team_id": validated_team_id,
    "organization_id": stytch_org_id
})

logger.info("ayz_auth.cache", {
    "event": "user_context_loaded",
    "source": "cache" | "mongodb",
    "cache_key": cache_key,
    "has_team_id": bool(validated_team_id)
})
```

Monitor these metrics in production:
- **Stale team detection rate**: How often auto-correction triggers
- **Cache hit rate**: Should remain >90%
- **403 error rate**: Should drop to near zero
- **Auto-correction success rate**: Should be 100%

---

## Testing Strategy

### Test Scenario 1: Stale Team ID Detection

```
Given:
  - User belongs to Org A (team_id: 68a4ac950d61e34b54b19866)
  - User belongs to Org B (team_id: 690267936d33d610c7513172)
  - MongoDB User.current_team_id = 68a4ac950d61e34b54b19866 (Org A)

When:
  - User logs into Org B
  - ayz-auth loads user context

Then:
  - ✅ ayz-auth detects team 68a4ac... belongs to Org A, not Org B
  - ✅ ayz-auth queries for teams in Org B
  - ✅ ayz-auth finds team 690267... in Org B
  - ✅ ayz-auth returns team 690267... in StytchContext
  - ✅ ayz-auth updates MongoDB User.current_team_id to 690267...
  - ✅ Warning logged with stale team info
```

### Test Scenario 2: Cache Behavior

```
Given:
  - User in Org A (team_id: xxx)
  - Redis cache exists for user in Org A
  - User switches to Org B

When:
  - ayz-auth loads user context for Org B

Then:
  - ✅ Cache key includes org: user_context:{member_id}:org:{org_b_id}
  - ✅ Cache miss (different key than Org A)
  - ✅ Load from MongoDB
  - ✅ Validate and return correct team for Org B
  - ✅ Cache with org-scoped key
```

### Test Scenario 3: MongoDB Update

```
Given:
  - User has stale team_id in MongoDB

When:
  - ayz-auth auto-corrects team_id

Then:
  - ✅ MongoDB User.current_team_id updated
  - ✅ If MongoDB update fails, still return validated team_id
  - ✅ Error logged if update fails
  - ✅ Request doesn't fail (graceful degradation)
```

### Test Scenario 4: No Teams in Organization

```
Given:
  - User has no teams in Org B

When:
  - User logs into Org B

Then:
  - ✅ ayz-auth returns current_team_id: null
  - ✅ Warning logged
  - ✅ Backend handles null team_id gracefully
  - ✅ User sees "No team selected" message
```

---

## Migration Path

If you choose to implement Option 1 (recommended), follow this migration path:

### Phase 1: Implement ayz-auth Fix
- Update ayz-auth package with organization validation
- Add auto-correction logic
- Update cache key structure
- Deploy to dev environment

### Phase 2: Test Thoroughly
- Test multi-org scenarios
- Verify cache behavior
- Monitor auto-correction logs
- Performance testing

### Phase 3: Deploy to Production
- Staged rollout (10% → 50% → 100%)
- Monitor error rates
- Verify auto-correction working
- Check cache hit rates

### Phase 4: Cleanup (Optional)
- Remove workarounds from frontend (if any)
- Update documentation
- Add monitoring dashboards
- Train team on new behavior

---

## Conclusion

The root cause of persistent 400/403 errors in multi-org scenarios is the **ayz-auth package reading stale `User.current_team_id` values from MongoDB without organization-scoped validation**.

The recommended solution is to **fix ayz-auth** to:
1. Accept organization context when loading user data
2. Validate team_id belongs to current organization
3. Auto-correct stale values in MongoDB
4. Use org-scoped Redis cache keys

This fix will transparently resolve the issue for all backend microservices using ayz-auth, without requiring changes to their code.

---

## References

### Key Files in ayz-auth
- [src/ayz_auth/db/entitlements_loader.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/db/entitlements_loader.py)
- [src/ayz_auth/db/mongo_client.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/db/mongo_client.py)
- [src/ayz_auth/models/context.py](https://github.com/brandsoulmates/ayz-auth/blob/main/src/ayz_auth/models/context.py)

### Key Files in soulmates-app-backend
- [app/api/sessions.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/api/sessions.py)
- [app/core/team_validation.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/core/team_validation.py)
- [app/core/stytch_auth.py](https://github.com/brandsoulmates/soulmates-app-backend/blob/main/app/core/stytch_auth.py)

### Key Files in soulmates-app (Frontend)
- [app/routes/app-layout.tsx](../../app/routes/app-layout.tsx)
- [app/contexts/TeamContext.tsx](../../app/contexts/TeamContext.tsx)
- [app/routes/api/teams/user.$userId.tsx](../../app/routes/api/teams/user.$userId.tsx)
- [app/lib/services/server/membershipService.ts](../../app/lib/services/server/membershipService.ts)

### Related Documentation
- [Multi-Org Team Context Fix Solution](./solution.md)
- [Membership Service Architecture](../../docs/membership/)
- [Authentication Flows](../../docs/auth/)
