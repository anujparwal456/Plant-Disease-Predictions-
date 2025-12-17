#!/usr/bin/env python3
"""Quick test of API with Gemini integration"""
import requests
import json
from PIL import Image
import io

# Create a simple test image (224x224 green image - should predict something)
img = Image.new('RGB', (224, 224), color=(76, 175, 80))  # Green
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Send to backend
print("=" * 60)
print("Testing API with Gemini integration")
print("=" * 60)

try:
    files = {'image': ('test.png', img_bytes, 'image/png')}
    response = requests.post('http://127.0.0.1:5000/api/predict', files=files, timeout=30)
    
    print(f"\n✅ Request successful!")
    print(f"Status Code: {response.status_code}")
    
    result = response.json()
    print(f"\n📊 Prediction Result:")
    print(json.dumps(result, indent=2))
    
    if 'report' in result:
        print(f"\n📝 Generated Report:")
        print(result['report'])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
