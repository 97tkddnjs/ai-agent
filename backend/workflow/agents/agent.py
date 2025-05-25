from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import BaseMessage
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.utils.config import get_llm
from backend.workflow.state import ResumeState, AgentType
from backend.rag.vector_store import search_info
import json

class AgentState(TypedDict):
    resume_state: Dict[str, Any]  # 전체 자소서 상태
    context: str  # 검색된 컨텍스트
    messages: List[BaseMessage]  # LLM에 전달할 메시지
    response: str  # LLM 응답

class Agent(ABC):
    def __init__(
        self, 
        system_prompt: str, 
        role: str, 
        k: int = 2, 
        session_id: str = None
    ):
        self.system_prompt = system_prompt
        self.role = role
        self.k = k
        self._setup_graph()
        self.session_id = session_id

    def _setup_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("prepare_messages", self._prepare_messages)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("update_state", self._update_state)
        
        workflow.add_edge("retrieve_context", "prepare_messages")
        workflow.add_edge("prepare_messages", "generate_response")
        workflow.add_edge("generate_response", "update_state")
        
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("update_state", END)
        
        self.graph = workflow.compile()

    def _retrieve_context(self, state: AgentState) -> AgentState:
        if self.k <= 0:
            return {**state, "context": ""}

        resume_state = state["resume_state"]
        current_question_id = resume_state["current_question_id"]
        
        # 현재 문항과 답변 가져오기
        current_question = next(
            q for q in resume_state["questions"] 
            if q["question_id"] == current_question_id
        )
        current_draft = resume_state["drafts"].get(current_question_id, "")

        # 검색 쿼리 구성
        if self.role == AgentType.RESUME_WRITER:
            query = f"{resume_state['organization']} {resume_state['position']} {current_question['category']}"
        else:
            # 평가자의 경우 자소서 내용 기반 검증
            if not current_draft:  # 초안이 없으면 검색 불가
                return {**state, "context": ""}
            
            # RAG 검색 수행
            search_results = search_info(
                content=current_draft,
                role=self.role,
                query=current_question['content'],
                k=self.k
            )
            
            # 검색 결과 포맷팅
            context = self._format_search_results(search_results)
            return {**state, "context": context}

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return ""
            
        formatted_text = "검증을 위해 수집된 정보:\n\n"
        for i, result in enumerate(results, 1):
            formatted_text += f"[정보 {i}]\n"
            formatted_text += f"출처: {result['source']}\n"
            formatted_text += f"주제: {result['topic']}\n"
            formatted_text += f"내용: {result['content']}\n\n"
        
        return formatted_text

    def _prepare_messages(self, state: AgentState) -> AgentState:
        resume_state = state["resume_state"]
        context = state["context"]
        
        messages = [SystemMessage(content=self.system_prompt)]
        
        for message in resume_state.get("messages", []):
            if message["role"] == "assistant":
                messages.append(AIMessage(content=message["content"]))
            else:
                messages.append(
                    HumanMessage(content=f"{message['role']}: {message['content']}")
                )
        
        prompt = self._create_prompt({**resume_state, "context": context})
        messages.append(HumanMessage(content=prompt))
        
        return {**state, "messages": messages}

    @abstractmethod
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        pass

    def _generate_response(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        response = get_llm().invoke(messages)
        return {**state, "response": response.content}

    def _update_state(self, state: AgentState) -> AgentState:
        resume_state = state["resume_state"]
        response = state["response"]
        current_question_id = resume_state["current_question_id"]
        
        new_resume_state = resume_state.copy()
        new_resume_state["messages"].append({
            "role": self.role,
            "content": response
        })
        new_resume_state["current_step"] = self.role
        
        # 각 에이전트별 상태 업데이트
        if self.role == AgentType.RESUME_WRITER:
            new_resume_state["drafts"][current_question_id] = response
        elif self.role == AgentType.CONTENT_ANALYZER:
            # JSON 응답에서 평가 유형 추출
            analysis_result = json.loads(response)
            new_resume_state["evaluation_types"][current_question_id] = analysis_result["evaluation_type"]
        elif self.role == AgentType.TECHNICAL_EVALUATOR:
            new_resume_state["technical_feedbacks"][current_question_id] = response
        elif self.role == AgentType.CULTURE_EVALUATOR:
            new_resume_state["culture_feedbacks"][current_question_id] = response
        elif self.role == AgentType.FINAL_REVIEWER:
            new_resume_state["final_drafts"][current_question_id] = response
        
        return {**state, "resume_state": new_resume_state}

    def run(self, state: ResumeState) -> ResumeState:
        agent_state = AgentState(
            resume_state=state,
            context="",
            messages=[],
            response=""
        )
        
        result = self.graph.invoke(agent_state)
        return result["resume_state"]

class BaseAgent(ABC):
    """자소서 관련 에이전트들의 기본 추상 클래스"""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """상태를 받아서 처리하고 새로운 상태를 반환하는 추상 메서드"""
        pass
    
    @abstractmethod
    async def generate_response(self, context: Dict[str, Any]) -> str:
        """컨텍스트를 받아서 응답을 생성하는 추상 메서드"""
        pass

# class ResumeWritingAgent(Agent):
#     def __init__(self, k: int = 2, session_id: str = None):
#         super().__init__(
#             system_prompt="""당신은 전문적인 자기소개서 작성 도우미입니다.
#             주어진 질문의 의도를 정확히 파악하고, 글자수 제한을 준수하면서
#             지원자의 경험과 회사의 요구사항을 잘 매칭시켜 설득력 있는 자기소개서를 작성해주세요.""",
#             role=AgentType.RESUME_WRITER,
#             k=k,
#             session_id=session_id,
#         )
    
#     def _create_prompt(self, state: Dict[str, Any]) -> str:
#         current_question = next(
#             q for q in state['questions'] 
#             if q['question_id'] == state['current_question_id']
#         )
        
#         return f"""
#         다음 자기소개서 문항에 대한 답변을 작성해주세요:

#         [문항 정보]
#         질문: {current_question['content']}
#         글자수 제한: {current_question['min_length'] or 0} ~ {current_question['max_length']}자
        
#         [회사 정보]
#         회사/조직: {state['organization']}
#         직무/포지션: {state['position']}
#         요구사항: {state['requirements']}
#         상세설명: {state['description']}
#         회사가치: {state.get('company_values', '정보 없음')}
        
#         [지원자 프로필]
#         {state['user_profile']}
        
#         {state.get('context', '')}
        
#         다음 사항을 고려하여 작성해주세요:
#         1. 질문의 의도에 맞는 내용 구성
#         2. 구체적인 경험과 성과 중심으로 작성
#         3. 회사의 요구사항과 가치에 부합하는 내용 선택
#         4. 정확한 글자수 제한 준수
#         5. 문단 구성을 통한 가독성 확보
        
#         답변을 작성해주세요.
#         """

# class TechnicalEvaluator(Agent):
#     def __init__(self, k: int = 2, session_id: str = None):
#         super().__init__(
#             system_prompt="""당신은 해당 직무 분야의 전문가(팀장)입니다.
#             지원자의 자기소개서를 기술적 측면에서 평가하고 구체적인 피드백을 제공해주세요.""",
#             role=AgentType.TECHNICAL_EVALUATOR,
#             k=k,
#             session_id=session_id,
#         )
    
#     def _create_prompt(self, state: Dict[str, Any]) -> str:
#         current_question = next(
#             q for q in state['questions'] 
#             if q['question_id'] == state['current_question_id']
#         )
#         current_draft = state['drafts'][state['current_question_id']]
        
#         return f"""
#         다음 자기소개서 답변을 기술적 측면에서 평가해주세요:

#         [문항]
#         {current_question['content']}
        
#         [답변]
#         {current_draft}
        
#         [직무 정보]
#         직무/포지션: {state['position']}
#         요구사항: {state['requirements']}
        
#         {state.get('context', '')}
        
#         다음 기준으로 평가해주세요:
#         1. 직무 관련 기술적 역량이 잘 드러나는가?
#         2. 구체적인 기술 경험과 프로젝트가 잘 설명되었는가?
#         3. 해당 직무에 필요한 핵심 기술이 누락되지 않았는가?
#         4. 기술적 성과와 문제 해결 능력이 잘 표현되었는가?
        
#         구체적인 개선 제안을 포함하여 피드백을 작성해주세요.
#         """

# class CultureEvaluator(Agent):
#     def __init__(self, k: int = 2, session_id: str = None):
#         super().__init__(
#             system_prompt="""당신은 HR 부서의 전문가(팀장)입니다.
#             지원자의 자기소개서를 조직문화 적합성 측면에서 평가하고 구체적인 피드백을 제공해주세요.""",
#             role=AgentType.CULTURE_EVALUATOR,
#             k=k,
#             session_id=session_id,
#         )
    
#     def _create_prompt(self, state: Dict[str, Any]) -> str:
#         current_question = next(
#             q for q in state['questions'] 
#             if q['question_id'] == state['current_question_id']
#         )
#         current_draft = state['drafts'][state['current_question_id']]
        
#         return f"""
#         다음 자기소개서 답변을 조직문화 적합성 측면에서 평가해주세요:

#         [문항]
#         {current_question['content']}
        
#         [답변]
#         {current_draft}
        
#         [회사 정보]
#         회사/조직: {state['organization']}
#         회사가치: {state.get('company_values', '정보 없음')}
        
#         {state.get('context', '')}
        
#         다음 기준으로 평가해주세요:
#         1. 회사의 가치관과 문화에 부합하는가?
#         2. 협업 능력과 커뮤니케이션 스킬이 잘 드러나는가?
#         3. 지원자의 성장 가능성과 열정이 잘 표현되었는가?
#         4. 회사에 대한 이해도가 충분히 반영되었는가?
#         5. 답변이 진정성 있게 작성되었는가?
        
#         구체적인 개선 제안을 포함하여 피드백을 작성해주세요.
#         """

# class FinalReviewer(Agent):
#     def __init__(self, k: int = 2, session_id: str = None):
#         super().__init__(
#             system_prompt="""당신은 자기소개서 최종 검토 전문가입니다.
#             받은 피드백을 바탕으로 자기소개서를 개선하여 최종본을 작성해주세요.""",
#             role=AgentType.FINAL_REVIEWER,
#             k=k,
#             session_id=session_id,
#         )
    
#     def _create_prompt(self, state: Dict[str, Any]) -> str:
#         current_question = next(
#             q for q in state['questions'] 
#             if q['question_id'] == state['current_question_id']
#         )
#         current_draft = state['drafts'][state['current_question_id']]
#         tech_feedback = state['technical_feedbacks'].get(state['current_question_id'], '')
#         culture_feedback = state['culture_feedbacks'].get(state['current_question_id'], '')
        
#         return f"""
#         다음 자기소개서 답변과 피드백을 바탕으로 개선된 최종본을 작성해주세요:

#         [문항]
#         {current_question['content']}
#         글자수 제한: {current_question['min_length'] or 0} ~ {current_question['max_length']}자
        
#         [초안]
#         {current_draft}
        
#         [기술 평가 피드백]
#         {tech_feedback}
        
#         [조직문화 평가 피드백]
#         {culture_feedback}
        
#         다음 사항을 고려하여 최종본을 작성해주세요:
#         1. 모든 피드백을 적절히 반영
#         2. 글자수 제한 준수
#         3. 질문 의도에 맞는 내용 구성
#         4. 가독성과 설득력 강화
        
#         최종 답변을 작성해주세요.
#         """ 