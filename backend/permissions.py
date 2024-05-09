# permissions.py

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from token_manager import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def role_required(role_permissions: dict):
    def decorator(func):
        async def wrapper(token: str = Depends(oauth2_scheme), *args, **kwargs):
            decoded_token = decode_access_token(token)
            user_role = decoded_token.get('role') if decoded_token else None
            user_username = decoded_token.get('sub') if decoded_token else None
            
            if user_role in role_permissions:
                permission_condition = role_permissions[user_role]
                # Evaluate the condition, if it's callable
                if callable(permission_condition):
                    if not permission_condition(user_username, *args, **kwargs):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions"
                        )
                # Allow access if the role matches and no additional conditions are required
                return await func(*args, **kwargs)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role not allowed"
                )
        return wrapper
    return decorator
