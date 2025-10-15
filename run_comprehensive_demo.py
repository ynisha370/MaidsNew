#!/usr/bin/env python3
"""
Comprehensive Demo Runner
Sets up demo data and runs all feature tests
"""

import asyncio
import subprocess
import sys
from datetime import datetime

def print_banner():
    """Print welcome banner"""
    print("="*80)
    print("🎉 MAIDS OF CYFAIR - COMPREHENSIVE DEMO TESTING")
    print("="*80)
    print("This script will:")
    print("1. Create demo cleaners, customers, and bookings")
    print("2. Test all system features (except Twilio)")
    print("3. Generate comprehensive test reports")
    print("="*80)
    print()

def check_backend_server():
    """Check if backend server is running"""
    print("🔍 Checking backend server status...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running on port 8000")
            return True
        else:
            print(f"⚠️  Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running on port 8000")
        print("   Please start the backend server first:")
        print("   cd backend && python server.py")
        return False

def run_demo_data_setup():
    """Run demo data setup"""
    print("\n🔧 Setting up demo data...")
    try:
        result = subprocess.run([sys.executable, "demo_data_setup.py"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Demo data setup completed successfully")
            return True
        else:
            print(f"❌ Demo data setup failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Demo data setup timed out")
        return False
    except Exception as e:
        print(f"❌ Error running demo data setup: {str(e)}")
        return False

def run_feature_tests():
    """Run feature tests"""
    print("\n🧪 Running feature tests...")
    try:
        result = subprocess.run([sys.executable, "feature_test_suite.py"], 
                              capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ Feature tests completed successfully")
            return True
        else:
            print(f"❌ Feature tests failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Feature tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running feature tests: {str(e)}")
        return False

def print_demo_credentials():
    """Print demo credentials for testing"""
    print("\n" + "="*80)
    print("🔑 DEMO CREDENTIALS FOR TESTING")
    print("="*80)
    print("\n📱 Cleaner App Login Credentials:")
    print("   Email: sarah.johnson@maids.com")
    print("   Password: cleaner123")
    print("   Name: Sarah Johnson")
    print()
    print("   Email: maria.garcia@maids.com")
    print("   Password: cleaner123")
    print("   Name: Maria Garcia")
    print()
    print("   Email: jennifer.smith@maids.com")
    print("   Password: cleaner123")
    print("   Name: Jennifer Smith")
    print()
    print("   Email: lisa.wilson@maids.com")
    print("   Password: cleaner123")
    print("   Name: Lisa Wilson")
    print()
    print("   Email: ana.rodriguez@maids.com")
    print("   Password: cleaner123")
    print("   Name: Ana Rodriguez")
    print()
    print("👥 Customer Portal Login Credentials:")
    print("   Email: john.doe@example.com")
    print("   Password: customer123")
    print("   Name: John Doe")
    print()
    print("   Email: jane.smith@example.com")
    print("   Password: customer123")
    print("   Name: Jane Smith")
    print()
    print("   Email: mike.wilson@example.com")
    print("   Password: customer123")
    print("   Name: Mike Wilson")
    print()
    print("   Email: sarah.brown@example.com")
    print("   Password: customer123")
    print("   Name: Sarah Brown")
    print()
    print("👨‍💼 Admin Dashboard Login Credentials:")
    print("   Email: admin@maids.com")
    print("   Password: admin@maids@1234")
    print()
    print("🌐 URLs for Testing:")
    print("   Frontend: http://localhost:3000")
    print("   Admin Dashboard: http://localhost:3000/admin")
    print("   Cleaner App: http://localhost:3000/cleaner")
    print("   Backend API: http://localhost:8000/api")
    print("="*80)

def main():
    """Main function"""
    print_banner()
    
    # Check if backend server is running
    if not check_backend_server():
        return 1
    
    # Run demo data setup
    if not run_demo_data_setup():
        print("\n❌ Demo setup failed. Exiting.")
        return 1
    
    # Run feature tests
    if not run_feature_tests():
        print("\n❌ Feature tests failed. Exiting.")
        return 1
    
    # Print demo credentials
    print_demo_credentials()
    
    print("\n🎉 COMPREHENSIVE DEMO TESTING COMPLETED!")
    print("   All features have been tested successfully.")
    print("   Demo data has been created and is ready for use.")
    print("   Check the generated test reports for detailed results.")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
