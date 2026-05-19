# PDF 浮水印 GUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Flask web GUI for pdf-watermark that renders live PDF watermark previews in-browser, supports Traditional Chinese throughout, and accepts files via drag-and-drop or path input.

**Architecture:** Flask backend exposes 5 API endpoints that wrap the existing `add_watermark_from_options()`. Alpine.js 3 manages all UI state in a single HTML page. PDF.js 3 renders PDF previews directly in the browser canvas — no Poppler required. All JS assets are vendored locally for offline use.

**Tech Stack:** Python 3.10+, Flask 3.x, Alpine.js 3.14.1, PDF.js 3.11.174

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/pdf_watermark/gui/__init__.py` | Package marker |
| Create | `src/pdf_watermark/gui/app.py` | Flask factory + `main()` entry point |
| Create | `src/pdf_watermark/gui/routes.py` | All 5 API routes + 3 private helpers |
| Create | `src/pdf_watermark/gui/templates/index.html` | Single-page Alpine.js UI |
| Create | `src/pdf_watermark/gui/static/alpine.min.js` | Vendored Alpine.js 3.14.1 |
| Create | `src/pdf_watermark/gui/static/pdfjs/pdf.min.js` | Vendored PDF.js 3.11.174 |
| Create | `src/pdf_watermark/gui/static/pdfjs/pdf.worker.min.js` | PDF.js worker |
| Modify | `pyproject.toml` | Add `flask>=3.0.0` dep + `watermark-gui` script |
| Create | `tests/test_gui_app.py` | Tests for Flask app factory |
| Create | `tests/test_gui_routes.py` | Tests for all API routes |

---

## Task 1: Add Flask dependency and CLI entry point

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add flask to dependencies and watermark-gui script**

In `pyproject.toml`, update `dependencies`:

```toml
dependencies = [
    "pypdf>=3.11.0",
    "pillow>=9.5.0",
    "reportlab>=4.4.4",
    "numpy>=1.25.0",
    "click>=8.1.3",
    "pdf2image>=1.17.0",
    "types-reportlab>=4.4.4.20250926",
    "dataclass-click>=1.0.4",
    "flask>=3.0.0",
]
```

Update `[project.scripts]`:

```toml
[project.scripts]
watermark = "pdf_watermark.watermark:cli"
pdf-watermark = "pdf_watermark.watermark:cli"
watermark-gui = "pdf_watermark.gui.app:main"
```

- [ ] **Step 2: Sync and verify**

```powershell
uv sync
uv run python -c "import flask; print(flask.__version__)"
```

Expected: Flask version printed (e.g. `3.1.0`).

- [ ] **Step 3: Commit**

```powershell
git add pyproject.toml uv.lock
git commit -m "feat: add flask dependency and watermark-gui entry point"
```

---

## Task 2: Flask app factory

**Files:**
- Create: `src/pdf_watermark/gui/__init__.py`
- Create: `src/pdf_watermark/gui/app.py`
- Create: `src/pdf_watermark/gui/templates/index.html` (minimal placeholder)
- Create: `src/pdf_watermark/gui/static/` (empty dir placeholder)
- Create: `tests/test_gui_app.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_gui_app.py`:

```python
from pdf_watermark.gui.app import create_app


def test_create_app_default():
    app = create_app()
    assert app is not None
    assert app.config["TESTING"] is False


def test_create_app_testing_mode():
    app = create_app(testing=True)
    assert app.config["TESTING"] is True


def test_index_returns_html():
    app = create_app(testing=True)
    with app.test_client() as client:
        response = client.get("/")
    assert response.status_code == 200
    assert b"PDF" in response.data
```

- [ ] **Step 2: Run to confirm failure**

```powershell
uv run pytest tests/test_gui_app.py -v
```

Expected: `ModuleNotFoundError: No module named 'pdf_watermark.gui'`

- [ ] **Step 3: Create the package files**

Create `src/pdf_watermark/gui/__init__.py` (empty).

Create `src/pdf_watermark/gui/app.py`:

```python
import atexit
import os
import shutil
import threading
import webbrowser

from flask import Flask


def create_app(testing: bool = False) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["TESTING"] = testing
    app.config["_temp_dirs"] = []

    from pdf_watermark.gui.routes import register_routes
    register_routes(app)

    def _cleanup() -> None:
        for d in app.config["_temp_dirs"]:
            shutil.rmtree(d, ignore_errors=True)

    atexit.register(_cleanup)
    return app


def main() -> None:
    port = int(os.environ.get("WATERMARK_GUI_PORT", 7860))
    app = create_app()

    def _open() -> None:
        webbrowser.open(f"http://localhost:{port}")

    threading.Timer(1.0, _open).start()
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
```

Create `src/pdf_watermark/gui/templates/index.html` (minimal — full UI comes in Task 5):

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><title>PDF 浮水印工具</title></head>
<body><h1>PDF 浮水印工具</h1></body>
</html>
```

Create the static dir placeholder (PowerShell):

```powershell
New-Item -ItemType Directory -Path "src/pdf_watermark/gui/static/pdfjs" -Force
```

Create `src/pdf_watermark/gui/routes.py` (index route only for now — full implementation in Task 3):

```python
from flask import Flask, render_template


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("index.html")
```

- [ ] **Step 4: Run tests to confirm pass**

```powershell
uv run pytest tests/test_gui_app.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/pdf_watermark/gui/ tests/test_gui_app.py
git commit -m "feat: Flask app factory with index route"
```

---

## Task 3: Implement all API routes

**Files:**
- Modify: `src/pdf_watermark/gui/routes.py`
- Create: `tests/test_gui_routes.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_gui_routes.py`:

```python
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


# --- /api/upload ---

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


# --- /api/raw ---

def test_raw_serves_pdf(client):
    response = client.get(f"/api/raw?path={INPUT_PDF}")
    assert response.status_code == 200
    assert response.content_type == "application/pdf"


def test_raw_rejects_missing_file(client):
    response = client.get("/api/raw?path=/nonexistent/file.pdf")
    assert response.status_code == 404


# --- /api/preview ---

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


# --- /api/process ---

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


# --- /api/fonts ---

def test_fonts_returns_cjk_and_latin(client):
    response = client.get("/api/fonts")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "STSong-Light" in data["cjk_fonts"]
    assert "MSung-Light" in data["cjk_fonts"]
    assert "Helvetica" in data["latin_fonts"]
    assert "DarkGardenMK" not in data["latin_fonts"]
```

- [ ] **Step 2: Run to confirm failures**

```powershell
uv run pytest tests/test_gui_routes.py -v
```

Expected: Most tests fail (routes not implemented).

- [ ] **Step 3: Implement routes.py**

Replace `src/pdf_watermark/gui/routes.py` with:

```python
import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from pdf_watermark.font_utils import STANDARD_CID_FONTS, STANDARD_FONTS
from pdf_watermark.handler import add_watermark_from_options
from pdf_watermark.options import DrawingOptions, FilesOptions, GridOptions, InsertOptions


def register_routes(app: Flask) -> None:

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/upload", methods=["POST"])
    def upload():
        if "file" not in request.files:
            return jsonify({"error": "沒有上傳檔案"}), 400
        file = request.files["file"]
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "只接受 PDF 檔案"}), 400
        temp_dir = tempfile.mkdtemp()
        app.config["_temp_dirs"].append(temp_dir)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        return jsonify({"temp_path": temp_path})

    @app.route("/api/raw")
    def raw():
        path = request.args.get("path", "")
        if not os.path.isfile(path):
            return jsonify({"error": "檔案不存在"}), 404
        return send_file(path, mimetype="application/pdf")

    @app.route("/api/preview", methods=["POST"])
    def preview():
        data = request.get_json()
        input_path = data.get("file_path", "")
        if not os.path.isfile(input_path):
            return jsonify({"error": "找不到輸入檔案"}), 400
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                output_path = f.name
            _apply_watermark(input_path, output_path, data, verbose=False)
            return send_file(output_path, mimetype="application/pdf")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/process", methods=["POST"])
    def process():
        data = request.get_json()
        file_path = data.get("file_path", "")
        output_path = data.get("output_path") or None
        try:
            files_options = FilesOptions(
                file=Path(file_path),
                output=Path(output_path) if output_path else None,
                workers=int(data.get("workers", 1)),
                verbose=True,
            )
            drawing_options = _build_drawing_options(data)
            specific_options = _build_specific_options(data)
            add_watermark_from_options(files_options, drawing_options, specific_options)
            return jsonify({
                "count": len(files_options.input_files),
                "output_path": str(files_options.output or files_options.file),
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/fonts")
    def fonts():
        latin = [f for f in STANDARD_FONTS if f != "DarkGardenMK"]
        return jsonify({"cjk_fonts": list(STANDARD_CID_FONTS), "latin_fonts": latin})


def _build_drawing_options(data: dict) -> DrawingOptions:
    return DrawingOptions(
        watermark=data["watermark"],
        opacity=float(data.get("opacity", 0.1)),
        angle=float(data.get("angle", 45)),
        text_color=data.get("text_color", "#000000"),
        text_font=data.get("text_font", "Helvetica"),
        text_size=int(data.get("text_size", 12)),
        unselectable=bool(data.get("unselectable", False)),
        image_scale=float(data.get("image_scale", 1.0)),
        save_as_image=False,
        dpi=int(data.get("dpi", 300)),
        custom_fonts_folder=data.get("custom_fonts_folder"),
    )


def _build_specific_options(data: dict):
    if data.get("mode", "grid") == "grid":
        return GridOptions(
            horizontal_boxes=int(data.get("horizontal_boxes", 3)),
            vertical_boxes=int(data.get("vertical_boxes", 6)),
            margin=bool(data.get("margin", False)),
        )
    return InsertOptions(
        x=float(data.get("x", 0.5)),
        y=float(data.get("y", 0.5)),
        horizontal_alignment=data.get("horizontal_alignment", "center"),
    )


def _apply_watermark(
    input_path: str, output_path: str, data: dict, verbose: bool = False
) -> None:
    files_options = FilesOptions(
        file=Path(input_path),
        output=Path(output_path),
        verbose=verbose,
    )
    drawing_options = _build_drawing_options(data)
    specific_options = _build_specific_options(data)
    add_watermark_from_options(files_options, drawing_options, specific_options)
```

- [ ] **Step 4: Run tests to confirm pass**

```powershell
uv run pytest tests/test_gui_routes.py -v
```

Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/pdf_watermark/gui/routes.py tests/test_gui_routes.py
git commit -m "feat: implement all 5 GUI API routes with tests"
```

---

## Task 4: Vendor Alpine.js and PDF.js

**Files:**
- Create: `src/pdf_watermark/gui/static/alpine.min.js`
- Create: `src/pdf_watermark/gui/static/pdfjs/pdf.min.js`
- Create: `src/pdf_watermark/gui/static/pdfjs/pdf.worker.min.js`

- [ ] **Step 1: Download Alpine.js 3.14.1**

```powershell
Invoke-WebRequest `
  -Uri "https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js" `
  -OutFile "src/pdf_watermark/gui/static/alpine.min.js"
```

Expected: File created ~15 KB.

- [ ] **Step 2: Download PDF.js 3.11.174**

```powershell
Invoke-WebRequest `
  -Uri "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js" `
  -OutFile "src/pdf_watermark/gui/static/pdfjs/pdf.min.js"

Invoke-WebRequest `
  -Uri "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js" `
  -OutFile "src/pdf_watermark/gui/static/pdfjs/pdf.worker.min.js"
```

Expected: `pdf.min.js` ~700 KB, `pdf.worker.min.js` ~500 KB.

- [ ] **Step 3: Verify**

```powershell
Get-Item src/pdf_watermark/gui/static/alpine.min.js,
         src/pdf_watermark/gui/static/pdfjs/pdf.min.js,
         src/pdf_watermark/gui/static/pdfjs/pdf.worker.min.js |
  Select-Object Name, Length
```

Expected: All three files with non-zero size.

- [ ] **Step 4: Commit**

```powershell
git add src/pdf_watermark/gui/static/
git commit -m "feat: vendor Alpine.js 3.14.1 and PDF.js 3.11.174 for offline use"
```

---

## Task 5: Build the full UI

**Files:**
- Modify: `src/pdf_watermark/gui/templates/index.html`

- [ ] **Step 1: Replace the placeholder with the full index.html**

Replace the entire content of `src/pdf_watermark/gui/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PDF 浮水印工具</title>
  <script src="/static/alpine.min.js" defer></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif;
      background: #f0f2f5; height: 100vh; display: flex; flex-direction: column;
    }
    header {
      background: #1a2634; color: #fff; padding: 10px 20px;
      display: flex; justify-content: space-between; align-items: center;
      flex-shrink: 0;
    }
    header h1 { font-size: 1rem; font-weight: 600; letter-spacing: 0.02em; }
    .main { display: flex; flex: 1; overflow: hidden; }

    /* Left panel */
    .left-panel {
      width: 300px; min-width: 300px; background: #fff;
      border-right: 1px solid #dde1e7; overflow-y: auto;
      padding: 14px 16px; display: flex; flex-direction: column; gap: 11px;
    }
    .section-title {
      font-size: 0.7rem; font-weight: 700; color: #888;
      text-transform: uppercase; letter-spacing: 0.08em;
      border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; margin-top: 4px;
    }
    label { font-size: 0.83rem; color: #444; display: block; margin-bottom: 3px; }
    input[type="text"], select {
      width: 100%; padding: 6px 9px; border: 1px solid #ccc; border-radius: 4px;
      font-size: 0.88rem;
      font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
      transition: border-color 0.15s;
    }
    input[type="text"]:focus, select:focus { outline: none; border-color: #3b82f6; }
    input[type="text"].input-error { border-color: #ef4444; }
    input[type="range"] { width: 100%; cursor: pointer; accent-color: #3b82f6; }
    input[type="color"] {
      width: 36px; height: 28px; padding: 1px 2px;
      border: 1px solid #ccc; border-radius: 4px; cursor: pointer;
    }
    .slider-row { display: flex; align-items: center; gap: 8px; }
    .slider-row input[type="range"] { flex: 1; }
    .slider-val { font-size: 0.78rem; color: #555; min-width: 38px; text-align: right; font-variant-numeric: tabular-nums; }
    .radio-group { display: flex; gap: 14px; }
    .radio-group label { display: flex; align-items: center; gap: 5px; cursor: pointer; font-size: 0.85rem; }
    .check-label { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 0.85rem; }

    /* Drop zone */
    .drop-zone {
      border: 2px dashed #bbb; border-radius: 6px; padding: 14px 10px;
      text-align: center; cursor: pointer; transition: all 0.2s;
      color: #999; font-size: 0.82rem; user-select: none;
    }
    .drop-zone:hover, .drop-zone.active { border-color: #3b82f6; background: #eff6ff; color: #2563eb; }
    .drop-zone p { margin: 0; line-height: 1.5; }

    /* Alerts */
    .alert {
      border-radius: 4px; padding: 7px 10px; font-size: 0.8rem; line-height: 1.4;
    }
    .alert-warn  { background: #fefce8; border: 1px solid #fbbf24; color: #92400e; }
    .alert-error { background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; }
    .alert-ok    { background: #f0fdf4; border: 1px solid #86efac; color: #166534; }

    /* Advanced toggle */
    .adv-toggle {
      background: none; border: none; cursor: pointer; font-size: 0.83rem;
      color: #3b82f6; padding: 2px 0; text-align: left; width: 100%;
      font-family: inherit;
    }
    .adv-toggle:hover { text-decoration: underline; }
    .adv-section { border-top: 1px solid #f0f0f0; padding-top: 10px; display: flex; flex-direction: column; gap: 10px; }

    /* Buttons */
    .btn-primary {
      background: #2563eb; color: #fff; border: none; border-radius: 5px;
      padding: 9px 18px; font-size: 0.9rem; cursor: pointer; font-family: inherit;
      transition: background 0.15s;
    }
    .btn-primary:hover:not(:disabled) { background: #1d4ed8; }
    .btn-primary:disabled { background: #9ca3af; cursor: not-allowed; }

    /* Right panel */
    .right-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .preview-half {
      flex: 1; display: flex; flex-direction: column; overflow: auto;
      padding: 10px 14px; background: #f8f9fa;
    }
    .preview-half:first-child { border-bottom: 2px solid #dde1e7; background: #f0f2f5; }
    .preview-half h3 {
      font-size: 0.72rem; font-weight: 600; color: #6b7280;
      text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;
    }
    canvas { max-width: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.12); background: #fff; }
    .preview-hint { font-size: 0.82rem; color: #9ca3af; padding: 12px 0; }

    optgroup { font-weight: 700; font-size: 0.8rem; }
    option   { font-weight: 400; }
  </style>
</head>
<body x-data="app()" x-init="init()">

  <!-- Header -->
  <header>
    <h1>📄 PDF 浮水印工具</h1>
    <button
      class="btn-primary"
      @click="process()"
      :disabled="!filePath || processing || !watermark"
    >
      <span x-show="!processing">產生浮水印</span>
      <span x-show="processing">處理中…</span>
    </button>
  </header>

  <div class="main">

    <!-- ── Left: Controls ── -->
    <div class="left-panel">

      <!-- File input -->
      <div class="section-title">輸入檔案</div>

      <div
        class="drop-zone"
        :class="{ active: dragOver }"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="handleDrop($event)"
        @click="$refs.fileInput.click()"
      >
        <p>拖曳 PDF 到此處</p>
        <p style="font-size:0.72rem;margin-top:3px;color:#aaa;">或點擊選擇檔案（單一 PDF）</p>
        <input type="file" x-ref="fileInput" accept=".pdf,.PDF" style="display:none"
               @change="handleFileInput($event)">
      </div>

      <div>
        <label>或輸入路徑（支援單一檔案或資料夾批次）</label>
        <input type="text" x-model="filePath"
               :class="{ 'input-error': pathError }"
               placeholder="C:\...\document.pdf"
               @input.debounce.600ms="onPathInput()">
        <div x-show="pathError" class="alert alert-error" style="margin-top:4px;" x-text="pathError"></div>
      </div>

      <!-- Watermark content -->
      <div class="section-title">浮水印內容</div>
      <div class="radio-group">
        <label><input type="radio" value="text"  x-model="watermarkType" @change="debouncePreview()"> 文字</label>
        <label><input type="radio" value="image" x-model="watermarkType" @change="debouncePreview()"> 圖片</label>
      </div>

      <template x-if="watermarkType === 'text'">
        <div>
          <label>浮水印文字</label>
          <input type="text" x-model="watermark" @input="debouncePreview()" placeholder="機密文件">
          <div x-show="cjkFontWarning" class="alert alert-warn" style="margin-top:5px;">
            ⚠ 偵測到中文字元，建議改用上方「✓ 支援中文」字體
          </div>
        </div>
      </template>

      <template x-if="watermarkType === 'image'">
        <div>
          <label>圖片路徑（PNG / JPG）</label>
          <input type="text" x-model="watermark" @input="debouncePreview()" placeholder="C:\...\logo.png">
        </div>
      </template>

      <!-- Common params -->
      <div class="section-title">常用設定</div>

      <div>
        <label>透明度</label>
        <div class="slider-row">
          <input type="range" min="0.01" max="1" step="0.01" x-model="opacity" @input="debouncePreview()">
          <span class="slider-val" x-text="parseFloat(opacity).toFixed(2)"></span>
        </div>
      </div>

      <div>
        <label>角度</label>
        <div class="slider-row">
          <input type="range" min="0" max="360" step="1" x-model="angle" @input="debouncePreview()">
          <span class="slider-val" x-text="angle + '°'"></span>
        </div>
      </div>

      <template x-if="watermarkType === 'text'">
        <div style="display:flex;flex-direction:column;gap:9px;">
          <div style="display:flex;gap:10px;align-items:flex-end;">
            <div>
              <label>顏色</label>
              <input type="color" x-model="textColor" @input="debouncePreview()">
            </div>
            <div style="flex:1;">
              <label>大小</label>
              <div class="slider-row">
                <input type="range" min="6" max="72" step="1" x-model="textSize" @input="debouncePreview()">
                <span class="slider-val" x-text="textSize + 'pt'"></span>
              </div>
            </div>
          </div>
          <div>
            <label>字體</label>
            <select x-model="textFont" @change="debouncePreview()">
              <optgroup label="✓ 支援中文">
                <option value="STSong-Light">STSong-Light（宋體）</option>
                <option value="MSung-Light">MSung-Light（明體）</option>
                <option value="HYGothic-Medium">HYGothic-Medium（韓文黑體）</option>
                <option value="HeiseiMin-W3">HeiseiMin-W3（日文明朝）</option>
                <option value="HeiseiKakuGo-W5">HeiseiKakuGo-W5（日文黑體）</option>
              </optgroup>
              <optgroup label="僅支援英文">
                <option value="Helvetica">Helvetica</option>
                <option value="Helvetica-Bold">Helvetica-Bold</option>
                <option value="Times-Roman">Times-Roman</option>
                <option value="Courier">Courier</option>
              </optgroup>
            </select>
          </div>
        </div>
      </template>

      <div>
        <label>模式</label>
        <div class="radio-group">
          <label><input type="radio" value="grid"   x-model="mode" @change="debouncePreview()"> 格狀排列</label>
          <label><input type="radio" value="insert" x-model="mode" @change="debouncePreview()"> 指定位置</label>
        </div>
      </div>

      <!-- Advanced (collapsed) -->
      <button class="adv-toggle" @click="showAdvanced = !showAdvanced">
        <span x-text="showAdvanced ? '▼' : '▶'"></span> 進階選項
      </button>

      <div x-show="showAdvanced" class="adv-section">

        <template x-if="mode === 'grid'">
          <div style="display:flex;flex-direction:column;gap:9px;">
            <div>
              <label>水平重複</label>
              <div class="slider-row">
                <input type="range" min="1" max="10" step="1" x-model="horizontalBoxes" @input="debouncePreview()">
                <span class="slider-val" x-text="horizontalBoxes"></span>
              </div>
            </div>
            <div>
              <label>垂直重複</label>
              <div class="slider-row">
                <input type="range" min="1" max="15" step="1" x-model="verticalBoxes" @input="debouncePreview()">
                <span class="slider-val" x-text="verticalBoxes"></span>
              </div>
            </div>
            <label class="check-label">
              <input type="checkbox" x-model="margin" @change="debouncePreview()"> 留邊距
            </label>
          </div>
        </template>

        <template x-if="mode === 'insert'">
          <div style="display:flex;flex-direction:column;gap:9px;">
            <div>
              <label>水平位置（0=左，1=右）</label>
              <div class="slider-row">
                <input type="range" min="0" max="1" step="0.05" x-model="posX" @input="debouncePreview()">
                <span class="slider-val" x-text="parseFloat(posX).toFixed(2)"></span>
              </div>
            </div>
            <div>
              <label>垂直位置（0=下，1=上）</label>
              <div class="slider-row">
                <input type="range" min="0" max="1" step="0.05" x-model="posY" @input="debouncePreview()">
                <span class="slider-val" x-text="parseFloat(posY).toFixed(2)"></span>
              </div>
            </div>
            <div>
              <label>水平對齊</label>
              <select x-model="horizontalAlignment" @change="debouncePreview()">
                <option value="center">置中</option>
                <option value="left">靠左</option>
                <option value="right">靠右</option>
              </select>
            </div>
          </div>
        </template>

        <div>
          <label>平行處理數量</label>
          <div class="slider-row">
            <input type="range" min="1" max="8" step="1" x-model="workers">
            <span class="slider-val" x-text="workers"></span>
          </div>
        </div>

        <label class="check-label">
          <input type="checkbox" x-model="unselectable" @change="debouncePreview()">
          文字不可選取（檔案較大）
        </label>

      </div>

      <!-- Output -->
      <div class="section-title">輸出設定</div>
      <div>
        <label>輸出路徑（留空則覆蓋原檔）</label>
        <input type="text" x-model="outputPath" placeholder="C:\...\output.pdf 或資料夾">
      </div>

      <!-- Status -->
      <div x-show="statusMsg"
           :class="statusOk ? 'alert alert-ok' : 'alert alert-error'"
           x-text="statusMsg">
      </div>

    </div><!-- /left-panel -->

    <!-- ── Right: Preview ── -->
    <div class="right-panel">
      <div class="preview-half">
        <h3>原始 PDF（第 1 頁）</h3>
        <canvas id="canvas-original"></canvas>
        <div x-show="!filePath" class="preview-hint">請先選擇 PDF 檔案</div>
      </div>
      <div class="preview-half">
        <h3>套用後預覽（第 1 頁）</h3>
        <canvas id="canvas-preview"></canvas>
        <div x-show="previewLoading" class="preview-hint">預覽產生中…</div>
        <div x-show="previewErr && !previewLoading" class="alert alert-error" x-text="previewErr"></div>
        <div x-show="!filePath && !previewLoading && !previewErr" class="preview-hint">預覽將在此顯示</div>
      </div>
    </div>

  </div><!-- /main -->

  <script src="/static/pdfjs/pdf.min.js"></script>
  <script>
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/pdfjs/pdf.worker.min.js';

    function app() {
      return {
        // File
        filePath: '', pathError: '', dragOver: false,
        // Watermark
        watermarkType: 'text', watermark: '機密文件',
        // Style
        opacity: 0.3, angle: 45, textColor: '#000000',
        textFont: 'STSong-Light', textSize: 24,
        // Mode
        mode: 'grid',
        // Grid
        horizontalBoxes: 3, verticalBoxes: 6, margin: false,
        // Insert
        posX: 0.5, posY: 0.5, horizontalAlignment: 'center',
        // Advanced
        workers: 1, unselectable: false,
        // Output
        outputPath: '',
        // UI state
        showAdvanced: false, processing: false,
        previewLoading: false, previewErr: '',
        statusMsg: '', statusOk: true,
        _t: null,

        get cjkFontWarning() {
          const cjk = /[一-鿿぀-ヿ가-힯]/.test(this.watermark);
          const latin = ['Helvetica','Helvetica-Bold','Times-Roman','Courier',
                         'Symbol','ZapfDingbats'].includes(this.textFont);
          return cjk && latin;
        },

        init() { /* initial state already set above */ },

        async handleDrop(event) {
          this.dragOver = false;
          const file = event.dataTransfer.files[0];
          if (!file) return;
          if (!file.name.match(/\.pdf$/i)) {
            this.pathError = '只接受 PDF 檔案';
            return;
          }
          await this._upload(file);
        },

        async handleFileInput(event) {
          const file = event.target.files[0];
          if (file) await this._upload(file);
        },

        async _upload(file) {
          this.pathError = '';
          const fd = new FormData();
          fd.append('file', file);
          const res = await fetch('/api/upload', { method: 'POST', body: fd });
          const data = await res.json();
          if (data.error) { this.pathError = data.error; return; }
          this.filePath = data.temp_path;
          await this._loadOriginal();
          this.debouncePreview();
        },

        async onPathInput() {
          this.pathError = '';
          if (!this.filePath) return;
          await this._loadOriginal();
          this.debouncePreview();
        },

        debouncePreview() {
          clearTimeout(this._t);
          this._t = setTimeout(() => this._doPreview(), 500);
        },

        async _loadOriginal() {
          if (!this.filePath) return;
          try {
            await this._renderCanvas(
              `/api/raw?path=${encodeURIComponent(this.filePath)}`,
              'canvas-original'
            );
          } catch (e) {
            this.pathError = '無法讀取 PDF：' + e.message;
          }
        },

        async _doPreview() {
          if (!this.filePath || !this.watermark) return;
          this.previewLoading = true;
          this.previewErr = '';
          try {
            const res = await fetch('/api/preview', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(this._payload()),
            });
            if (!res.ok) {
              const d = await res.json();
              this.previewErr = d.error || '預覽失敗';
              return;
            }
            const blob = await res.blob();
            const url  = URL.createObjectURL(blob);
            await this._renderCanvas(url, 'canvas-preview');
            URL.revokeObjectURL(url);
          } catch (e) {
            this.previewErr = e.message;
          } finally {
            this.previewLoading = false;
          }
        },

        async _renderCanvas(url, id) {
          const pdf  = await pdfjsLib.getDocument(url).promise;
          const page = await pdf.getPage(1);
          const vp   = page.getViewport({ scale: 1.4 });
          const canvas = document.getElementById(id);
          canvas.width  = vp.width;
          canvas.height = vp.height;
          await page.render({ canvasContext: canvas.getContext('2d'), viewport: vp }).promise;
        },

        _payload() {
          return {
            file_path: this.filePath,
            watermark: this.watermark,
            opacity:   parseFloat(this.opacity),
            angle:     parseFloat(this.angle),
            text_color: this.textColor,
            text_font:  this.textFont,
            text_size:  parseInt(this.textSize),
            mode: this.mode,
            horizontal_boxes: parseInt(this.horizontalBoxes),
            vertical_boxes:   parseInt(this.verticalBoxes),
            margin:     this.margin,
            x:          parseFloat(this.posX),
            y:          parseFloat(this.posY),
            horizontal_alignment: this.horizontalAlignment,
            unselectable: this.unselectable,
          };
        },

        async process() {
          this.processing = true;
          this.statusMsg  = '';
          try {
            const res = await fetch('/api/process', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                ...this._payload(),
                output_path: this.outputPath || null,
                workers:     parseInt(this.workers),
              }),
            });
            const data = await res.json();
            if (data.error) {
              this.statusMsg = '錯誤：' + data.error;
              this.statusOk  = false;
            } else {
              this.statusMsg = `✓ 完成！已處理 ${data.count} 個檔案 → ${data.output_path}`;
              this.statusOk  = true;
            }
          } catch (e) {
            this.statusMsg = '網路錯誤：' + e.message;
            this.statusOk  = false;
          } finally {
            this.processing = false;
          }
        },
      };
    }
  </script>
</body>
</html>
```

- [ ] **Step 2: Run the existing test to verify HTML still passes**

```powershell
uv run pytest tests/test_gui_app.py::test_index_returns_html -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```powershell
git add src/pdf_watermark/gui/templates/index.html
git commit -m "feat: complete Alpine.js UI with live preview and Traditional Chinese support"
```

---

## Task 6: Smoke test

**Files:** None (verification only)

- [ ] **Step 1: Run all GUI tests**

```powershell
uv run pytest tests/test_gui_app.py tests/test_gui_routes.py tests/test_register_fonts.py -v
```

Expected: All tests PASS (Poppler-dependent tests are in other files and remain skipped/failed as before).

- [ ] **Step 2: Start the server**

```powershell
uv run watermark-gui
```

Expected: Console shows `Running on http://127.0.0.1:7860`, browser opens automatically.

- [ ] **Step 3: Manual checklist in browser**

Work through these in order:

1. Drag a PDF onto the drop zone → original PDF renders in top-right panel
2. Default watermark `機密文件` with `STSong-Light` → preview renders Chinese correctly (no boxes)
3. Change font to `Helvetica` → yellow warning `⚠ 偵測到中文字元` appears
4. Change font back to `STSong-Light` → warning disappears, preview updates
5. Move opacity slider to 0.5 → preview re-renders after 500ms
6. Toggle "進階選項" → section expands; change horizontal repeat to 5 → preview updates
7. Switch mode to "指定位置" → advanced section shows x/y sliders instead of grid sliders
8. Enter a valid output path, click "產生浮水印" → green success message shows
9. Enter a non-existent path in the file input → red border + error message

- [ ] **Step 4: Final commit**

```powershell
git add .
git commit -m "feat: pdf-watermark GUI complete — Flask + Alpine.js + PDF.js with live preview"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|-----------------|------|
| Flask + Alpine.js + PDF.js | T1–T5 |
| Offline static assets | T4 |
| `uv run watermark-gui` entry | T1 |
| Auto-open browser, port 7860 | T2 app.py |
| `WATERMARK_GUI_PORT` env var | T2 app.py |
| 5 API routes (index, upload, raw, preview, process, fonts) | T3 |
| Two-panel layout with original vs preview | T5 HTML |
| Live preview debounce 500ms | T5 JS `debouncePreview()` |
| Drag-and-drop single PDF | T5 JS `handleDrop()` |
| Path input for file or directory | T5 HTML + `onPathInput()` |
| All common params (opacity, angle, color, font, size, mode) | T5 HTML |
| Advanced params (grid size, insert position, workers, unselectable) | T5 HTML |
| CJK fonts listed first with label | T5 HTML `<optgroup>` |
| CJK warning when Latin font + Chinese text | T5 JS `get cjkFontWarning()` |
| `lang="zh-Hant"` + UTF-8 | T5 HTML `<head>` |
| Error handling for all edge cases | T3 routes + T5 JS |
| Temp file cleanup on shutdown | T2 `app.py` atexit |
