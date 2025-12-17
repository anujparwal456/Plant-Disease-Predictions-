import requests
import json
from PIL import Image
import time

# Create test image
Image.new('RGB', (224,224), (100,150,200)).save('test_gemini.png')

print("Testing backend with Gemini API integration...\n")

# Test 1: Same image 3 times
print("=== Test 1: Consistency (same image 3 times) ===")
for i in range(3):
    r = requests.post('http://127.0.0.1:5000/api/predict', files={'image': open('test_gemini.png','rb')}, timeout=60)
    data = r.json()
    print(f"Attempt {i+1}: {data['label']} ({data['confidence']:.1f}%)")
    if 'report' in data:
        print(f"  Status: {data['report'].get('status')}")
        print(f"  Remedy: {data['report'].get('remedy')[:100]}...")

# Test 2: Check Gemini enhancement
print("\n=== Test 2: Full Report (with Gemini) ===")
r = requests.post('http://127.0.0.1:5000/api/predict', files={'image': open('test_gemini.png','rb')}, timeout=60)
data = r.json()
print(json.dumps(data, indent=2)[:500] + "...")
