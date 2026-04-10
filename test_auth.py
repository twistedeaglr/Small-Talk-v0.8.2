"""
Test script for the authentication system.
"""

from user_manager import UserManager


def test_authentication():
    """Test user registration and login."""
    print("=== User Authentication System Test ===\n")
    
    user_manager = UserManager()
    
    # Test 1: Register a user
    print("1. Testing user registration:")
    success, message = user_manager.register("alice", "password123")
    print(f"   Register 'alice': {message}")
    assert success, "Registration should succeed"
    
    # Test 2: Try to register with same username
    print("\n2. Testing duplicate username prevention:")
    success, message = user_manager.register("alice", "different")
    print(f"   Register 'alice' again: {message}")
    assert not success, "Duplicate registration should fail"
    
    # Test 3: Password too short
    print("\n3. Testing password validation:")
    success, message = user_manager.register("bob", "short")
    print(f"   Register 'bob' with short password: {message}")
    assert not success, "Short password should be rejected"
    
    # Test 4: Successful login
    print("\n4. Testing successful login:")
    success, message = user_manager.register("charlie", "password456")
    success, message = user_manager.login("charlie", "password456")
    print(f"   Login 'charlie' with correct password: {message}")
    assert success, "Login should succeed with correct password"
    
    # Test 5: Failed login with wrong password
    print("\n5. Testing failed login with wrong password:")
    success, message = user_manager.login("charlie", "wrongpassword")
    print(f"   Login 'charlie' with wrong password: {message}")
    assert not success, "Login should fail with wrong password"
    
    # Test 6: Failed login with nonexistent user
    print("\n6. Testing failed login with nonexistent user:")
    success, message = user_manager.login("nonexistent", "password")
    print(f"   Login 'nonexistent': {message}")
    assert not success, "Login should fail for nonexistent user"
    
    # Test 7: Change password
    print("\n7. Testing password change:")
    success, message = user_manager.change_password("charlie", "password456", "newpassword789")
    print(f"   Change password: {message}")
    assert success, "Password change should succeed"
    
    # Test 8: Login with new password
    success, message = user_manager.login("charlie", "newpassword789")
    print(f"   Login with new password: {message}")
    assert success, "Should be able to login with new password"
    
    # Test 9: User exists check
    print("\n8. Testing user existence check:")
    exists = user_manager.user_exists("alice")
    print(f"   'alice' exists: {exists}")
    assert exists, "alice should exist"
    
    not_exists = user_manager.user_exists("nobody")
    print(f"   'nobody' exists: {not_exists}")
    assert not not_exists, "nobody should not exist"
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    test_authentication()
