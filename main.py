import streamlit as st
from front.components.sidebar import render_sidebar, init_session_state
from front.components.history import render_history, render_history_detail
from front.utils.api import send_resume_request
from typing import Dict, Any

def render_responses(response_data: Dict[str, Any]):
    """에이전트 응답을 화면에 표시합니다."""
    if not response_data:
        return
    
    # 초안 표시
    if "drafts" in response_data:
        st.subheader("📝 초안")
        for qid, draft in response_data["drafts"].items():
            with st.expander(f"문항 {qid} 초안", expanded=True):
                st.write(draft)
    
    # 기술 평가 표시
    if "technical_feedbacks" in response_data:
        st.subheader("💻 기술 평가")
        for qid, feedback in response_data["technical_feedbacks"].items():
            with st.expander(f"문항 {qid} 기술 평가", expanded=True):
                st.write(feedback)
    
    # 문화 평가 표시
    if "culture_feedbacks" in response_data:
        st.subheader("🤝 조직문화 평가")
        for qid, feedback in response_data["culture_feedbacks"].items():
            with st.expander(f"문항 {qid} 문화 평가", expanded=True):
                st.write(feedback)
    
    # 최종본 표시
    if "final_drafts" in response_data:
        st.subheader("✨ 최종본")
        for qid, final in response_data["final_drafts"].items():
            with st.expander(f"문항 {qid} 최종본", expanded=True):
                st.write(final)

def main():
    st.set_page_config(
        page_title="AI 자기소개서 작성",
        page_icon="📝",
        layout="wide"
    )
    
    # 세션 상태 초기화
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "new"
    if "current_response" not in st.session_state:
        st.session_state.current_response = None
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "selected_history" not in st.session_state:
        st.session_state.selected_history = None
    
    # 사이드바 탭
    tab1, tab2 = st.sidebar.tabs(["새 작성", "히스토리"])
    
    # 새 작성 탭
    with tab1:
        st.session_state.current_tab = "new"
         # 메인 영역
        st.title("🤖 AI 자기소개서 작성")
        st.markdown("""
        이 애플리케이션은 AI가 여러분의 자기소개서 작성을 도와드립니다.
        기술적 평가와 문화적 평가를 통해 더 나은 자기소개서를 작성할 수 있습니다.
        """)
        sidebar_result = render_sidebar()  # 새 작성 폼 표시
        
       
        
        if sidebar_result and sidebar_result.get("submit_clicked") and not st.session_state.is_processing:
            try:
                st.session_state.is_processing = True
                with st.spinner("자기소개서를 작성 중입니다..."):
                    request_data = {k: v for k, v in sidebar_result.items() if k != "submit_clicked"}
                    response = send_resume_request(request_data)
                    st.session_state.current_response = response
                st.success("자기소개서 작성이 완료되었습니다!")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
            finally:
                st.session_state.is_processing = False
                
        
    
    # 히스토리 탭
    with tab2:
        st.session_state.current_tab = "history"
        # 히스토리 목록만 표시
        st.title("📚 작성 히스토리")
        render_history()  # 히스토리 컴포넌트 렌더링
        
        # 선택된 히스토리 상세 표시
        if st.session_state.get("selected_history"):
            render_history_detail()
    if st.session_state.current_response:
            render_responses(st.session_state.current_response)
if __name__ == "__main__":
    main() 