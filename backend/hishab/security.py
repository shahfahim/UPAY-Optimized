import threading
"""
Security Module for Hishab AI Copilot
Handles rate limiting and PII (Personally Identifiable Information) stripping to ensure financial data security.
"""

import time
import re
from typing import Dict, List

class RateLimiter:
    """
    Robust in-memory rate limiter to prevent API spam.
    Uses a sliding window approach with timestamps to track requests per client.
    """
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed within the time window.
            window_seconds: Time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Mapping from client_id (e.g., IP address or user ID) to a list of request timestamps
        self._requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if the client is allowed to make a request based on their recent activity.
        
        Args:
            client_id: Unique identifier for the client (IP or user ID).
            
        Returns:
            True if the request is allowed, False if rate limited.
        """
        current_time = time.time()
        
        with self._lock:
            if client_id not in self._requests:
                self._requests[client_id] = [current_time]
                return True
                
            # Clean up old requests outside the current window
            self._requests[client_id] = [
                req_time for req_time in self._requests[client_id] 
                if current_time - req_time <= self.window_seconds
            ]
            
            if len(self._requests[client_id]) < self.max_requests:
                self._requests[client_id].append(current_time)
                return True
                
            return False
        
    def get_remaining_requests(self, client_id: str) -> int:
        """
        Returns the number of requests left for a client in the current window.
        """
        if client_id not in self._requests:
            return self.max_requests
            
        current_time = time.time()
        # Count only valid requests within the window
        valid_requests = [
            req_time for req_time in self._requests[client_id] 
            if current_time - req_time <= self.window_seconds
        ]
        return max(0, self.max_requests - len(valid_requests))

def PII_Stripper(text: str) -> str:
    """
    Removes sensitive Personally Identifiable Information (PII) from strings.
    Specifically targets:
    - Phone numbers (e.g., Bangladeshi format +88017..., 017...)
    - PINs (4 to 6 digit standalone sequences)
    
    Args:
        text: The input string potentially containing PII.
        
    Returns:
        The sanitized string with PII replaced by redaction tags.
    """
    if not text:
        return text
        
    # Pattern for BD phone numbers: optional +88 or 88, followed by 11 digits starting with 01
    # Example: +8801712345678, 01712345678, 8801712345678
    phone_pattern = re.compile(r'(?<!\d)(?:\+?88)?01[3-9]\d{8}(?!\d)')

    # PINs/OTPs only when a keyword names them, so plain amounts ("5000 tk") are kept
    pin_pattern = re.compile(r'(?i)((?:pin|পিন|otp|password|pass(?:word)?)\s*(?:is|:|=|হলো|হল|holo)?\s*)[0-9০-৯]{4,6}(?![0-9০-৯])')

    # Replace PII with masks
    masked_text = phone_pattern.sub('[PHONE_REDACTED]', text)
    masked_text = pin_pattern.sub(lambda m: m.group(1) + '[PIN_REDACTED]', masked_text)

    return masked_text
