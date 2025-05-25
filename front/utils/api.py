import requests
from typing import Dict, Any, List

def get_api_url() -> str:
    """API 기본 URL을 반환합니다."""
    return "http://localhost:8000"

def send_resume_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """자기소개서 작성 요청을 보냅니다."""
    url = f"{get_api_url()}/resume/api/v1/resume/create"  # API 경로 수정
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API 요청 실패: {str(e)}")

def get_resume_status(session_id: str) -> Dict[str, Any]:
    """자기소개서 작성 상태를 조회합니다."""
    url = f"{get_api_url()}/resume/api/v1/resume/status/{session_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"상태 조회 실패: {str(e)}")

def get_resume_histories() -> List[Dict[str, Any]]:
    """자기소개서 히스토리 목록을 조회합니다."""
    url = f"{get_api_url()}/resume/histories"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"히스토리 조회 실패: {str(e)}")

def get_resume_detail(history_id: int) -> Dict[str, Any]:
    """자기소개서 히스토리 상세 정보를 조회합니다."""
    url = f"{get_api_url()}/resume/histories/{history_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"상세 정보 조회 실패: {str(e)}")

def delete_resume_history(history_id: int) -> bool:
    """자기소개서 히스토리를 삭제합니다."""
    url = f"{get_api_url()}/resume/histories/{history_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False 