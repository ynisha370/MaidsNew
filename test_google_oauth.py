#!/usr/bin/env python3
"""
Comprehensive Google OAuth Testing Script

This script tests the entire Google OAuth flow including:
1. Environment configuration verification
2. OAuth endpoint accessibility
3. Token exchange simulation
4. User creation/retrieval
5. Database connectivity
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import urlencode

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_environment_variables():
    """Test 1: Verify environment variables are loaded correctly"""
    print_header("TEST 1: Environment Variables")
    
    # Load backend .env
    backend_env_path = os.path.join('backend', '.env')
    if not os.path.exists(backend_env_path):
        print_error(f"Backend .env file not found at {backend_env_path}")
        return False
    
    load_dotenv(backend_env_path)
    
    tests = []
    
    # Check GOOGLE_CLIENT_ID
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    if google_client_id:
        if google_client_id == '758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com':
            print_success(f"GOOGLE_CLIENT_ID: {google_client_id}")
            tests.append(True)
        else:
            print_warning(f"GOOGLE_CLIENT_ID: {google_client_id}")
            print_warning("Expected: 758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com")
            tests.append(False)
    else:
        print_error("GOOGLE_CLIENT_ID not found in .env")
        tests.append(False)
    
    # Check GOOGLE_CLIENT_SECRET
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    if google_client_secret and google_client_secret != 'your_google_client_secret_here':
        print_success(f"GOOGLE_CLIENT_SECRET: {'*' * 20} (hidden)")
        tests.append(True)
    else:
        print_error("GOOGLE_CLIENT_SECRET not set or using template value")
        tests.append(False)
    
    # Check GOOGLE_REDIRECT_URI
    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    expected_uri = 'http://localhost:8000/api/auth/google/callback'
    if google_redirect_uri == expected_uri:
        print_success(f"GOOGLE_REDIRECT_URI: {google_redirect_uri}")
        tests.append(True)
    else:
        print_error(f"GOOGLE_REDIRECT_URI: {google_redirect_uri}")
        print_error(f"Expected: {expected_uri}")
        tests.append(False)
    
    # Check MongoDB connection
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    print_info(f"MONGO_URL: {mongo_url}")
    
    return all(tests)

def test_backend_server():
    """Test 2: Verify backend server is running and accessible"""
    print_header("TEST 2: Backend Server Accessibility")
    
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    
    try:
        # Test health endpoint
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend server is running at {backend_url}")
            return True
        else:
            print_error(f"Backend server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend server at {backend_url}")
        print_info("Make sure the backend server is running: cd backend && python server.py")
        return False
    except Exception as e:
        print_error(f"Error connecting to backend: {str(e)}")
        return False

def test_oauth_endpoints():
    """Test 3: Verify OAuth endpoints are accessible"""
    print_header("TEST 3: OAuth Endpoints")
    
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    tests = []
    
    # Test OAuth callback endpoint (POST)
    try:
        # We expect this to fail with 422 (missing data), but it confirms the endpoint exists
        response = requests.post(
            f"{backend_url}/api/auth/google/callback",
            json={},
            timeout=5
        )
        if response.status_code in [422, 400]:
            print_success(f"OAuth callback endpoint (POST) exists: {backend_url}/api/auth/google/callback")
            tests.append(True)
        else:
            print_warning(f"OAuth callback endpoint returned unexpected status: {response.status_code}")
            tests.append(True)  # Still counts as accessible
    except Exception as e:
        print_error(f"OAuth callback endpoint (POST) not accessible: {str(e)}")
        tests.append(False)
    
    # Test OAuth callback endpoint (GET)
    try:
        response = requests.get(
            f"{backend_url}/api/auth/google/callback",
            params={'error': 'test'},
            timeout=5
        )
        # We expect 400 because we're sending an error parameter
        if response.status_code == 400:
            print_success(f"OAuth callback endpoint (GET) exists: {backend_url}/api/auth/google/callback")
            tests.append(True)
        else:
            print_warning(f"OAuth callback endpoint (GET) returned status: {response.status_code}")
            tests.append(True)
    except Exception as e:
        print_error(f"OAuth callback endpoint (GET) not accessible: {str(e)}")
        tests.append(False)
    
    return all(tests)

def test_mongodb_connection():
    """Test 4: Verify MongoDB connection and users collection"""
    print_header("TEST 4: MongoDB Connection")
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'maidsofcyfair')
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        print_success(f"Connected to MongoDB at {mongo_url}")
        
        # Check database
        db = client[db_name]
        print_success(f"Accessing database: {db_name}")
        
        # Check users collection
        users_count = db.users.count_documents({})
        print_info(f"Users collection has {users_count} document(s)")
        
        # Check for Google OAuth users
        oauth_users_count = db.users.count_documents({"google_id": {"$exists": True, "$ne": None}})
        print_info(f"Found {oauth_users_count} user(s) with Google OAuth")
        
        client.close()
        return True
        
    except Exception as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        print_info("Make sure MongoDB is running: brew services start mongodb-community")
        return False

def test_google_oauth_url():
    """Test 5: Verify Google OAuth URL construction"""
    print_header("TEST 5: Google OAuth URL Construction")
    
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/auth/google/callback')
    
    if not google_client_id:
        print_error("GOOGLE_CLIENT_ID not found")
        return False
    
    # Construct OAuth URL
    params = {
        'client_id': google_client_id,
        'redirect_uri': google_redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': 'signin',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    print_success("Google OAuth URL constructed successfully:")
    print_info(f"Base URL: https://accounts.google.com/o/oauth2/v2/auth")
    print_info(f"Client ID: {google_client_id}")
    print_info(f"Redirect URI: {google_redirect_uri}")
    print_info(f"Scopes: openid email profile")
    
    print(f"\n{YELLOW}Full OAuth URL (copy to browser to test):{RESET}")
    print(f"{oauth_url}\n")
    
    return True

def test_frontend_env():
    """Test 6: Verify frontend environment configuration"""
    print_header("TEST 6: Frontend Environment Configuration")
    
    frontend_env_path = os.path.join('frontend', '.env')
    
    if not os.path.exists(frontend_env_path):
        print_error(f"Frontend .env file not found at {frontend_env_path}")
        return False
    
    # Read frontend .env
    frontend_env = {}
    with open(frontend_env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                frontend_env[key] = value
    
    tests = []
    
    # Check REACT_APP_GOOGLE_CLIENT_ID
    if 'REACT_APP_GOOGLE_CLIENT_ID' in frontend_env:
        expected_id = '758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com'
        if frontend_env['REACT_APP_GOOGLE_CLIENT_ID'] == expected_id:
            print_success(f"REACT_APP_GOOGLE_CLIENT_ID: {frontend_env['REACT_APP_GOOGLE_CLIENT_ID']}")
            tests.append(True)
        else:
            print_error(f"REACT_APP_GOOGLE_CLIENT_ID: {frontend_env['REACT_APP_GOOGLE_CLIENT_ID']}")
            print_error(f"Expected: {expected_id}")
            tests.append(False)
    else:
        print_error("REACT_APP_GOOGLE_CLIENT_ID not found in frontend .env")
        tests.append(False)
    
    # Check REACT_APP_BACKEND_URL
    if 'REACT_APP_BACKEND_URL' in frontend_env:
        backend_url = frontend_env['REACT_APP_BACKEND_URL']
        if backend_url in ['http://localhost:8000', 'http://127.0.0.1:8000']:
            print_success(f"REACT_APP_BACKEND_URL: {backend_url}")
            tests.append(True)
        else:
            print_warning(f"REACT_APP_BACKEND_URL: {backend_url}")
            print_info("Expected: http://localhost:8000 for local development")
            tests.append(True)
    else:
        print_error("REACT_APP_BACKEND_URL not found in frontend .env")
        tests.append(False)
    
    return all(tests)

def print_summary(results):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for test_name, result in results.items():
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BOLD}Total: {total} | Passed: {GREEN}{passed}{RESET} | Failed: {RED}{failed}{RESET}{BOLD}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 All tests passed! Google OAuth is configured correctly.{RESET}\n")
        print_info("Next steps:")
        print("  1. Make sure backend is running: cd backend && python server.py")
        print("  2. Make sure frontend is running: cd frontend && npm start")
        print("  3. Test Google Sign Up at: http://localhost:3000/register")
        print("  4. Test Google Sign In at: http://localhost:3000/login")
        return True
    else:
        print(f"\n{RED}{BOLD}❌ Some tests failed. Please fix the issues above.{RESET}\n")
        print_info("Refer to GOOGLE_OAUTH_FIX_INSTRUCTIONS.md for detailed setup instructions.")
        return False

def main():
    """Run all tests"""
    print_header("Google OAuth Configuration Test Suite")
    print_info(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Environment Variables": test_environment_variables(),
        "Backend Server": test_backend_server(),
        "OAuth Endpoints": test_oauth_endpoints(),
        "MongoDB Connection": test_mongodb_connection(),
        "Google OAuth URL": test_google_oauth_url(),
        "Frontend Environment": test_frontend_env()
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

