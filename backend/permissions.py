# permissions.py

from fastapi import HTTPException, status
from functools import wraps
from token_manager import decode_access_token, ExpiredTokenError, InvalidTokenError

class RolePermissionError(Exception):
    """Base class for role permission errors."""
    pass

class RoleNotFoundError(RolePermissionError):
    """Raised when the role is not found in the roles_permissions dictionary."""
    pass

class PermissionDeniedError(RolePermissionError):
    """Raised when the permission check fails."""
    pass


def validate_user_token(token: str):
    if token.startswith('Bearer '):
        token = token[7:]
    try:
        payload = decode_access_token(token)
    except ExpiredTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token has expired: {str(e)}")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    user = payload.get("sub")
    role = payload.get("role")
    if not user or not role:
        raise HTTPException(status_code=401, detail="Invalid token: no user or role")
    return user, role

def validate_user(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        token = request.headers.get('Authorization')
        try:
            user, role = validate_user_token(token)
        except HTTPException as e:
            raise e
        
        request.state.user = user
        request.state.role = role
        return await f(*args, **kwargs)
    return wrapper



def check_role_permissions(role: str, roles_permissions: dict, user: str, **kwargs):
    try:
        if role not in roles_permissions:
            raise RoleNotFoundError(f"Role '{role}' not found in permissions.")
        
        condition = roles_permissions[role]
        if condition is None or condition(user, **kwargs):
            return True
        else:
            raise PermissionDeniedError(f"Permission denied for user '{user}' with role '{role}'.")
    except RoleNotFoundError as e:
        raise e
    except PermissionDeniedError as e:
        raise e
    except Exception as e:
        raise RolePermissionError(f"An unexpected error occurred: {str(e)}")

def role_required(roles_permissions: dict):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            role = request.state.role
            user = request.state.user
            try:
                if not check_role_permissions(role, roles_permissions, user, **kwargs):
                    raise PermissionDeniedError(f"Permission denied for user '{user}' with role '{role}'.")
            except RoleNotFoundError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            except PermissionDeniedError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            except RolePermissionError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            
            return await f(*args, **kwargs)
        return wrapper
    return decorator
