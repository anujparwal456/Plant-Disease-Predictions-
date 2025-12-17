import io
from PIL import Image
import requests

def run():
    buf = io.BytesIO()
    Image.new("RGB", (224, 224), color=(0, 200, 100)).save(buf, format="PNG")
    buf.seek(0)
    files = {"image": ("e2e.png", buf, "image/png")}
    resp = requests.post("http://127.0.0.1:5000/api/predict", files=files)
    print("status:", resp.status_code)
    try:
        print(resp.json())
    except Exception as e:
        print("response text:", resp.text)

if __name__ == "__main__":
    run()
