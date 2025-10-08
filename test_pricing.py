#!/usr/bin/env python3

import requests
import time

# Test the pricing endpoints
try:
    # Wait for server to start
    time.sleep(3)

    # Test base pricing for different house sizes and frequencies
    base_url = 'http://localhost:8000/api'

    # Test pricing for 2000-2500 sq ft, one-time cleaning
    response = requests.get(f'{base_url}/pricing/2000-2500/one_time')
    print('2000-2500 sq ft, one-time:', response.json())

    # Test pricing for 2000-2500 sq ft, monthly
    response = requests.get(f'{base_url}/pricing/2000-2500/monthly')
    print('2000-2500 sq ft, monthly:', response.json())

    # Test pricing for 1000-1500 sq ft, one-time cleaning
    response = requests.get(f'{base_url}/pricing/1000-1500/one_time')
    print('1000-1500 sq ft, one-time:', response.json())

    # Test room pricing calculation
    rooms_data = {
        'rooms': {
            'bedrooms': 2,
            'bathrooms': 1,
            'halfBathrooms': 1,
            'kitchen': True,
            'livingRoom': True
        },
        'frequency': 'one_time'
    }

    response = requests.post(f'{base_url}/calculate-room-pricing', json=rooms_data)
    print('Room pricing calculation:', response.json())

except Exception as e:
    print(f'Error testing pricing: {e}')
    print('Make sure the backend server is running on localhost:8000')

