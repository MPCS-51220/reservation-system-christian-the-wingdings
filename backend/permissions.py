# permissions.py

from fastapi import HTTPException, status
from functools import wraps
from jose import jwt
from token_manager import decode_access_token

def validate_user(f):
    '''
    validate_user is a decorator that checks if the user is authenticated and has a valid token.
    If the token is valid, the user and role are added to the request state.

    Args:
        f (__function__): The function to be wrapped

    Raises:
        HTTPException 401: If the token is invalid

    Returns:
        __function__: The wrapped function if the token is valid with the user and role added to the request state
    '''
    @wraps(f)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        token = request.headers.get('Authorization')
        if token.startswith('Bearer '):
            token = token[7:]
        try:
            payload = decode_access_token(token)
            user: str = payload.get("sub")
            role: str = payload.get("role")
            
            if not role or not user:
                raise HTTPException(status_code=401, detail="Invalid token")
            request.state.role = role
            request.state.user = user

            return await f(*args, **kwargs)
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return wrapper


def role_required(roles_permissions: dict):
    '''
    role_required is a decorator that checks if the user has the required role to access the endpoint.
    The roles_permissions dictionary contains the role as the key and a condition function as the value.
    If the role is in the dictionary and the condition function is met, the function is executed.
    role and user are defined from the request state and reference the jwt from the header of a request.

    Args:
        roles_permissions (dict): A dictionary with the role as the key and a condition function as the value
    
    Raises:
        HTTPException 403: If the user does not have the required role
    
    Returns:
        __function__: The wrapped function if the user has the required role and condition function is met
    '''
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            role = request.state.role
            user = request.state.user
            try:
                if role in roles_permissions.keys():
                    condition = roles_permissions[role]
                    if condition is None or condition(user, **kwargs):
                        return await f(*args, **kwargs)
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Forbidden {e}')

        return wrapper
    return decorator
