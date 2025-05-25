from backend.workflow.agents.agent import Agent
from backend.workflow.state import AgentType
from typing import Dict, Any

class TechnicalEvaluator(Agent):
    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="""당신은 해당 직무 분야의 전문가(팀장)입니다.
            지원자의 자기소개서를 기술적 측면에서 평가하고 구체적인 피드백을 제공해주세요.""",
            role=AgentType.TECHNICAL_EVALUATOR,
            k=k,
            session_id=session_id,
        )
    
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        current_question = next(
            q for q in state['questions'] 
            if q['question_id'] == state['current_question_id']
        )
        current_draft = state['drafts'][state['current_question_id']]
        
        return f"""
        다음 자기소개서 답변을 기술적 측면에서 평가해주세요:

        [문항]
        {current_question['content']}
        
        [답변]
        {current_draft}
        
        [직무 정보]
        직무/포지션: {state['position']}
        요구사항: {state['requirements']}
        
        [검증 정보]
        {state.get('context', '검증 정보 없음')}
        
        다음 기준으로 평가해주세요:
        1. 직무 관련 기술적 역량이 잘 드러나는가?
        2. 구체적인 기술 경험과 프로젝트가 잘 설명되었는가?
        3. 해당 직무에 필요한 핵심 기술이 누락되지 않았는가?
        4. 기술적 성과와 문제 해결 능력이 잘 표현되었는가?
        5. 답변의 진실성이 검증되었는가? (수집된 정보 기반)
        
        응답 형식:
        1. 평가 결과 요약
        2. 각 평가 기준별 점수(1-5점)와 구체적 피드백
        3. 검증 결과 (수집된 정보와의 일치성, 신뢰성)
        4. 개선 제안
        """

class CultureEvaluator(Agent):
    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="""당신은 HR 팀장입니다.
            지원자의 자기소개서를 조직문화 적합성과 인성 측면에서 평가하고 구체적인 피드백을 제공해주세요.""",
            role=AgentType.CULTURE_EVALUATOR,
            k=k,
            session_id=session_id,
        )
    
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        current_question = next(
            q for q in state['questions'] 
            if q['question_id'] == state['current_question_id']
        )
        current_draft = state['drafts'][state['current_question_id']]
        
        return f"""
        다음 자기소개서 답변을 조직문화 적합성 측면에서 평가해주세요:

        [문항]
        {current_question['content']}
        
        [답변]
        {current_draft}
        
        [회사 정보]
        회사/조직: {state['organization']}
        회사가치: {state.get('company_values', '정보 없음')}
        
        [검증 정보]
        {state.get('context', '검증 정보 없음')}
        
        다음 기준으로 평가해주세요:
        1. 회사의 가치관과 문화에 부합하는가?
        2. 협업 능력과 커뮤니케이션 스킬이 잘 드러나는가?
        3. 지원자의 성장 가능성과 열정이 잘 표현되었는가?
        4. 회사에 대한 이해도가 충분히 반영되었는가?
        5. 답변의 진실성이 검증되었는가? (수집된 정보 기반)
        
        응답 형식:
        1. 평가 결과 요약
        2. 각 평가 기준별 점수(1-5점)와 구체적 피드백
        3. 검증 결과 (수집된 정보와의 일치성, 신뢰성)
        4. 개선 제안
        """

class FinalReviewer(Agent):
    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="""당신은 전문적인 자기소개서 작성 도우미입니다.
            받은 피드백을 바탕으로 자기소개서를 개선하여 최종본을 작성해주세요.""",
            role=AgentType.FINAL_REVIEWER,
            k=k,
            session_id=session_id,
        )
    
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        current_question = next(
            q for q in state['questions'] 
            if q['question_id'] == state['current_question_id']
        )
        current_draft = state['drafts'][state['current_question_id']]
        tech_feedback = state['technical_feedbacks'].get(state['current_question_id'], '')
        culture_feedback = state['culture_feedbacks'].get(state['current_question_id'], '')
        
        return f"""
        다음 자기소개서 답변과 피드백을 바탕으로 개선된 최종본을 작성해주세요:

        [문항 정보]
        질문: {current_question['content']}
        글자수 제한: {current_question['max_length']}자
        
        [초안]
        {current_draft}
        
        [기술 평가 피드백]
        {tech_feedback}
        
        [조직문화 평가 피드백]
        {culture_feedback}
        
        다음 사항을 고려하여 최종본을 작성해주세요:
        1. 모든 피드백을 적절히 반영
        2. 글자수 제한 준수 (반드시 {current_question['max_length']}자 이내)
        3. 질문 의도에 맞는 내용 구성
        4. 가독성과 설득력 강화
        
        최종 답변을 작성해주세요.
        """ 