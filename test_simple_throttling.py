#!/usr/bin/env python3
"""
Simple test script for the in-memory throttling system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.throttling_service import throttling_service
from datetime import datetime

def test_basic_throttling():
    """Test basic throttling functionality."""
    app = create_app()
    
    with app.app_context():
        print("=== Testing Basic Throttling ===")
        
        # Test IP throttling
        test_ip = "192.168.1.100"
        test_email = "test@example.com"
        
        # Should not be throttled initially
        is_throttled, message = throttling_service.check_throttling(test_ip, 'ip', 'initiate_auth')
        print(f"Initial IP check: throttled={is_throttled}, message={message}")
        assert not is_throttled, "Should not be throttled initially"
        
        # Record some attempts
        for i in range(3):
            throttling_service.record_attempt(test_ip, 'ip', 'initiate_auth')
            print(f"Recorded attempt {i+1}")
        
        # Should still not be throttled (under limit)
        is_throttled, message = throttling_service.check_throttling(test_ip, 'ip', 'initiate_auth')
        print(f"After 3 attempts: throttled={is_throttled}, message={message}")
        assert not is_throttled, "Should not be throttled after 3 attempts"
        
        # Record more attempts to trigger throttling
        for i in range(3):
            throttling_service.record_attempt(test_ip, 'ip', 'initiate_auth')
            print(f"Recorded attempt {i+4}")
        
        # Should now be throttled
        is_throttled, message = throttling_service.check_throttling(test_ip, 'ip', 'initiate_auth')
        print(f"After 6 attempts: throttled={is_throttled}, message={message}")
        assert is_throttled, "Should be throttled after 6 attempts"
        
        print("✓ Basic throttling test passed")

def test_email_throttling():
    """Test email-based throttling."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Testing Email Throttling ===")
        
        test_email = "user@example.com"
        
        # Should not be throttled initially
        is_throttled, message = throttling_service.check_throttling(test_email, 'email', 'verify_code')
        print(f"Initial email check: throttled={is_throttled}, message={message}")
        assert not is_throttled, "Should not be throttled initially"
        
        # Record attempts to trigger throttling
        for i in range(12):  # More than the 10 limit for verify_code
            throttling_service.record_attempt(test_email, 'email', 'verify_code')
            print(f"Recorded verify attempt {i+1}")
        
        # Should now be throttled
        is_throttled, message = throttling_service.check_throttling(test_email, 'email', 'verify_code')
        print(f"After 12 attempts: throttled={is_throttled}, message={message}")
        assert is_throttled, "Should be throttled after 12 attempts"
        
        print("✓ Email throttling test passed")

def test_reset_functionality():
    """Test reset functionality."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Testing Reset Functionality ===")
        
        test_ip = "10.0.0.100"
        
        # Record some attempts
        for i in range(3):
            throttling_service.record_attempt(test_ip, 'ip', 'initiate_auth')
        
        # Reset attempts
        throttling_service.reset_attempts(test_ip, 'ip', 'initiate_auth')
        
        # Should not be throttled after reset
        is_throttled, message = throttling_service.check_throttling(test_ip, 'ip', 'initiate_auth')
        print(f"After reset: throttled={is_throttled}, message={message}")
        assert not is_throttled, "Should not be throttled after reset"
        
        print("✓ Reset functionality test passed")

def test_ip_detection():
    """Test IP detection functionality."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Testing IP Detection ===")
        
        # Test private IP detection
        private_ips = ["127.0.0.1", "192.168.1.1", "10.0.0.1", "172.16.0.1"]
        for ip in private_ips:
            is_private = throttling_service.is_private_ip(ip)
            print(f"{ip}: private={is_private}")
            assert is_private, f"{ip} should be detected as private"
        
        # Test public IP detection
        public_ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        for ip in public_ips:
            is_private = throttling_service.is_private_ip(ip)
            print(f"{ip}: private={is_private}")
            assert not is_private, f"{ip} should be detected as public"
        
        print("✓ IP detection test passed")

def test_stats():
    """Test statistics functionality."""
    app = create_app()
    
    with app.app_context():
        print("\n=== Testing Statistics ===")
        
        # Clear any existing data
        throttling_service.attempts.clear()
        
        # Record some attempts
        throttling_service.record_attempt("test1@example.com", "email", "initiate_auth")
        throttling_service.record_attempt("test2@example.com", "email", "initiate_auth")
        throttling_service.record_attempt("192.168.1.100", "ip", "initiate_auth")
        
        stats = throttling_service.get_stats()
        print(f"Stats: {stats}")
        
        assert stats['total_attempts'] == 3, f"Expected 3 attempts, got {stats['total_attempts']}"
        assert stats['unique_identifiers'] == 3, f"Expected 3 unique identifiers, got {stats['unique_identifiers']}"
        
        print("✓ Statistics test passed")

if __name__ == "__main__":
    print("Running simple throttling system tests...")
    
    try:
        test_basic_throttling()
        test_email_throttling()
        test_reset_functionality()
        test_ip_detection()
        test_stats()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 