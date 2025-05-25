from typing import Optional
from backend.workflow.agents.resume_agent import ResumeWritingAgent
from backend.workflow.agents.evaluation_agents import TechnicalEvaluator, CultureEvaluator, FinalReviewer
from backend.workflow.state import ResumeState, AgentType
from langgraph.graph import StateGraph, END
from backend.workflow.agents.content_analyzer import ContentAnalyzer

def create_resume_graph(enable_rag: bool = True, session_id: str = None) -> StateGraph:
    workflow = StateGraph(ResumeState)
    
    # 에이전트 인스턴스 생성
    k_value = 2 if enable_rag else 0
    resume_writer = ResumeWritingAgent(k=k_value, session_id=session_id)
    content_analyzer = ContentAnalyzer(k=k_value, session_id=session_id)
    tech_evaluator = TechnicalEvaluator(k=k_value, session_id=session_id)
    culture_evaluator = CultureEvaluator(k=k_value, session_id=session_id)
    final_reviewer = FinalReviewer(k=k_value, session_id=session_id)
    
    # 노드 추가
    workflow.add_node(AgentType.RESUME_WRITER, resume_writer.run)
    workflow.add_node(AgentType.CONTENT_ANALYZER, content_analyzer.run)
    workflow.add_node(AgentType.TECHNICAL_EVALUATOR, tech_evaluator.run)
    workflow.add_node(AgentType.CULTURE_EVALUATOR, culture_evaluator.run)
    workflow.add_node(AgentType.FINAL_REVIEWER, final_reviewer.run)
    
    # 분석 결과에 따른 라우팅
    def route_after_analysis(state: ResumeState):
        evaluation_type = state["evaluation_types"].get(state["current_question_id"])
        
        if evaluation_type == "both":
            return AgentType.TECHNICAL_EVALUATOR
        elif evaluation_type == "technical":
            return AgentType.TECHNICAL_EVALUATOR
        else:  # "culture"
            return AgentType.CULTURE_EVALUATOR
            
    def route_after_tech(state: ResumeState):
        evaluation_type = state["evaluation_types"].get(state["current_question_id"])
        if evaluation_type == "both":
            return AgentType.CULTURE_EVALUATOR
        return AgentType.FINAL_REVIEWER
    
    # 워크플로우 엣지 설정
    # 초안 작성 -> 컨텐츠 분석
    workflow.add_edge(AgentType.RESUME_WRITER, AgentType.CONTENT_ANALYZER)
    
    # 컨텐츠 분석 결과에 따라 평가자 라우팅
    workflow.add_conditional_edges(
        AgentType.CONTENT_ANALYZER,
        route_after_analysis,
        [AgentType.TECHNICAL_EVALUATOR, AgentType.CULTURE_EVALUATOR]
    )
    
    # 기술 평가 후 문화 평가 또는 최종 검토로
    workflow.add_conditional_edges(
        AgentType.TECHNICAL_EVALUATOR,
        route_after_tech,
        [AgentType.CULTURE_EVALUATOR, AgentType.FINAL_REVIEWER]
    )
    
    # 문화 평가 -> 최종 검토
    workflow.add_edge(AgentType.CULTURE_EVALUATOR, AgentType.FINAL_REVIEWER)
    
    # 최종 검토 -> 종료
    workflow.add_edge(AgentType.FINAL_REVIEWER, END)
    
    # 시작점 설정
    workflow.set_entry_point(AgentType.RESUME_WRITER)
    
    return workflow.compile()

if __name__ == "__main__":
    graph = create_resume_graph(True)
    graph_image = graph.get_graph().draw_mermaid_png()
    
    output_path = "resume_graph.png"
    with open(output_path, "wb") as f:
        f.write(graph_image) 