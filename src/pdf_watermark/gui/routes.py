import os
import tempfile
from pathlib import Path

from flask import Flask, after_this_request, jsonify, render_template, request, send_file

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
        resolved = Path(path).resolve() if path else None
        if resolved is None or not resolved.is_file():
            return jsonify({"error": "檔案不存在"}), 404
        # Only serve PDF files (prevents serving arbitrary non-PDF content)
        if resolved.suffix.lower() != ".pdf":
            return jsonify({"error": "只提供 PDF 檔案"}), 403
        return send_file(str(resolved), mimetype="application/pdf")

    @app.route("/api/preview", methods=["POST"])
    def preview():
        data = request.get_json()
        if not data:
            return jsonify({"error": "無效的請求"}), 400
        input_path = data.get("file_path", "")
        if not os.path.isfile(input_path):
            return jsonify({"error": "找不到輸入檔案"}), 400
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                output_path = f.name
            _apply_watermark(input_path, output_path, data, verbose=False)

            @after_this_request
            def _cleanup_preview(response):
                try:
                    os.unlink(output_path)
                except Exception:
                    pass
                return response

            return send_file(output_path, mimetype="application/pdf")
        except Exception as e:
            try:
                os.unlink(output_path)
            except Exception:
                pass
            return jsonify({"error": str(e)}), 500

    @app.route("/api/process", methods=["POST"])
    def process():
        data = request.get_json()
        if not data:
            return jsonify({"error": "無效的請求"}), 400
        file_path = data.get("file_path", "")
        output_path = data.get("output_path") or None
        if not output_path:
            input_p = Path(file_path)
            if input_p.is_file():
                output_path = str(
                    input_p.parent / f"{input_p.stem}_watermark{input_p.suffix}"
                )
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

    @app.route("/api/browse")
    def browse():
        import tkinter as tk
        from tkinter import filedialog

        dialog_type = request.args.get("type", "file")  # file | directory | save
        initial_file = request.args.get("initial_file", "")

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        path = ""
        if dialog_type == "file":
            path = filedialog.askopenfilename(
                title="選擇 PDF 檔案",
                filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")],
            )
        elif dialog_type == "directory":
            path = filedialog.askdirectory(title="選擇資料夾")
        elif dialog_type == "save":
            path = filedialog.asksaveasfilename(
                title="選擇輸出位置",
                defaultextension=".pdf",
                filetypes=[("PDF 檔案", "*.pdf")],
                initialfile=initial_file,
            )
        root.destroy()
        return jsonify({"path": path or None})


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
