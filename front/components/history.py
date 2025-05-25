import streamlit as st
from datetime import datetime
from typing import Dict, Any
from ..utils.api import get_resume_histories, get_resume_detail, delete_resume_history

def format_datetime(dt: str) -> str:
    """datetime 문자열을 보기 좋게 포맷팅"""
    date_obj = datetime.fromisoformat(dt)
    return date_obj.strftime("%Y-%m-%d %H:%M")

def render_history():
    """히스토리 목록을 사이드바에 표시"""
    try:
        history_data = None#get_resume_histories()
        
        if not history_data:
            st.info("작성 히스토리가 없습니다.")
            return
        
        # 히스토리 목록 표시
        for item in history_data:
            with st.expander(
                f"📝 {item['organization']} - {item['position']}",
                expanded=False
            ):
                st.write(f"작성일시: {format_datetime(item['created_at'])}")
                st.write(f"문항 수: {len(item['questions'])}개")
                
                if st.button("상세 보기", key=f"view_{item['id']}"):
                    st.session_state.selected_history = item['id']
                
                if st.button("삭제", key=f"delete_{item['id']}", type="secondary"):
                    if delete_resume_history(item['id']):
                        st.success("삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("삭제 중 오류가 발생했습니다.")
    
    except Exception as e:
        st.error(f"히스토리 조회 중 오류가 발생했습니다: {str(e)}")

def render_history_detail():
    """히스토리 상세 내용 표시"""
    if "selected_history" not in st.session_state:
        st.info("히스토리를 선택해주세요.")
        return
    
    try:
        history_id = st.session_state.selected_history
        detail_data = get_resume_detail(history_id)
        
        if not detail_data:
            st.error("데이터를 불러올 수 없습니다.")
            return
        
        # 기본 정보 표시
        st.header(f"{detail_data['organization']} - {detail_data['position']}")
        st.subheader("기본 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"작성일시: {format_datetime(detail_data['created_at'])}")
        with col2:
            st.write(f"직무: {detail_data['position']}")
        
        # 지원자 프로필
        with st.expander("지원자 프로필", expanded=False):
            st.write(f"교육: {detail_data['user_profile']['education']}")
            st.write(f"경력: {detail_data['user_profile']['experience']}")
            st.write(f"기술: {detail_data['user_profile']['skills']}")
            if detail_data['user_profile'].get('certificates'):
                st.write(f"자격증: {detail_data['user_profile']['certificates']}")
            st.write(f"프로젝트: {detail_data['user_profile']['projects']}")
            if detail_data['user_profile'].get('achievements'):
                st.write(f"성과: {detail_data['user_profile']['achievements']}")
        
        # 문항별 결과 표시
        st.subheader("작성 결과")
        for question in detail_data['questions']:
            with st.expander(f"문항 {question['question_id']}", expanded=True):
                st.write("**문항**")
                st.write(question['content'])
                
                st.write("**초안**")
                st.write(detail_data['drafts'][str(question['question_id'])])
                
                if 'technical_feedbacks' in detail_data:
                    st.write("**기술 평가**")
                    st.write(detail_data['technical_feedbacks'][str(question['question_id'])])
                
                if 'culture_feedbacks' in detail_data:
                    st.write("**문화 평가**")
                    st.write(detail_data['culture_feedbacks'][str(question['question_id'])])
                
                st.write("**최종본**")
                st.write(detail_data['final_drafts'][str(question['question_id'])])
                
    except Exception as e:
        st.error(f"상세 정보 조회 중 오류가 발생했습니다: {str(e)}") 