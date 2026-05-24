"""
conftest.py — Fixtures dùng chung cho toàn bộ test suite.
Tạo FastAPI app không có lifespan DB để unit tests chạy được mà không cần PostgreSQL.
"""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.entrypoints.api_v1.router import api_v1_router


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Trả về FastAPI app không có lifespan DB — dùng cho unit tests."""
    app = FastAPI(title="Q-School Test App")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_v1_router)
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """HTTP test client, dependency overrides được reset sau mỗi test."""
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c
    test_app.dependency_overrides.clear()
