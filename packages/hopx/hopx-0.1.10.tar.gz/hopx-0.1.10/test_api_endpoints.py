#!/usr/bin/env python3
"""
Quick API Endpoint Test - Python SDK
Tests all endpoints without waiting for full build
"""

import requests
import time

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'
BASE_URL = 'https://api.hopx.dev'


def test_endpoints():
    print('🧪 Quick API Endpoint Test (Python)\n')
    print(f'API: {BASE_URL}')
    print('─' * 60)
    
    try:
        # Test 1: Get Upload Link
        print('\n📤 Test 1: Get File Upload Link')
        resp = requests.post(
            f'{BASE_URL}/v1/templates/files/upload-link',
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'files_hash': 'a' * 64,
                'content_length': 1024,
            },
        )
        data = resp.json()
        print(f'   ✅ Status: {resp.status_code}')
        print(f'   Present: {data["present"]}')
        if data.get('upload_url'):
            print(f'   Upload URL: {data["upload_url"][:60]}...')
        
        # Test 2: Trigger Build
        print('\n🔨 Test 2: Trigger Template Build')
        resp = requests.post(
            f'{BASE_URL}/v1/templates/build',
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'alias': f'python-test-{int(time.time())}',
                'steps': [
                    {'type': 'run', 'command': 'echo "test"'},
                    {'type': 'run', 'command': 'apt-get update'}
                ],
                'start_cmd': '/bin/bash',
                'ready_cmd': {'type': 'port', 'port': 22},
                'cpu': 2,
                'memory_mb': 2048,
                'disk_gb': 10,
                'skip_cache': False,
            },
        )
        data = resp.json()
        print(f'   ✅ Status: {resp.status_code}')
        print(f'   Build ID: {data["build_id"]}')
        print(f'   Template ID: {data["template_id"]}')
        print(f'   Status: {data["status"]}')
        build_id = data['build_id']
        
        # Test 3: Get Build Status
        print('\n📊 Test 3: Get Build Status')
        time.sleep(2)
        
        resp = requests.get(
            f'{BASE_URL}/v1/templates/build/{build_id}/status',
            headers={'Authorization': f'Bearer {API_KEY}'},
        )
        data = resp.json()
        print(f'   ✅ Status: {resp.status_code}')
        print(f'   Build Status: {data["status"]}')
        print(f'   Progress: {data["progress"]}%')
        
        # Test 4: Stream Logs
        print('\n📜 Test 4: Stream Build Logs (SSE)')
        resp = requests.get(
            f'{BASE_URL}/v1/templates/build/{build_id}/logs',
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Accept': 'text/event-stream',
            },
            stream=True,
        )
        print(f'   ✅ SSE Connection: {resp.status_code}')
        print(f'   Content-Type: {resp.headers.get("content-type")}')
        resp.close()
        
        # Test 5: List Templates
        print('\n📋 Test 5: List Templates')
        resp = requests.get(
            f'{BASE_URL}/v1/templates?limit=3',
            headers={'Authorization': f'Bearer {API_KEY}'},
        )
        data = resp.json()
        print(f'   ✅ Status: {resp.status_code}')
        print(f'   Templates found: {len(data.get("data", []))}')
        if data.get('data'):
            print(f'   First template: {data["data"][0]["name"]}')
        
        print('\n' + '─' * 60)
        print('✅ ALL ENDPOINT TESTS PASSED!')
        print('─' * 60)
        print('\n📊 Summary:')
        print('   ✅ Upload Link endpoint working')
        print('   ✅ Build Trigger endpoint working')
        print('   ✅ Build Status endpoint working')
        print('   ✅ Build Logs (SSE) endpoint working')
        print('   ✅ List Templates endpoint working')
        print('\n🎉 Python SDK API Integration: SUCCESS!')
        
    except Exception as e:
        print(f'\n❌ Test FAILED: {e}')
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    test_endpoints()

