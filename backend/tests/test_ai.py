import pytest
try:
    from app.ai.client import generate_content, test_gemini_connection as check_gemini_connection
except ImportError:
    from backend.app.ai.client import generate_content, test_gemini_connection as check_gemini_connection

def test_generate_content_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    res = generate_content("Test prompt")
    assert res["success"] is False
    assert res["fallback"] is True
    assert "GEMINI_API_KEY" in res["error"]

def test_connection_helper_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    res = check_gemini_connection()
    assert res["connected"] is False
    assert "GEMINI_API_KEY" in res["message"]
