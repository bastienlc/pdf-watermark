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
