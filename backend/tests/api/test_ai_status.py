# Tests for GET /api/v1/ai-status endpoint

import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ai_status_api_key_missing():
    # Test status = "API_KEY_MISSING" when GOOGLE_API_KEY is not configured
    with patch("backend.app.api.routes.GOOGLE_API_KEY", ""):
        response = client.get("/api/v1/ai-status")
        assert response.status_code == 200
        data = response.json()
        assert data["gemini_api_configured"] is False
        assert data["status"] == "API_KEY_MISSING"
        assert data["llm_enrichment_enabled"] is True
        assert data["fallback_enabled"] is True


def test_ai_status_fallback_mode():
    # Test status = "FALLBACK_MODE" when key is present but connectivity check fails
    with patch("backend.app.api.routes.GOOGLE_API_KEY", "fake_key"):
        with patch("backend.app.api.routes.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = Exception("API connectivity error")
            mock_client_class.return_value = mock_client
            
            response = client.get("/api/v1/ai-status")
            assert response.status_code == 200
            data = response.json()
            assert data["gemini_api_configured"] is True
            assert data["status"] == "FALLBACK_MODE"


def test_ai_status_ai_active():
    # Test status = "AI_ACTIVE" when key is present and connectivity check succeeds
    with patch("backend.app.api.routes.GOOGLE_API_KEY", "fake_key"):
        with patch("backend.app.api.routes.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            response = client.get("/api/v1/ai-status")
            assert response.status_code == 200
            data = response.json()
            assert data["gemini_api_configured"] is True
            assert data["status"] == "AI_ACTIVE"
            mock_client.models.generate_content.assert_called_once_with(
                model="gemini-2.5-flash",
                contents="hi",
                config={"max_output_tokens": 1}
            )
