from flask import Flask, render_template


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("index.html")
