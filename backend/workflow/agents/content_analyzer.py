from backend.workflow.agents.agent import Agent, AgentState
from backend.workflow.state import AgentType, EvaluationType
from typing import Dict, Any
import json

class ContentAnalyzer(Agent):
    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="""당신은 자기소개서 내용을 분석하여 어떤 유형의 평가가 필요한지 판단하는 전문가입니다.
            기술적인 내용이 주를 이루면 technical, 문화적/개인적 내용이 주를 이루면 culture,
            둘 다 중요하게 다루어져야 한다면 both로 평가해주세요.""",
            role=AgentType.CONTENT_ANALYZER,
            k=k,
            session_id=session_id
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        current_id = state["current_question_id"]
        current_draft = state["drafts"].get(current_id, "")
        current_question = next(
            q for q in state["questions"] 
            if q["question_id"] == current_id
        )
        
        return f"""
        다음 자기소개서 내용을 분석하여 어떤 유형의 평가가 필요한지 판단해주세요.

        [문항]
        {current_question["content"]}

        [작성된 답변]
        {current_draft}

        [직무 정보]
        회사/조직: {state['organization']}
        직무/포지션: {state['position']}
        요구사항: {state['requirements']}

        다음 중 하나로 평가 유형을 결정해주세요:
        - technical: 기술적 역량 평가가 중점적으로 필요한 경우
        - culture: 문화적 적합성 평가가 중점적으로 필요한 경우
        - both: 기술적 역량과 문화적 적합성 모두 중요하게 평가해야 하는 경우

        다음 JSON 형식으로 응답해주세요:
        {{"evaluation_type": "technical|culture|both", "reason": "평가 유형 선택 이유"}}
        """

    def _update_state(self, state: AgentState) -> AgentState:
        resume_state = state["resume_state"]
        response = state["response"]
        current_id = resume_state["current_question_id"]
        
        try:
            analysis_result = json.loads(response)
            evaluation_type = analysis_result["evaluation_type"]
        except:
            evaluation_type = "both"  # 파싱 실패시 기본값
            
        new_resume_state = resume_state.copy()
        new_resume_state["evaluation_types"][current_id] = evaluation_type
        new_resume_state["current_step"] = self.role
        new_resume_state["messages"].append({
            "role": self.role,
            "content": response
        })
        
        return {**state, "resume_state": new_resume_state} 