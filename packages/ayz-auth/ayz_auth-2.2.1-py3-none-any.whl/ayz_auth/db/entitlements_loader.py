"""
Entitlements and team context data loader.

Orchestrates loading of organization entitlements, user context, and team data
from MongoDB with Redis caching.
"""

from typing import Any, Dict, Optional

from ..cache.redis_client import redis_client
from ..utils.logger import logger
from .mongo_client import mongo_client


class EntitlementsLoader:
    """
    Loads entitlements and team context data with caching.

    Provides a high-level interface for loading organization entitlements,
    user context, and team details with intelligent caching strategies.
    """

    async def load_organization_entitlements(
        self, stytch_org_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load organization entitlements with 1-hour caching.

        Args:
            stytch_org_id: Stytch organization identifier

        Returns:
            Dict containing:
                - entitlements: List[str]
                - subscription_tier: str
                - subscription_limits: Dict[str, int]
                - mongo_organization_id: str (MongoDB ObjectId as string)
            Returns None if MongoDB is not configured or organization not found
        """
        try:
            # Try cache first
            cached_data = await redis_client.get_cached_organization_entitlements(
                stytch_org_id
            )
            if cached_data:
                logger.debug(
                    f"Using cached organization entitlements for org: {stytch_org_id}"
                )
                return cached_data

            # Fallback to MongoDB
            org_doc = await mongo_client.get_organization(stytch_org_id)
            if not org_doc:
                logger.debug(
                    f"Organization not found in MongoDB for org: {stytch_org_id}"
                )
                return None

            # Extract entitlements data
            raw_id = org_doc.get("_id")
            entitlements_data = {
                "entitlements": org_doc.get("entitlements", []),
                "subscription_tier": org_doc.get("subscription_tier"),
                "subscription_limits": org_doc.get("subscription_limits", {}),
                "mongo_organization_id": str(raw_id) if raw_id is not None else None,
            }

            # Cache for 1 hour
            await redis_client.cache_organization_entitlements(
                stytch_org_id, entitlements_data
            )

            logger.debug(
                f"Loaded organization entitlements from MongoDB for org: {stytch_org_id}"
            )
            return entitlements_data

        except Exception as e:
            logger.warning(
                f"Failed to load organization entitlements: {str(e)}. "
                f"Continuing without entitlements data."
            )
            return None

    async def load_user_context(
        self, stytch_member_id: str, stytch_org_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load user context with team information.

        Caches mongo_user_id for 1 hour, but team context (current_team_id,
        current_team_name) is always loaded fresh from MongoDB.

        Args:
            stytch_member_id: Stytch member identifier
            stytch_org_id: Optional Stytch organization identifier for team validation

        Returns:
            Dict containing:
                - current_team_id: str (MongoDB ObjectId as string) or None
                - current_team_name: str or None
                - mongo_user_id: str (MongoDB ObjectId as string)
            Returns None if MongoDB is not configured or user not found
        """
        try:
            # Try cache first for mongo_user_id (org-scoped if org_id provided)
            cached_mongo_user_id = await redis_client.get_cached_user_context(
                stytch_member_id, stytch_org_id
            )
            if cached_mongo_user_id:
                logger.debug(
                    f"Using cached mongo_user_id for member: {stytch_member_id}"
                    + (f" in org: {stytch_org_id}" if stytch_org_id else "")
                )

            # Fallback to MongoDB
            # Pass org context for multi-org user lookup
            user_doc = await mongo_client.get_user(stytch_member_id, stytch_org_id)
            if not user_doc:
                logger.debug(
                    f"User not found in MongoDB for member: {stytch_member_id}"
                )
                return None

            # Extract user context
            current_team_id = user_doc.get("current_team_id")
            # Get ObjectId from user_doc for MongoDB operations
            user_object_id = user_doc.get("_id")
            # Use cached mongo_user_id string if available, otherwise convert ObjectId to string
            mongo_user_id_str = (
                cached_mongo_user_id
                if cached_mongo_user_id
                else str(user_object_id) if user_object_id else None
            )

            # Validate team belongs to current organization (if org context provided)
            validated_team_id = None
            team_name = None

            if current_team_id and stytch_org_id:
                # Validate team belongs to the current organization
                validated_team_id = await self._validate_team_belongs_to_org(
                    current_team_id, stytch_org_id, stytch_member_id
                )

                if validated_team_id:
                    team_name = await self._load_team_name(validated_team_id)
            elif current_team_id:
                # No org context - use team_id as-is (backwards compatibility)
                validated_team_id = str(current_team_id)
                team_name = await self._load_team_name(current_team_id)

            # If no valid team found and org context provided, get first team in org
            if not validated_team_id and stytch_org_id:
                validated_team_id = await self._get_first_team_in_org(
                    stytch_member_id, stytch_org_id
                )
                if validated_team_id:
                    team_name = await self._load_team_name(validated_team_id)

                    # Auto-correct stale MongoDB value
                    await self._update_user_current_team(
                        user_object_id, validated_team_id
                    )

            user_context = {
                "current_team_id": validated_team_id,
                "current_team_name": team_name,
                "mongo_user_id": mongo_user_id_str,
            }

            # Cache mongo_user_id for 1 hour if not already cached (org-scoped if org_id provided)
            if not cached_mongo_user_id:
                await redis_client.cache_user_context(
                    stytch_member_id, user_context, stytch_org_id
                )

            logger.debug(
                f"Loaded user context from MongoDB for member: {stytch_member_id}"
                + (f" in org: {stytch_org_id}" if stytch_org_id else "")
            )
            return user_context

        except Exception as e:
            logger.warning(
                f"Failed to load user context: {str(e)}. "
                f"Continuing without user context data."
            )
            return None

    async def _load_team_name(self, team_id: Any) -> Optional[str]:
        """
        Load team name by team ID.

        Args:
            team_id: MongoDB ObjectId of the team

        Returns:
            Team name if found, None otherwise
        """
        try:
            team_doc = await mongo_client.get_team(team_id)
            if team_doc:
                return team_doc.get("name")
            return None

        except Exception as e:
            logger.warning(f"Failed to load team name: {str(e)}")
            return None

    async def _validate_team_belongs_to_org(
        self, team_id: Any, stytch_org_id: str, stytch_member_id: str
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
                logger.debug(f"Team {team_id} validated for org {stytch_org_id}")
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
        self, stytch_member_id: str, stytch_org_id: str
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
            # Get user document (pass org context for multi-org user lookup)
            user_doc = await mongo_client.get_user(stytch_member_id, stytch_org_id)
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
            memberships = (
                await db["user_team_memberships"]
                .find({"user_id": user_id, "status": "active"})
                .to_list(length=100)
            )

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

    async def _update_user_current_team(self, user_id: Any, team_id: str) -> None:
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
                {"_id": user_id}, {"$set": {"current_team_id": team_object_id}}
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

    async def load_complete_session_data(
        self, stytch_org_id: str, stytch_member_id: str
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
        # Load organization entitlements and user context in parallel
        import asyncio

        org_data_task = self.load_organization_entitlements(stytch_org_id)
        # Pass organization context to user context loader for team validation
        user_data_task = self.load_user_context(stytch_member_id, stytch_org_id)

        org_data, user_data = await asyncio.gather(
            org_data_task, user_data_task, return_exceptions=True
        )

        # Handle exceptions from parallel loading
        if isinstance(org_data, Exception):
            logger.warning(f"Exception loading organization data: {org_data}")
            org_data = None

        if isinstance(user_data, Exception):
            logger.warning(f"Exception loading user data: {user_data}")
            user_data = None

        # Combine results with safe defaults
        return {
            # Organization entitlements (default to None if not available)
            "entitlements": org_data.get("entitlements") if org_data else None,
            "subscription_tier": (
                org_data.get("subscription_tier") if org_data else None
            ),
            "subscription_limits": (
                org_data.get("subscription_limits") if org_data else None
            ),
            "mongo_organization_id": (
                org_data.get("mongo_organization_id") if org_data else None
            ),
            # User context (default to None if not available)
            "current_team_id": user_data.get("current_team_id") if user_data else None,
            "current_team_name": (
                user_data.get("current_team_name") if user_data else None
            ),
            "mongo_user_id": user_data.get("mongo_user_id") if user_data else None,
        }


# Global entitlements loader instance
entitlements_loader = EntitlementsLoader()
