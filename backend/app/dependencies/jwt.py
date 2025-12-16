from fastapi import Request, HTTPException
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from app.core.config import settings
import logging
logger = logging.getLogger(__name__)

def get_current_mechanic_id_from_cookie(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(status_code=401, detail="Token missing")
    try:

        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")
        try:
            mechanic_id = int(sub)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Invalid token: sub is not an integer")
        if not mechanic_id:
             raise HTTPException(status_code=401, detail="Invalid token")   
        return mechanic_id

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"CRITICAL ERROR in get_current_mechanic_id_from_cookie: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")