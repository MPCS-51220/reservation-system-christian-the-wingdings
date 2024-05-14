# token_manager.py
from datetime import datetime, timedelta, timezone
from jose import jwt


SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # Default to 15 minutes
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'decoded exp field: {decoded_token.get("exp")}')
        
        exp_timestamp = decoded_token.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        return decoded_token if exp_datetime >= datetime.now(timezone.utc) else None
    except jwt.JWTError:
        return None
