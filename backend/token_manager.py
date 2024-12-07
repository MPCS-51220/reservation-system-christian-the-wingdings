# token_manager.py
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

class TokenError(Exception):
    pass

class TokenCreationError(TokenError):
    pass

class TokenDecodeError(TokenError):
    pass

class ExpiredTokenError(TokenDecodeError):
    pass

class InvalidTokenError(TokenDecodeError):
    pass

def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # Default to 15 minutes
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise TokenCreationError(f"Failed to create token: {str(e)}")

def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = decoded_token.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if exp_datetime < datetime.now(timezone.utc):
            raise ExpiredTokenError("Token has expired")
        return decoded_token
    except ExpiredSignatureError:
        raise ExpiredTokenError("Token has expired")
    except JWTError:
        raise InvalidTokenError("Invalid token during decoding")
