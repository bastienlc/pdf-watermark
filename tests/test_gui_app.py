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
