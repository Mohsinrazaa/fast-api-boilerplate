import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.jwt import verify_access_token
from app.utils.response import error_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """ Middleware to enforce authentication on protected routes.
        Checks for a valid JWT in the Authorization header.
        Attaches user info to request.state.user if valid.
        Public routes are exempt from authentication.
    """
    async def dispatch(self, request: Request, call_next):
        """Middleware to enforce authentication on protected routes."""
        try:
            logger.info(f"Request path: {request.url.path}")
            public_routes = [
                '/', "/auth/login", "/auth/signup", "/auth/google",
                "/auth/google/callback", "/docs", "/openapi.json",
                '/auth/forgot-password', '/auth/reset-password',
                '/otp/verify', '/otp/generate', '/users'
            ]
            if request.url.path in public_routes or request.method == "OPTIONS":
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Unauthorized: Missing or invalid Authorization header")

            token = auth_header.split(" ")[1]
            user = verify_access_token(token)
            request.state.user = user  

            return await call_next(request)

        except HTTPException as http_exc:
            logger.warning(f"AuthMiddleware HTTPException: {http_exc.detail}")
            return error_response(http_exc.status_code, http_exc.detail)
        except Exception as e:
            logger.error(f"AuthMiddleware error: {str(e)}")
            return error_response(500, "Internal Server Error. Please contact support.")