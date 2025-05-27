"""
Middleware for limiting request rate per IP.
"""

import redis
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from config.security_settings import security_settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for limiting request rate per IP.
    Uses Redis as storage for counters.
    """
    
    def __init__(
        self,
        app,
        redis_url=None,
        rate_limit_paths=None,
        rate_limit=None,
        time_window=None,
    ):
        """
        Initializes the rate limiting middleware.
        
        Args:
            app: The FastAPI app instance
            redis_url: Redis connection URL
            rate_limit_paths: List of paths to protect
            rate_limit: Maximum number of requests
            time_window: Time window in seconds
        """
        super().__init__(app)
        
        self.redis_url = security_settings.REDIS_URL
        self.redis = redis.from_url(self.redis_url)
        self.rate_limit = security_settings.RATE_LIMIT_DEFAULT
        self.time_window = security_settings.RATE_LIMIT_WINDOW
        self.rate_limit_paths = security_settings.RATE_LIMIT_PATHS
        
        logger.info(f"Rate limit middleware initialized: {self.rate_limit} requests per {self.time_window} seconds")
    
    async def dispatch(self, request: Request, call_next):
        """
        Processes the request and applies rate limiting if necessary.
        
        Args:
            request: The HTTP request
            call_next: The next function in the request pipeline
            
        Returns:
            The HTTP response or an error response if the limit is exceeded
        """
        client_ip = request.client.host
        path = request.url.path
        
        if any(path.startswith(limit_path) for limit_path in self.rate_limit_paths):
            key = f"rate_limit:{path}:{client_ip}"
            
            # Check if the client has exceeded the limit
            try:
                # Get the current request count
                requests = int(self.redis.get(key) or 0)
                
                # If the limit is exceeded, return error 429
                if requests >= self.rate_limit:
                    logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {requests} requests")
                    
                    # Calculate remaining time to reset
                    ttl = self.redis.ttl(key)
                    
                    return HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many requests. Try again in {ttl} seconds.",
                        headers={"Retry-After": str(ttl)}
                    ).response
                
                # Increment the counter and set TTL if it's new
                pipe = self.redis.pipeline()
                pipe.incr(key)
                if requests == 0:
                    pipe.expire(key, self.time_window)
                pipe.execute()
                
            except redis.RedisError as e:
                logger.error(f"Redis error in rate limiting: {str(e)}")
        
        # Proceed with the request
        response = await call_next(request)
        return response
