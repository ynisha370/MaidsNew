#!/usr/bin/env python3
import requests
from datetime import datetime

print('Testing server connectivity...')
try:
    response = requests.get('http://localhost:8002/api/admin/calendar/availability-summary?date=2025-10-09')
    print(f'Server status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Found {len(data.get("cleaners", []))} cleaners')
        for cleaner in data.get('cleaners', []):
            print(f'Cleaner: {cleaner["cleaner_name"]} - Calendar: {cleaner["calendar_enabled"]}')
            available_slots = sum(1 for slot_data in cleaner.get('slots', {}).values() if slot_data.get('available', False))
            print(f'  Available slots: {available_slots}')
    else:
        print(f'Error: {response.text[:200]}')
except Exception as e:
    print(f'Connection error: {e}')
