import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from ghkit.fastapi import error_handler


@pytest.fixture
def app():
    app = FastAPI()
    app.add_exception_handler(HTTPException, error_handler)
    return app


@pytest.fixture
def client(app):
    return TestClient(app=app)


def test_error_handling(app, client):
    """测试错误处理"""

    @app.get("/test")
    async def test_endpoint():
        raise HTTPException(status_code=404, detail="Not Found")

    response = client.get("/test")
    assert response.status_code == 404
    assert response.json() == {"code": 404, "message": "Not Found"}
