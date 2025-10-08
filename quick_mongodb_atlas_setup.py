#!/usr/bin/env python3
"""
QUICK MongoDB Atlas Setup Guide
===============================

This script provides the FASTEST way to get MongoDB running for testing.
Use MongoDB Atlas (cloud) - no installation required!
"""

import json
import os
from pathlib import Path

def main():
    print("QUICKEST MongoDB Setup - MongoDB Atlas (Cloud)")
    print("=" * 60)
    print()
    print("PROBLEM: MongoDB not running locally")
    print("SOLUTION: Use MongoDB Atlas (FREE cloud database)")
    print()

    print("STEP 1: Create MongoDB Atlas Account")
    print("-" * 40)
    print("1. Go to: https://www.mongodb.com/atlas")
    print("2. Click 'Try Free' or 'Start Free'")
    print("3. Create account (use Google/GitHub for fastest)")
    print("4. Verify email if required")
    print()

    print("STEP 2: Create Free Cluster")
    print("-" * 40)
    print("1. Click 'Build a Database'")
    print("2. Choose FREE tier (M0 Sandbox - 512MB)")
    print("3. Provider: AWS")
    print("4. Region: us-east-1 (N. Virginia) - closest to you")
    print("5. Cluster name: 'maidsofcyfair-cluster' (or any name)")
    print("6. Click 'Create cluster' (takes 2-3 minutes)")
    print()

    print("STEP 3: Set up Database User")
    print("-" * 40)
    print("1. Go to 'Database Access' tab")
    print("2. Click 'Add New Database User'")
    print("3. Authentication Method: Password")
    print("4. Username: 'admin'")
    print("5. Password: 'password123' (or your choice)")
    print("6. Built-in Role: 'Read and write to any database'")
    print("7. Click 'Add User'")
    print()

    print("STEP 4: Configure Network Access")
    print("-" * 40)
    print("1. Go to 'Network Access' tab")
    print("2. Click 'Add IP Address'")
    print("3. Choose 'Allow Access from Anywhere' (0.0.0.0/0)")
    print("4. Click 'Confirm' (WARNING: This is for development only!)")
    print()

    print("STEP 5: Get Connection String")
    print("-" * 40)
    print("1. Go to 'Clusters' tab")
    print("2. Click 'Connect' button")
    print("3. Choose 'Connect your application'")
    print("4. Copy the connection string (looks like this):")
    print("   mongodb+srv://admin:password123@cluster.mongodb.net/?retryWrites=true&w=majority")
    print()

    print("STEP 6: Update Configuration")
    print("-" * 40)
    print("1. Open backend/.env file")
    print("2. Update these lines:")
    print("   MONGO_URL=mongodb+srv://admin:password123@your-cluster.mongodb.net/?retryWrites=true&w=majority")
    print("   DB_NAME=maidsofcyfair")
    print("3. Replace 'password123' with your actual password")
    print("4. Replace 'your-cluster' with your actual cluster name")
    print()

    print("STEP 7: Test Connection")
    print("-" * 40)
    print("Run this command to verify everything works:")
    print("python test_mongodb_connection.py")
    print()

    print("STEP 8: Create Demo Data")
    print("-" * 40)
    print("Run this to see the demo data to insert:")
    print("python create_demo_cleaner.py")
    print()
    print("Then use MongoDB Compass or Atlas dashboard to insert the data.")
    print()

    print("STEP 9: Test Cleaner Login")
    print("-" * 40)
    print("1. Start backend: python backend/server.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Go to: http://localhost:3000/cleaner/login")
    print("4. Login with:")
    print("   Email: cleaner@maids.com")
    print("   Password: cleaner@123")
    print()

    print("SUCCESS: You should now have a working cleaner dashboard!")
    print()
    print("Time estimate: 10-15 minutes total")
    print("Cost: $0 (free tier)")
    print("Security: Development only - use proper security for production")

if __name__ == "__main__":
    main()
