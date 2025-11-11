# gptquery\processing\throttling.py

"""
Throttling strategies for API rate limiting.
"""
import time

class SimpleThrottler:
    """
    Basic time-based throttling with fixed delays between requests.
    """
    
    def __init__(self, rpm: int = 50):
        """
        Initialize throttler.
        
        Args:
            rpm: Requests per minute limit
        """
        self.rpm = rpm
        self.delay = 60.0 / rpm if rpm > 0 else 0
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        if self.delay <= 0:
            return
            
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

class AdaptiveThrottler:
    """
    Adaptive throttling that adjusts based on API responses.
    """
    
    def __init__(self, initial_rpm: int = 50, min_rpm: int = 10, max_rpm: int = 100):
        """
        Initialize adaptive throttler.
        
        Args:
            initial_rpm: Starting requests per minute
            min_rpm: Minimum RPM (when slowing down)
            max_rpm: Maximum RPM (when speeding up)
        """
        self.current_rpm = initial_rpm
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.delay = 60.0 / initial_rpm
        self.consecutive_successes = 0
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait and adapt based on success rate."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()
    
    def handle_rate_limit(self):
        """Call this when a rate limit is hit."""
        # Slow down
        self.current_rpm = max(self.min_rpm, self.current_rpm * 0.5)
        self.delay = 60.0 / self.current_rpm
        self.consecutive_successes = 0
    
    def handle_success(self):
        """Call this when a request succeeds."""
        self.consecutive_successes += 1
        # Speed up gradually after 10 consecutive successes
        if self.consecutive_successes >= 10:
            self.current_rpm = min(self.max_rpm, self.current_rpm * 1.1)
            self.delay = 60.0 / self.current_rpm
            self.consecutive_successes = 0

class TokenBucketThrottler:
    """
    Token bucket algorithm allowing bursts when tokens are available.
    Supports both requests per minute (RPM) and tokens per minute (TPM) limits.
    """

    def __init__(self, rpm: int = 4000, tpm: int = 4_000_000, burst_size: int = 10):
        """
        Initialize token bucket throttler.

        Args:
            rpm: Token refill rate (requests per minute)
            tpm: Token consumption limit (tokens per minute)
            burst_size: Maximum tokens in bucket (burst capacity)
        """
        self.rpm = rpm
        self.tpm = tpm
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self.refill_rate = rpm / 60.0  # tokens (requests) per second
        self.token_usage = 0  # tokens used in current minute
        self.token_usage_reset_time = time.time()

    def wait_if_needed(self, tokens_needed: int = 1):
        """Wait if no tokens available or token limit exceeded."""
        self._refill_tokens()
        self._reset_token_usage_if_needed()

        # Check if enough tokens (requests) are available
        while self.tokens < tokens_needed or (self.token_usage + tokens_needed) > self.tpm:
            # Wait for next token refill or token usage reset
            wait_time = max(1.0 / self.refill_rate, self.token_usage_reset_time + 60 - time.time())
            if wait_time > 0:
                time.sleep(wait_time)
            self._refill_tokens()
            self._reset_token_usage_if_needed()

        self.tokens -= tokens_needed
        self.token_usage += tokens_needed

    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.burst_size, self.tokens + new_tokens)
        self.last_refill = now

    def _reset_token_usage_if_needed(self):
        """Reset token usage counter every 60 seconds."""
        now = time.time()
        if now - self.token_usage_reset_time >= 60:
            self.token_usage = 0
            self.token_usage_reset_time = now

