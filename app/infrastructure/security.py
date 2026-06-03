"""Validación de JWT para proteger los endpoints de predicción.

El token lo emite wise_auth (HS256 con JWT_SECRET compartido). Este servicio solo
verifica firma y expiración; la autorización fina (rol) la maneja wise_auth/APIM.
Falla cerrado: si no hay secreto configurado o el token es inválido/ausente, 401.
"""

from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.config import Settings

_settings = Settings()
_bearer = HTTPBearer(auto_error=False)


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    if not _settings.jwt_secret:
        # Sin secreto configurado no se puede validar nada: se rechaza por seguridad.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="auth_not_configured"
        )
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token"
        )
    try:
        return jwt.decode(
            credentials.credentials,
            _settings.jwt_secret,
            algorithms=[_settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token_expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        ) from exc
