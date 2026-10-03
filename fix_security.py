import threading
import re

with open('backend/hishab/security.py', 'r', encoding='utf-8') as f:
    code = f.read()

if 'import threading' not in code:
    code = 'import threading\n' + code

code = code.replace('self._requests: Dict[str, List[float]] = {}', 'self._requests: Dict[str, List[float]] = {}\n        self._lock = threading.Lock()')

old_is_allowed = '''    def is_allowed(self, client_id: str) -> bool:
        \"\"\"
        Check if the client is allowed to make a request based on their recent activity.
        
        Args:
            client_id: Unique identifier for the client (IP or user ID).
            
        Returns:
            True if the request is allowed, False if rate limited.
        \"\"\"
        current_time = time.time()
        
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
            
        return False'''

new_is_allowed = '''    def is_allowed(self, client_id: str) -> bool:
        \"\"\"
        Check if the client is allowed to make a request based on their recent activity.
        
        Args:
            client_id: Unique identifier for the client (IP or user ID).
            
        Returns:
            True if the request is allowed, False if rate limited.
        \"\"\"
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
                
            return False'''

code = code.replace(old_is_allowed, new_is_allowed)
code = code.replace("phone_pattern = re.compile(r'(?:\+?88)?01[3-9]\d{8}')", "phone_pattern = re.compile(r'\\\\b(?:\\\\+?88)?01[3-9]\\\\d{8}\\\\b')")

with open('backend/hishab/security.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Security fixed')
