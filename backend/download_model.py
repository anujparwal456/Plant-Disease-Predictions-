import requests
import os

MODEL_URL = "https://drive.google.com/uc?export=download&id=1cEHgXukHRFfdgha8FH_Cflowlb0PP0gY"
SAVE_PATH = "models/model.h5"

# Create models folder if it doesn't exist
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

if not os.path.exists(SAVE_PATH):
    print("Downloading model…")
    r = requests.get(MODEL_URL)
    with open(SAVE_PATH, "wb") as f:
        f.write(r.content)
    print("Model downloaded successfully!")
else:
    print("Model already exists.")
