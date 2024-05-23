# permissions.py

from fastapi import HTTPException, status
from functools import wraps
from jose import jwt
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

# def validate_user(f):
#     '''
#     validate_user is a decorator that checks if the user is authenticated and has a valid token.
#     If the token is valid, the user and role are added to the request state.

#     Args:
#         f (__function__): The function to be wrapped

#     Raises:
#         HTTPException 401: If the token is invalid

#     Returns:
#         __function__: The wrapped function if the token is valid with the user and role added to the request state
#     '''
#     @wraps(f)
#     async def wrapper(*args, **kwargs):
#         request = kwargs.get('request')
#         token = request.headers.get('Authorization')
#         if token.startswith('Bearer '):
#             token = token[7:]
#         try:
#             payload = decode_access_token(token)
#             user: str = payload.get("sub")
#             role: str = payload.get("role")
            
#             if not role or not user:
#                 raise HTTPException(status_code=401, detail="Invalid token")
#             request.state.role = role
#             request.state.user = user

#             return await f(*args, **kwargs)
#         except jwt.JWTError:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     return wrapper


# def role_required(roles_permissions: dict):
#     '''
#     role_required is a decorator that checks if the user has the required role to access the endpoint.
#     The roles_permissions dictionary contains the role as the key and a condition function as the value.
#     If the role is in the dictionary and the condition function is met, the function is executed.
#     role and user are defined from the request state and reference the jwt from the header of a request.

#     Args:
#         roles_permissions (dict): A dictionary with the role as the key and a condition function as the value
    
#     Raises:
#         HTTPException 403: If the user does not have the required role
    
#     Returns:
#         __function__: The wrapped function if the user has the required role and condition function is met
#     '''
#     def decorator(f):
#         @wraps(f)
#         async def wrapper(*args, **kwargs):
#             request = kwargs.get('request')
#             role = request.state.role
#             user = request.state.user
#             try:
#                 if role in roles_permissions.keys():
#                     condition = roles_permissions[role]
#                     if condition is None or condition(user, **kwargs):
#                         return await f(*args, **kwargs)
#             except Exception as e:
#                 print(e)
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Forbidden {e}')

#         return wrapper
#     return decorator

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
