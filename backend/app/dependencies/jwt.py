from fastapi import Request, HTTPException
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from app.core.config import settings


def get_current_mechanic_id_from_cookie(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(status_code=401, detail="Token missing")
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        mechanic_id: int = int(payload.get("sub"))

        if not mechanic_id:
            raise  HTTPException(status_code=401, detail="Invalid token")
        return mechanic_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")