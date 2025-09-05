#!/usr/bin/env python3
"""
Test script for the Apartment Issue Ticketing System
This script demonstrates the system functionality and validates the setup.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"

def test_server_connection():
    """Test if the server is running and accessible"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_ticket_submission():
    """Test ticket submission functionality"""
    test_data = {
        'flat_no': 'A-101',
        'block_no': 'A',
        'problem_type': 'Plumbing',
        'date_raised': datetime.now().strftime('%Y-%m-%d'),
        'contact_number': '9876543210',
        'description': 'Test ticket - Water leakage in bathroom'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit", data=test_data, timeout=10)
        if response.status_code == 302:  # Redirect after successful submission
            print("✅ Ticket submission successful")
            return True
        else:
            print(f"❌ Ticket submission failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error submitting ticket: {e}")
        return False

def test_tickets_view():
    """Test tickets viewing functionality"""
    try:
        response = requests.get(f"{BASE_URL}/tickets", timeout=10)
        if response.status_code == 200:
            print("✅ Tickets view page accessible")
            return True
        else:
            print(f"❌ Tickets view failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing tickets view: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🚀 Starting Apartment Ticketing System Tests...\n")
    
    tests = [
        ("Server Connection", test_server_connection),
        ("Ticket Submission", test_ticket_submission),
        ("Tickets View", test_tickets_view)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        result = test_func()
        results.append(result)
        print()
        time.sleep(1)  # Small delay between tests
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
        print(f"\n🌐 Access your application at: {BASE_URL}")
        print("\n📋 Features available:")
        print("   • Submit new tickets")
        print("   • View all tickets")
        print("   • Filter and search tickets")
        print("   • Export to Excel")
        print("   • Real-time statistics")
    else:
        print("❌ Some tests failed. Please check the server and try again.")
    
    print("=" * 50)

if __name__ == "__main__":
    run_tests()