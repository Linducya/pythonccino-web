from fastapi import HTTPException, status

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token - Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )