import pytest
import os

def test_api_key_exists():
    """Test that OPENAI_API_KEY is set in the environment."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    assert api_key is not None, "❌ OPENAI_API_KEY is not set in the environment variables."
    print("✅ OPENAI_API_KEY is available.")

if __name__ == "__main__":
    pytest.main(["-v", "-s"])