import os

def get_api_url() -> str:
    """백엔드 API URL을 반환합니다."""
    return os.getenv("API_URL", "http://localhost:8000") 