#!/usr/bin/env python3
"""
Test script for cart API functionality
"""

import requests
import json

def test_cart_api():
    base_url = "http://localhost:5000"
    
    # 創建會話來保持狀態
    session = requests.Session()
    
    print("Testing Cart API...")
    
    # Test 1: Get empty cart
    print("\n1. Testing empty cart...")
    response = session.get(f"{base_url}/api/cart")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Add product to cart
    print("\n2. Testing add to cart...")
    cart_data = {
        "product_id": 1,
        "quantity": 1,
        "temperature": "normal",
        "ingredients": [1, 2]  # ingredient IDs
    }
    
    response = session.post(f"{base_url}/api/cart/add", json=cart_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Get cart with items
    print("\n3. Testing cart with items...")
    response = session.get(f"{base_url}/api/cart")
    print(f"Status: {response.status_code}")
    cart_response = response.json()
    print(f"Response: {json.dumps(cart_response, indent=2)}")
    
    # Test 4: Test cart page
    print("\n4. Testing cart page...")
    response = session.get(f"{base_url}/cart")
    print(f"Status: {response.status_code}")
    print(f"Cart page loaded successfully: {response.status_code == 200}")

if __name__ == "__main__":
    test_cart_api()
