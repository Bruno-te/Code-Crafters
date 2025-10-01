#!/usr/bin/env python3
"""
Test script for the Transaction API
"""
import requests
import json
import base64
import time
import threading
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password123"

def get_auth_header() -> str:
    """Get Basic Auth header"""
    credentials = f"{USERNAME}:{PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded_credentials}"

def test_get_all_transactions():
    """Test GET /transactions"""
    print("Testing GET /transactions...")
    try:
        response = requests.get(
            f"{BASE_URL}/transactions",
            headers={"Authorization": get_auth_header()}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['count']} transactions")
            if data['transactions']:
                print("Sample transaction:")
                print(json.dumps(data['transactions'][0], indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_get_transaction_by_id():
    """Test GET /transactions/{id}"""
    print("\nTesting GET /transactions/{id}...")
    try:
        # First get all transactions to find an ID
        response = requests.get(
            f"{BASE_URL}/transactions",
            headers={"Authorization": get_auth_header()}
        )
        if response.status_code == 200:
            data = response.json()
            if data['transactions']:
                transaction_id = data['transactions'][0]['id']
                print(f"Testing with transaction ID: {transaction_id}")
                
                # Get specific transaction
                response = requests.get(
                    f"{BASE_URL}/transactions/{transaction_id}",
                    headers={"Authorization": get_auth_header()}
                )
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    transaction = response.json()
                    print("Transaction details:")
                    print(json.dumps(transaction, indent=2))
                else:
                    print(f"Error: {response.text}")
            else:
                print("No transactions available for testing")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_create_transaction():
    """Test POST /transactions"""
    print("\nTesting POST /transactions...")
    try:
        new_transaction = {
            "amount": 50.00,
            "date": "2024-01-18T15:30:00Z",
            "message": "Test transaction created via API",
            "type": "credit",
            "status": "success",
            "sender": "+233241234599",
            "recipient": "+233241234600"
        }
        
        response = requests.post(
            f"{BASE_URL}/transactions",
            headers={
                "Authorization": get_auth_header(),
                "Content-Type": "application/json"
            },
            json=new_transaction
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            created_transaction = response.json()
            print("Created transaction:")
            print(json.dumps(created_transaction, indent=2))
            return created_transaction['id']
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_update_transaction(transaction_id: str):
    """Test PUT /transactions/{id}"""
    if not transaction_id:
        print("\nSkipping PUT test - no transaction ID available")
        return
        
    print(f"\nTesting PUT /transactions/{transaction_id}...")
    try:
        update_data = {
            "amount": 75.00,
            "message": "Updated transaction message via API",
            "status": "completed"
        }
        
        response = requests.put(
            f"{BASE_URL}/transactions/{transaction_id}",
            headers={
                "Authorization": get_auth_header(),
                "Content-Type": "application/json"
            },
            json=update_data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_transaction = response.json()
            print("Updated transaction:")
            print(json.dumps(updated_transaction, indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_delete_transaction(transaction_id: str):
    """Test DELETE /transactions/{id}"""
    if not transaction_id:
        print("\nSkipping DELETE test - no transaction ID available")
        return
        
    print(f"\nTesting DELETE /transactions/{transaction_id}...")
    try:
        response = requests.delete(
            f"{BASE_URL}/transactions/{transaction_id}",
            headers={"Authorization": get_auth_header()}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Delete result:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_unauthorized_access():
    """Test unauthorized access"""
    print("\nTesting unauthorized access...")
    try:
        response = requests.get(f"{BASE_URL}/transactions")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("✓ Unauthorized access properly blocked")
        else:
            print(f"✗ Expected 401, got {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the API server is running.")
    except Exception as e:
        print(f"Error: {e}")

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("MoMo SMS Transaction API Tests")
    print("=" * 60)
    
    # Test unauthorized access first
    test_unauthorized_access()
    
    # Test authenticated operations
    test_get_all_transactions()
    test_get_transaction_by_id()
    
    # Test CRUD operations
    created_id = test_create_transaction()
    if created_id:
        test_update_transaction(created_id)
        test_delete_transaction(created_id)
    
    print("\n" + "=" * 60)
    print("API Tests Completed")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
