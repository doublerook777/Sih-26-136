"""
Gemini AI Client for ProcuraAI (SIH 26136).
Provides structured problem statement drafting and fallback resilience.
"""
import os
import json
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL = "gemini-2.5-flash"


def get_gemini_client():
    """Initializes and returns a Google GenAI client if API key is available."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini GenAI client: {e}")
        return None


def generate_content(
    prompt: str,
    system_instruction: Optional[str] = None,
    response_mime_type: Optional[str] = None,
    response_schema: Optional[Any] = None,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = 10,
) -> Dict[str, Any]:
    """
    Generates content using Google Gemini with fallback handling and timeout.
    Returns a dictionary with status, text / json data, and metadata.
    """
    client = get_gemini_client()
    if not client:
        logger.info("GEMINI_API_KEY not set. Using offline template fallback.")
        return {
            "success": False,
            "fallback": True,
            "error": "GEMINI_API_KEY not configured",
            "content": None,
        }

    try:
        from google.genai import types

        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction
        if response_mime_type:
            config_args["response_mime_type"] = response_mime_type
        if response_schema:
            config_args["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_args) if config_args else None

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        text_output = response.text or ""
        parsed_json = None
        if response_mime_type == "application/json" or response_schema is not None:
            try:
                parsed_json = json.loads(text_output)
            except json.JSONDecodeError:
                parsed_json = None

        return {
            "success": True,
            "fallback": False,
            "text": text_output,
            "json": parsed_json,
            "model": model,
        }

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return {
            "success": False,
            "fallback": True,
            "error": str(e),
            "content": None,
        }


def test_gemini_connection() -> Dict[str, Any]:
    """Quick verification helper to test Gemini API connectivity."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "connected": False,
            "message": "GEMINI_API_KEY environment variable is not set. Please add it to your .env file."
        }

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    logger.info(f"Testing Gemini connection with key: {masked_key}")

    res = generate_content(
        prompt="Respond with exactly 'PONG: ProcuraAI SIH-26-136 Gemini Live' if you can read this.",
        model=DEFAULT_MODEL
    )

    if res["success"]:
        return {
            "connected": True,
            "model": res.get("model", DEFAULT_MODEL),
            "response": res.get("text", "").strip(),
            "message": "Gemini API test call succeeded!"
        }
    else:
        return {
            "connected": False,
            "error": res.get("error"),
            "message": f"Gemini test call failed: {res.get('error')}"
        }


if __name__ == "__main__":
    result = test_gemini_connection()
    print(json.dumps(result, indent=2))
