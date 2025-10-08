#!/usr/bin/env python3
"""
MongoDB Setup Guide for Windows
===============================

This script provides step-by-step instructions for setting up MongoDB
on Windows to resolve the "Invalid email or password" error.
"""

import json
import os
from pathlib import Path

def print_header():
    print("MONGODB SETUP GUIDE FOR WINDOWS")
    print("=" * 50)
    print()
    print("PROBLEM: MongoDB is not configured")
    print("SOLUTION: Set up MongoDB database for the application")
    print()

def option_mongodb_atlas():
    print("OPTION 1: MongoDB Atlas (Cloud) - RECOMMENDED")
    print("-" * 50)
    print()
    print("1. Go to: https://www.mongodb.com/atlas")
    print("2. Create a free account (M0 Sandbox - 512MB)")
    print("3. Create a new cluster (free tier)")
    print("4. Choose 'AWS' as provider, 'us-east-1' region")
    print("5. Cluster name: 'maidsofcyfair-cluster'")
    print("6. Click 'Create cluster'")
    print()
    print("7. In 'Database Access' tab:")
    print("   - Click 'Add New Database User'")
    print("   - Username: 'admin'")
    print("   - Password: 'password123' (or your choice)")
    print("   - Built-in Role: 'Read and write to any database'")
    print()
    print("8. In 'Network Access' tab:")
    print("   - Click 'Add IP Address'")
    print("   - Choose 'Allow Access from Anywhere' (0.0.0.0/0)")
    print("   - This is for development only!")
    print()
    print("9. In 'Clusters' tab:")
    print("   - Click 'Connect'")
    print("   - Choose 'Connect your application'")
    print("   - Copy the connection string")
    print()
    print("10. Update backend/.env file:")
    print("    MONGO_URL=mongodb+srv://admin:password123@maidsofcyfair-cluster.mongodb.net/?retryWrites=true&w=majority")
    print("    DB_NAME=maidsofcyfair")
    print()
    print("11. Replace 'password123' with your actual password")
    print("12. Test connection: python test_mongodb_connection.py")
    print()

def option_local_mongodb():
    print("OPTION 2: Local MongoDB Installation")
    print("-" * 50)
    print()
    print("1. Download MongoDB Community Edition:")
    print("   https://www.mongodb.com/try/download/community")
    print("   Choose Windows MSI installer")
    print()
    print("2. Install MongoDB:")
    print("   - Run the .msi installer")
    print("   - Choose 'Complete' installation")
    print("   - Install MongoDB Compass (GUI tool)")
    print()
    print("3. Start MongoDB service:")
    print("   - Open Command Prompt as Administrator")
    print("   - Run: net start MongoDB")
    print("   OR manually start from Services")
    print()
    print("4. Verify installation:")
    print("   - Open MongoDB Compass")
    print("   - Connect to: mongodb://localhost:27017")
    print("   - You should see 'admin', 'config', 'local' databases")
    print()
    print("5. Update backend/.env file:")
    print("    MONGO_URL=mongodb://localhost:27017")
    print("    DB_NAME=maidsofcyfair")
    print()
    print("6. Test connection: python test_mongodb_connection.py")
    print()

def demo_data_setup():
    print("STEP 3: Set up Demo Data")
    print("-" * 50)
    print()
    print("After MongoDB is running, create the demo cleaner account:")
    print()
    print("Run this command to see the exact data to insert:")
    print("python create_demo_cleaner.py")
    print()
    print("Then use MongoDB Compass or mongo shell to insert the data.")
    print()

def quick_test():
    print("STEP 4: Quick Test")
    print("-" * 50)
    print()
    print("1. Start backend server: python backend/server.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Test cleaner login: http://localhost:3000/cleaner/login")
    print("   Email: cleaner@maids.com")
    print("   Password: cleaner@123")
    print()

def troubleshooting():
    print("TROUBLESHOOTING")
    print("-" * 50)
    print()
    print("If you still get errors:")
    print("1. Check MongoDB is running: net start MongoDB")
    print("2. Check connection string in backend/.env")
    print("3. Verify demo data exists in database")
    print("4. Check browser console for API errors")
    print("5. Ensure backend runs on port 8000")
    print()

def main():
    print_header()
    option_mongodb_atlas()
    option_local_mongodb()
    demo_data_setup()
    quick_test()
    troubleshooting()

    print("SUCCESS: Once MongoDB is set up, the cleaner dashboard will work!")
    print()
    print("For immediate testing, use MongoDB Atlas - it's faster to set up!")

if __name__ == "__main__":
    main()
