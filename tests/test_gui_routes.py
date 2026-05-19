import json
import os
from pathlib import Path

import pytest

from pdf_watermark.gui.app import create_app

INPUT_PDF = str(Path(__file__).parent / "fixtures" / "input.pdf")

_GRID_PAYLOAD = {
    "file_path": INPUT_PDF,
    "watermark": "TEST",
    "opacity": 0.1,
    "angle": 45,
    "text_color": "#000000",
    "text_font": "Helvetica",
    "text_size": 12,
    "mode": "grid",
    "horizontal_boxes": 3,
    "vertical_boxes": 6,
    "margin": False,
    "unselectable": False,
}


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as c:
        yield c


def test_upload_returns_temp_path(client):
    with open(INPUT_PDF, "rb") as f:
        response = client.post(
            "/api/upload",
            data={"file": (f, "input.pdf")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "temp_path" in data
    assert os.path.isfile(data["temp_path"])


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/api/upload",
        data={"file": (b"hello", "file.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "error" in json.loads(response.data)


def test_upload_rejects_missing_file(client):
    response = client.post("/api/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400


def test_raw_serves_pdf(client):
    response = client.get(f"/api/raw?path={INPUT_PDF}")
    assert response.status_code == 200
    assert response.content_type == "application/pdf"


def test_raw_rejects_missing_file(client):
    response = client.get("/api/raw?path=/nonexistent/file.pdf")
    assert response.status_code == 404


def test_preview_returns_pdf_bytes(client):
    response = client.post(
        "/api/preview",
        data=json.dumps(_GRID_PAYLOAD),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/pdf"
    assert len(response.data) > 100


def test_preview_returns_error_for_missing_file(client):
    payload = {**_GRID_PAYLOAD, "file_path": "/no/such/file.pdf"}
    response = client.post(
        "/api/preview",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in json.loads(response.data)


def test_preview_insert_mode(client):
    payload = {
        **_GRID_PAYLOAD,
        "mode": "insert",
        "x": 0.5,
        "y": 0.5,
        "horizontal_alignment": "center",
    }
    response = client.post(
        "/api/preview",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/pdf"


def test_process_creates_output_file(client, tmp_path):
    output = str(tmp_path / "out.pdf")
    payload = {**_GRID_PAYLOAD, "output_path": output, "workers": 1}
    response = client.post(
        "/api/process",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 1
    assert os.path.isfile(output)


def test_process_returns_error_for_missing_file(client, tmp_path):
    payload = {**_GRID_PAYLOAD, "file_path": "/no/file.pdf", "output_path": str(tmp_path / "x.pdf")}
    response = client.post(
        "/api/process",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 500
    assert "error" in json.loads(response.data)


def test_fonts_returns_cjk_and_latin(client):
    response = client.get("/api/fonts")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "STSong-Light" in data["cjk_fonts"]
    assert "MSung-Light" in data["cjk_fonts"]
    assert "Helvetica" in data["latin_fonts"]
    assert "DarkGardenMK" not in data["latin_fonts"]
