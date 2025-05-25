from backend.workflow.agents.agent import Agent, AgentState
from backend.workflow.state import AgentType
from typing import Dict, Any

class ResumeWritingAgent(Agent):
    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="""당신은 전문적인 자기소개서 작성 도우미입니다. 
            주어진 질문의 의도를 정확히 파악하고, 글자수 제한을 준수하면서 
            지원자의 경험과 회사의 요구사항을 잘 매칭시켜 설득력 있는 자기소개서를 작성해주세요.""",
            role=AgentType.RESUME_WRITER,
            k=k,
            session_id=session_id,
        )
    
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        current_question = next(
            q for q in state['questions'] 
            if q['question_id'] == state['current_question_id']
        )
        
        return f"""
        다음 자기소개서 문항에 대한 답변을 작성해주세요:

        [문항 정보]
        질문: {current_question['content']}
        글자수 제한: {current_question['min_length'] or 0} ~ {current_question['max_length']}자
        문항 유형: {current_question['category'] or '일반'}
        
        [회사 정보]
        회사/조직: {state['organization']}
        직무/포지션: {state['position']}
        요구사항: {state['requirements']}
        상세설명: {state['description']}
        회사가치: {state.get('company_values', '정보 없음')}
        
        [지원자 프로필]
        교육: {state['user_profile']['education']}
        경력: {state['user_profile']['experience']}
        기술: {state['user_profile']['skills']}
        자격증: {state['user_profile']['certificates']}
        프로젝트: {state['user_profile']['projects']}
        성과: {state['user_profile']['achievements']}
        
        {state.get('context', '')}
        
        다음 사항을 고려하여 작성해주세요:
        1. 질문의 의도에 맞는 내용 구성
        2. 구체적인 경험과 성과 중심으로 작성
        3. 회사의 요구사항과 가치에 부합하는 내용 선택
        4. 정확한 글자수 제한 준수 (반드시 {current_question['max_length']}자 이내)
        5. 문단 구성을 통한 가독성 확보
        
        답변을 작성해주세요.
        """

   