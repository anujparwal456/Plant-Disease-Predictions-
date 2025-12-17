import requests
from PIL import Image

Image.new('RGB', (224,224), (100,150,200)).save('test_consistency.png')

print('Testing same image 3 times:')
for i in range(3):
    r = requests.post('http://127.0.0.1:5000/api/predict', files={'image': open('test_consistency.png','rb')}, timeout=30)
    data = r.json()
    print(f"  Test {i+1}: {data['label']} ({data['confidence']:.1f}%)")
