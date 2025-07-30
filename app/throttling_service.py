from datetime import datetime, timedelta
from flask import request, current_app
import ipaddress
from collections import defaultdict
import threading

class InMemoryThrottlingService:
    """Simple in-memory throttling service for both user and IP-based protection."""
    
    def __init__(self):
        self.attempts = defaultdict(list)  # key: (identifier, identifier_type, action)
        self.lock = threading.Lock()
        
        # Configuration
        self.config = {
            'initiate_auth': {
                'max_attempts': 5,
                'window_minutes': 60,
                'block_minutes': 30
            },
            'verify_code': {
                'max_attempts': 10,
                'window_minutes': 60,
                'block_minutes': 60
            }
        }
    
    def get_client_ip(self):
        """Get the real client IP address, handling proxies."""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_private_ip(self, ip):
        """Check if an IP address is private/internal."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    def should_skip_throttling(self, ip):
        """Determine if throttling should be skipped for this IP."""
        if self.is_private_ip(ip):
            current_app.logger.debug(f"Skipping throttling for private IP: {ip}")
            return True
        return False
    
    def _get_key(self, identifier, identifier_type, action):
        """Get the key for storing attempts."""
        return (identifier, identifier_type, action)
    
    def _cleanup_old_attempts(self, key):
        """Remove attempts older than the window."""
        if key not in self.attempts:
            return
        
        config = self.config.get(key[2], self.config['initiate_auth'])
        window_start = datetime.utcnow() - timedelta(minutes=config['window_minutes'])
        
        with self.lock:
            self.attempts[key] = [
                attempt for attempt in self.attempts[key]
                if attempt['timestamp'] >= window_start
            ]
    
    def check_throttling(self, identifier, identifier_type, action):
        """
        Check if an identifier should be throttled.
        
        Returns:
            tuple: (is_throttled, message)
        """
        config = self.config.get(action, self.config['initiate_auth'])
        key = self._get_key(identifier, identifier_type, action)
        
        # Clean up old attempts
        self._cleanup_old_attempts(key)
        
        with self.lock:
            attempts = self.attempts[key]
            
            # Check if currently blocked
            if attempts:
                last_attempt = attempts[-1]
                if last_attempt.get('blocked_until') and last_attempt['blocked_until'] > datetime.utcnow():
                    remaining = (last_attempt['blocked_until'] - datetime.utcnow()).total_seconds()
                    minutes = int(remaining // 60)
                    seconds = int(remaining % 60)
                    return True, f"Too many attempts. Please try again in {minutes}m {seconds}s."
            
            # Check if we should be blocked based on recent attempts
            if len(attempts) >= config['max_attempts']:
                # Set block
                blocked_until = datetime.utcnow() + timedelta(minutes=config['block_minutes'])
                attempts.append({
                    'timestamp': datetime.utcnow(),
                    'blocked_until': blocked_until
                })
                
                current_app.logger.warning(
                    f"Throttling {identifier_type} {identifier} for action {action}: throttled"
                )
                return True, f"Rate limit exceeded. Please try again in {config['block_minutes']} minutes."
        
        return False, None
    
    def record_attempt(self, identifier, identifier_type, action):
        """Record an attempt for throttling purposes."""
        key = self._get_key(identifier, identifier_type, action)
        
        with self.lock:
            self.attempts[key].append({
                'timestamp': datetime.utcnow()
            })
        
        current_app.logger.info(
            f"Recorded {identifier_type} attempt: {identifier} for action {action}"
        )
    
    def reset_attempts(self, identifier, identifier_type, action):
        """Reset attempts for an identifier (e.g., after successful authentication)."""
        key = self._get_key(identifier, identifier_type, action)
        
        with self.lock:
            if key in self.attempts:
                del self.attempts[key]
        
        current_app.logger.info(
            f"Reset throttling attempts for {identifier_type} {identifier} for action {action}"
        )
    
    def check_auth_throttling(self, email=None):
        """Check throttling for authentication endpoints."""
        client_ip = self.get_client_ip()
        
        # Skip throttling for private IPs in development
        if self.should_skip_throttling(client_ip):
            return False, None
        
        # Check IP-based throttling
        is_throttled, message = self.check_throttling(client_ip, 'ip', 'initiate_auth')
        if is_throttled:
            return True, message
        
        # Check email-based throttling if email provided
        if email:
            is_throttled, message = self.check_throttling(email, 'email', 'initiate_auth')
            if is_throttled:
                return True, message
        
        return False, None
    
    def check_verify_throttling(self, email=None):
        """Check throttling for verification endpoints."""
        client_ip = self.get_client_ip()
        
        # Skip throttling for private IPs in development
        if self.should_skip_throttling(client_ip):
            return False, None
        
        # Check IP-based throttling
        is_throttled, message = self.check_throttling(client_ip, 'ip', 'verify_code')
        if is_throttled:
            return True, message
        
        # Check email-based throttling if email provided
        if email:
            is_throttled, message = self.check_throttling(email, 'email', 'verify_code')
            if is_throttled:
                return True, message
        
        return False, None
    
    def record_auth_attempt(self, email=None):
        """Record an authentication attempt."""
        client_ip = self.get_client_ip()
        
        if not self.should_skip_throttling(client_ip):
            self.record_attempt(client_ip, 'ip', 'initiate_auth')
        
        if email:
            self.record_attempt(email, 'email', 'initiate_auth')
    
    def record_verify_attempt(self, email=None):
        """Record a verification attempt."""
        client_ip = self.get_client_ip()
        
        if not self.should_skip_throttling(client_ip):
            self.record_attempt(client_ip, 'ip', 'verify_code')
        
        if email:
            self.record_attempt(email, 'email', 'verify_code')
    
    def reset_auth_attempts(self, email=None):
        """Reset authentication attempts after successful login."""
        client_ip = self.get_client_ip()
        
        if not self.should_skip_throttling(client_ip):
            self.reset_attempts(client_ip, 'ip', 'initiate_auth')
            self.reset_attempts(client_ip, 'ip', 'verify_code')
        
        if email:
            self.reset_attempts(email, 'email', 'initiate_auth')
            self.reset_attempts(email, 'email', 'verify_code')
    
    def get_stats(self):
        """Get current throttling statistics."""
        with self.lock:
            total_attempts = sum(len(attempts) for attempts in self.attempts.values())
            blocked_count = sum(
                1 for attempts in self.attempts.values()
                if attempts and attempts[-1].get('blocked_until', datetime.min) > datetime.utcnow()
            )
            
            return {
                'total_attempts': total_attempts,
                'blocked_count': blocked_count,
                'unique_identifiers': len(self.attempts)
            }

# Global instance
throttling_service = InMemoryThrottlingService() 