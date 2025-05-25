from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict
from enum import Enum

class AgentType(str, Enum):
    RESUME_WRITER = "RESUME_WRITER"
    CONTENT_ANALYZER = "CONTENT_ANALYZER"
    TECHNICAL_EVALUATOR = "TECHNICAL_EVALUATOR"
    CULTURE_EVALUATOR = "CULTURE_EVALUATOR"
    FINAL_REVIEWER = "FINAL_REVIEWER"
    
    @classmethod
    def to_korean(cls, role: str) -> str:
        if role == cls.RESUME_WRITER:
            return "자소서 작성"
        elif role == cls.TECHNICAL_EVALUATOR:
            return "기술 평가"
        elif role == cls.CULTURE_EVALUATOR:
            return "조직문화 평가"
        elif role == cls.FINAL_REVIEWER:
            return "최종 검토"
        elif role == cls.CONTENT_ANALYZER:
            return "내용 분석"
        else:
            return role

class EvaluationType(str, Enum):
    TECHNICAL = "technical"
    CULTURE = "culture"
    BOTH = "both"

class ResumeQuestion(TypedDict):
    question_id: int
    content: str  # 질문 내용
    max_length: int  # 최대 글자수
    min_length: Optional[int]  # 최소 글자수
    category: Optional[str]  # 질문 카테고리 (직무역량, 성장과정, 지원동기 등)

class ResumeState(TypedDict):
    organization: str
    position: str
    requirements: str
    description: str
    company_values: Optional[str]
    user_profile: Dict[str, str]
    questions: List[Dict[str, Any]]
    current_question_id: int
    messages: List[Dict[str, str]]
    drafts: Dict[int, str]
    evaluation_types: Dict[int, str]  # ContentAnalyzer의 결과를 저장
    technical_feedbacks: Dict[int, str]
    culture_feedbacks: Dict[int, str]
    final_drafts: Dict[int, str]
    current_step: str

    def __init__(
        self,
        organization: str,
        position: str,
        requirements: str,
        description: str,
        company_values: Optional[str],
        user_profile: Dict[str, str],
        questions: List[Dict[str, Any]]
    ):
        self.state = {
            "organization": organization,
            "position": position,
            "requirements": requirements,
            "description": description,
            "company_values": company_values,
            "user_profile": user_profile,
            "messages": [],
            "current_step": "START",
            "questions": questions,
            "current_question_id": questions[0]["question_id"] if questions else None,
            "drafts": {},
            "evaluation_types": {},
            "technical_feedbacks": {},
            "culture_feedbacks": {},
            "final_drafts": {},
            "docs": {}
        }
    
    def update(self, updates: Dict[str, Any]) -> None:
        self.state.update(updates) 