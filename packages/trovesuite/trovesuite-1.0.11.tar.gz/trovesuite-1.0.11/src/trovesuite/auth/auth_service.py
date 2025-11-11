"""Auth Service - Business logic for user authentication and authorization"""
from datetime import datetime, timezone
from typing import Annotated
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from ..utils.helper import Helper
from ..configs.settings import db_settings
from ..configs.database import DatabaseManager
from ..configs.logging import get_logger
from ..entities.sh_response import Respons
from .auth_read_dto import AuthServiceReadDto
from .auth_write_dto import AuthServiceWriteDto
import jwt

logger = get_logger("auth_service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    """Service class for authentication and authorization operations"""

    def __init__(self) -> None:
        """Initialize the service"""
        pass
    
    @staticmethod
    def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, db_settings.SECRET_KEY, algorithms=[db_settings.ALGORITHM])
            user_id = payload.get("user_id")
            tenant_id = payload.get("tenant_id")

            if user_id is None or tenant_id is None:
                raise credentials_exception

            return {"user_id": user_id, "tenant_id": tenant_id}

        except jwt.InvalidTokenError as exc:
            raise credentials_exception from exc
        
    @staticmethod
    def authorize(data: AuthServiceWriteDto) -> Respons[AuthServiceReadDto]:

        user_id: str = data.user_id
        tenant_id: str = data.tenant_id

        """Check if a user is authorized based on login settings and roles"""
        # Input validation
        if not user_id or not isinstance(user_id, str):
            return Respons[AuthServiceReadDto](
                detail="Invalid user_id: must be a non-empty string",
                data=[],
                success=False,
                status_code=400,
                error="INVALID_USER_ID"
            )

        if not tenant_id or not isinstance(tenant_id, str):
            return Respons[AuthServiceReadDto](
                detail="Invalid tenant_id: must be a non-empty string",
                data=[],
                success=False,
                status_code=400,
                error="INVALID_TENANT_ID"
            )

        try:

            is_tenant_verified = DatabaseManager.execute_query(
                f"SELECT is_verified FROM {db_settings.MAIN_TENANTS_TABLE} WHERE delete_status = 'NOT_DELETED' AND id = %s",
                (tenant_id,),
            )

            if not is_tenant_verified or len(is_tenant_verified) == 0:
                logger.warning("Login failed - tenant not found: %s", tenant_id)
                return Respons[AuthServiceReadDto](
                    detail=f"Tenant '{tenant_id}' not found or has been deleted",
                    data=[],
                    success=False,
                    status_code=404,
                    error="TENANT_NOT_FOUND"
                )

            if not is_tenant_verified[0]['is_verified']:
                logger.warning("Login failed - tenant not verified for user: %s, tenant: %s", user_id, tenant_id)
                return Respons[AuthServiceReadDto](
                    detail=f"Tenant '{tenant_id}' is not verified. Please contact your administrator.",
                    data=[],
                    success=False,
                    status_code=403,
                    error="TENANT_NOT_VERIFIED"
                )

            # 1️⃣ Get all groups the user belongs to
            user_groups = DatabaseManager.execute_query(
                f"""SELECT group_id FROM "{tenant_id}".{db_settings.TENANT_USER_GROUPS_TABLE}
                    WHERE delete_status = 'NOT_DELETED' AND is_active = true AND user_id = %s""",(user_id,),
            )

            # 2️⃣ Prepare list of group_ids
            group_ids = [g["group_id"] for g in user_groups] if user_groups else []

            # 3️⃣ Get login settings - check user-level first, then group-level
            if group_ids:
                login_settings_details = DatabaseManager.execute_query(
                    f"""SELECT user_id, group_id, is_suspended, can_always_login,
                    is_multi_factor_enabled, is_login_before, working_days,
                    login_on, logout_on FROM "{tenant_id}".{db_settings.TENANT_LOGIN_SETTINGS_TABLE}
                    WHERE (delete_status = 'NOT_DELETED' AND is_active = true )
                    AND (user_id = %s OR group_id = ANY(%s))
                    ORDER BY user_id NULLS LAST
                    LIMIT 1""",
                    (user_id, group_ids),
                )
            else:
                login_settings_details = DatabaseManager.execute_query(
                    f"""SELECT user_id, group_id, is_suspended, can_always_login,
                    is_multi_factor_enabled, is_login_before, working_days,
                    login_on, logout_on FROM "{tenant_id}".{db_settings.TENANT_LOGIN_SETTINGS_TABLE}
                    WHERE (delete_status = 'NOT_DELETED' AND is_active = true ) AND user_id = %s""",
                    (user_id,),
                )

            if not login_settings_details or len(login_settings_details) == 0:
                logger.warning("Authorization failed - user not found: %s in tenant: %s", user_id, tenant_id)
                return Respons[AuthServiceReadDto](
                    detail=f"User '{user_id}' not found in tenant '{tenant_id}' or account is inactive",
                    data=[],
                    success=False,
                    status_code=404,
                    error="USER_NOT_FOUND"
                )

            if login_settings_details[0]['is_suspended']:
                logger.warning("Authorization failed - user suspended: %s", user_id)
                return Respons[AuthServiceReadDto](
                    detail="Your account has been suspended. Please contact your administrator.",
                    data=[],
                    success=False,
                    status_code=403,
                    error="USER_SUSPENDED"
                )

            if not login_settings_details[0]['can_always_login']:
                current_day = datetime.now().strftime("%A").upper()

                if current_day not in login_settings_details[0]['working_days']:
                    logger.warning("Authorization failed - outside working days for user: %s checking custom login period", user_id)

                    # Get current datetime (full date and time) with timezone
                    current_datetime = datetime.now(timezone.utc).replace(microsecond=0, second=0)

                    # Get from database (should already be datetime objects)
                    login_on = login_settings_details[0]['login_on']
                    logout_on = login_settings_details[0]['logout_on']

                    # Set defaults if None (with timezone awareness)
                    if not login_on:
                        login_on = datetime.min.replace(tzinfo=timezone.utc)
                    if not logout_on:
                        logout_on = datetime.max.replace(tzinfo=timezone.utc)

                    # Compare full datetime objects (both date and time)
                    if not (login_on <= current_datetime <= logout_on):
                        logger.warning("Authorization failed - outside allowed period for user: %s", user_id)
                        return Respons[AuthServiceReadDto](
                            detail="Login is not allowed at this time. Please check your access schedule.",
                            data=[],
                            success=False,
                            status_code=403,
                            error="LOGIN_TIME_RESTRICTED"
                        )

            # 4️⃣ Build query dynamically to include groups (if any) + user
            # ⚠️ CHANGED: Simplified to new schema - only select user_id, group_id, role_id, resource_type
            if group_ids:
                get_user_roles = DatabaseManager.execute_query(
                    f"""
                        SELECT DISTINCT ON (group_id, user_id, role_id)
                            group_id, user_id, role_id, resource_type
                        FROM "{tenant_id}".{db_settings.TENANT_ASSIGN_ROLES_TABLE}
                        WHERE delete_status = 'NOT_DELETED'
                        AND is_active = true
                        AND (user_id = %s OR group_id = ANY(%s))
                        ORDER BY group_id, user_id, role_id;
                    """,
                    (user_id, group_ids),
                )
            else:
                # No groups, just check roles for user
                get_user_roles = DatabaseManager.execute_query(
                    f"""
                        SELECT DISTINCT ON (user_id, role_id)
                            user_id, role_id, resource_type
                        FROM "{tenant_id}".{db_settings.TENANT_ASSIGN_ROLES_TABLE}
                        WHERE delete_status = 'NOT_DELETED'
                        AND is_active = true
                        AND user_id = %s
                        ORDER BY user_id, role_id;
                    """,
                    (user_id,),
                )

            # GET permissions and Append to Role
            get_user_roles_with_tenant_and_permissions = []
            for role in get_user_roles:
                permissions = DatabaseManager.execute_query(
                    f"""SELECT permission_id FROM {db_settings.MAIN_ROLE_PERMISSIONS_TABLE} WHERE role_id = %s""",
                    params=(role["role_id"],),)

                role_dict = {**role, "tenant_id": tenant_id, "permissions": [p['permission_id'] for p in permissions]}
                get_user_roles_with_tenant_and_permissions.append(role_dict)

            roles_dto = Helper.map_to_dto(get_user_roles_with_tenant_and_permissions, AuthServiceReadDto)

            return Respons[AuthServiceReadDto](
                detail="Authorized",
                data=roles_dto,
                success=True,
                status_code=200,
                error=None,
            )

        except HTTPException as http_ex:
            raise http_ex

        except Exception as e:
            logger.error("Authorization check failed for user: %s", str(e))
            return Respons[AuthServiceReadDto](
                detail=None,
                data=[],
                success=False,
                status_code=500,
                error="Authorization check failed due to an internal error"
            )

    @staticmethod
    def check_permission(users_data: list, action=None, resource_type=None) -> bool:
        """
        Check if user has a given permission (action).

        Args:
            users_data: List of user authorization data containing roles and permissions
            action: The permission/action to check for
            resource_type: Optional resource type filter (e.g., 'rt-user', 'rt-group')

        Returns:
            bool: True if user has the permission, False otherwise
        """
        for user_data in users_data:
            # Check resource_type if specified
            if resource_type and user_data.resource_type and user_data.resource_type != resource_type:
                continue

            # Check if the permission exists
            if action and action in user_data.permissions:
                return True

        return False
    
    @staticmethod
    def get_user_info_from_token(token: str) -> dict:
        """
        Convenience method to get user information from a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User information including user_id and tenant_id
            
        Raises:
            HTTPException: If token is invalid
        """
        return AuthService.decode_token(token)
    
    @staticmethod
    def authorize_user_from_token(token: str) -> Respons[AuthServiceReadDto]:
        """
        Convenience method to authorize a user directly from a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Respons[AuthServiceReadDto]: Authorization result with user roles and permissions
            
        Raises:
            HTTPException: If token is invalid
        """
        user_info = AuthService.decode_token(token)
        return AuthService.authorize(user_info["user_id"], user_info["tenant_id"])
    
    @staticmethod
    def get_user_permissions(user_roles: list) -> list:
        """
        Get all unique permissions for a user across all their roles.
        
        Args:
            user_roles: List of user roles from authorization
            
        Returns:
            list: Unique list of permissions
        """
        permissions = set()
        for role in user_roles:
            if role.permissions:
                permissions.update(role.permissions)
        return list(permissions)
    
    @staticmethod
    def has_any_permission(user_roles: list, required_permissions: list) -> bool:
        """
        Check if user has any of the required permissions.
        
        Args:
            user_roles: List of user roles from authorization
            required_permissions: List of permissions to check for
            
        Returns:
            bool: True if user has any of the required permissions
        """
        user_permissions = AuthService.get_user_permissions(user_roles)
        return any(perm in user_permissions for perm in required_permissions)
    
    @staticmethod
    def has_all_permissions(user_roles: list, required_permissions: list) -> bool:
        """
        Check if user has all of the required permissions.
        
        Args:
            user_roles: List of user roles from authorization
            required_permissions: List of permissions to check for
            
        Returns:
            bool: True if user has all of the required permissions
        """
        user_permissions = AuthService.get_user_permissions(user_roles)
        return all(perm in user_permissions for perm in required_permissions)
