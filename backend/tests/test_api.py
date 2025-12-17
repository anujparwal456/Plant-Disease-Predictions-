import io
import os
import sys
import json
from PIL import Image

import pytest

# ensure backend folder is on sys.path for import
HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import app


def create_test_image():
    img = Image.new("RGB", (224, 224), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_predict_endpoint_smoke():
    """Test that /api/predict accepts image and returns valid response structure."""
    client = app.test_client()
    img_buf = create_test_image()
    data = {
        "image": (img_buf, "test.png"),
    }
    resp = client.post("/api/predict", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    j = resp.get_json()
    assert isinstance(j, dict)
    assert "id" in j
    assert "label" in j
    assert "report" in j
    assert "confidence" in j
    # Check that report has required fields
    report = j.get("report", {})
    assert "crop" in report
    assert "disease" in report
    assert "status" in report
