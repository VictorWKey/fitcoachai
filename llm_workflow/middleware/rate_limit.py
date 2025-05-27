import redis
import os
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para limitar la tasa de solicitudes por IP.
    Utiliza Redis como almacenamiento para los contadores.
    """
    
    def __init__(
        self,
        app,
        redis_url=None,
        rate_limit_paths=None,
        rate_limit=5,  # solicitudes
        time_window=60,  # segundos
    ):
        super().__init__(app)
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis = redis.from_url(self.redis_url)
        self.rate_limit = rate_limit
        self.time_window = time_window

        self.rate_limit_paths = rate_limit_paths or [
            "/auth/login",
            "/auth/register",
            "/auth/forgot-password",
            "/auth/resend-verification"
        ]
        
        logger.info(f"Rate limit middleware initialized: {self.rate_limit} requests per {self.time_window} seconds")
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        
        if any(path.startswith(limit_path) for limit_path in self.rate_limit_paths):
            key = f"rate_limit:{path}:{client_ip}"
            
            try:
                requests = int(self.redis.get(key) or 0)
                
                if requests >= self.rate_limit:
                    logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {requests} requests")
                    
                    ttl = self.redis.ttl(key)
                    
                    return HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Demasiadas solicitudes. Intenta de nuevo en {ttl} segundos.",
                        headers={"Retry-After": str(ttl)}
                    ).response
                
                pipe = self.redis.pipeline()
                pipe.incr(key)
                if requests == 0:
                    pipe.expire(key, self.time_window)
                pipe.execute()
                
            except redis.RedisError as e:
                logger.error(f"Redis error in rate limiting: {str(e)}")
        
        response = await call_next(request)
        return response 