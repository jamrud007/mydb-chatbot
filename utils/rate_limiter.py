"""
Rate Limiter using Token Bucket Algorithm
"""
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, max_requests=10, time_window=60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.buckets = defaultdict(lambda: {
            'tokens': max_requests,
            'last_update': time.time()
        })
        logger.info(f"RateLimiter initialized: {max_requests} requests per {time_window}s")
    
    def _refill_bucket(self, user_id):
        """
        Refill tokens in the bucket based on elapsed time
        
        Args:
            user_id: User identifier
        """
        bucket = self.buckets[user_id]
        current_time = time.time()
        elapsed = current_time - bucket['last_update']
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = (elapsed / self.time_window) * self.max_requests
        bucket['tokens'] = min(self.max_requests, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = current_time
    
    def is_allowed(self, user_id='default'):
        """
        Check if request is allowed for user
        
        Args:
            user_id: User identifier
        
        Returns:
            tuple: (allowed: bool, retry_after: float)
        """
        self._refill_bucket(user_id)
        bucket = self.buckets[user_id]
        
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            logger.debug(f"Request allowed for {user_id}. Remaining tokens: {bucket['tokens']:.2f}")
            return True, 0
        else:
            # Calculate retry after time
            retry_after = self.time_window * (1 - bucket['tokens']) / self.max_requests
            logger.warning(f"Rate limit exceeded for {user_id}. Retry after: {retry_after:.2f}s")
            return False, retry_after
    
    def get_remaining_requests(self, user_id='default'):
        """
        Get remaining requests for user
        
        Args:
            user_id: User identifier
        
        Returns:
            int: Number of remaining requests
        """
        self._refill_bucket(user_id)
        return int(self.buckets[user_id]['tokens'])
    
    def reset(self, user_id='default'):
        """
        Reset rate limit for user
        
        Args:
            user_id: User identifier
        """
        if user_id in self.buckets:
            del self.buckets[user_id]
            logger.info(f"Rate limit reset for {user_id}")
