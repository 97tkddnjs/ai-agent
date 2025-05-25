import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from backend.workflow.graph import create_resume_graph
from backend.workflow.state import ResumeState

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resume", tags=["resume"])

class ResumeQuestion(BaseModel):
    question_id: int
    content: str
    max_length: int
    min_length: int
    category: str

class UserProfile(BaseModel):
    education: str
    experience: str
    skills: str
    certificates: str
    projects: str
    achievements: str

class ResumeRequest(BaseModel):
    organization: str = Field(..., description="회사/조직명")
    position: str = Field(..., description="직무/포지션")
    requirements: str = Field(..., description="주요 요구사항")
    description: str = Field(..., description="직무 설명")
    company_values: Optional[str] = Field(None, description="회사 가치/문화")
    user_profile: UserProfile = Field(..., description="지원자 프로필")
    questions: List[ResumeQuestion] = Field(..., description="자기소개서 문항 목록")

class ResumeState:
    def __init__(self, organization: str, position: str, requirements: str, 
                 description: str, company_values: Optional[str], 
                 user_profile: Dict[str, Any], questions: List[Dict[str, Any]]):
        self.state = {
            "organization": organization,
            "position": position,
            "requirements": requirements,
            "description": description,
            "company_values": company_values,
            "user_profile": user_profile,
            "questions": questions,
            "drafts": {},
            "evaluation_types": {},
            "technical_feedbacks": {},
            "culture_feedbacks": {},
            "final_drafts": {},
            "messages": []
        }

@router.post("/create")
async def create_resume(request: ResumeRequest):
    try:
        logger.info(f"Received resume creation request: {request}")
        
        # 초기 상태 생성 - current_question_id 추가
        initial_state = {
            "organization": request.organization,
            "position": request.position,
            "requirements": request.requirements,
            "description": request.description,
            "company_values": request.company_values,
            "user_profile": request.user_profile.dict(),
            "questions": [q.dict() for q in request.questions],
            "current_question_id": 1,  # 첫 번째 문항부터 시작
            "drafts": {},
            "evaluation_types": {},
            "technical_feedbacks": {},
            "culture_feedbacks": {},
            "final_drafts": {},
            "messages": []
        }
        
        logger.info("Creating resume graph...")
        graph = create_resume_graph()
        
        logger.info("Executing resume graph...")
        final_state = graph.invoke(initial_state)
        
        response = {
            "drafts": final_state.get("drafts", {}),
            "evaluation_types": final_state.get("evaluation_types", {}),
            "technical_feedbacks": final_state.get("technical_feedbacks", {}),
            "culture_feedbacks": final_state.get("culture_feedbacks", {}),
            "final_drafts": final_state.get("final_drafts", {}),
            "messages": final_state.get("messages", [])
        }
        
        logger.info("Resume creation completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error during resume creation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"자기소개서 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/status/{session_id}")
async def get_resume_status(session_id: str):
    """자기소개서 생성 상태를 확인합니다."""
    try:
        # TODO: 세션 상태 조회 로직 구현
        return {"status": "processing"}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"세션을 찾을 수 없습니다: {str(e)}"
        ) 