import streamlit as st
from typing import Dict, Any
from ..utils.api import send_resume_request

def init_session_state():
    if "current_step" not in st.session_state:
        st.session_state.current_step = "input"
    if "responses" not in st.session_state:
        st.session_state.responses = []

def render_new_resume_form():
    """새 자기소개서 작성 폼을 렌더링합니다."""
    with st.form("resume_form"):
        st.title("자소서 작성 도우미")
        
        # 기본 정보 입력
        with st.expander("기본 정보", expanded=True):
            st.info("* 표시된 항목은 필수 입력사항입니다")
            organization = st.text_input(
                "회사/조직명 *",
                placeholder="예: 네이버",
                help="필수 입력 항목입니다"
            )
            position = st.text_input(
                "직무/포지션 *",
                placeholder="예: 백엔드 개발자",
                help="필수 입력 항목입니다"
            )
            requirements = st.text_area(
                "주요 요구사항 *",
                placeholder="예: Spring Boot 기반 백엔드 개발 경험..."
            )
            description = st.text_area(
                "직무 설명",
                placeholder="예: MSA 환경에서 결제 시스템 개발..."
            )
            company_values = st.text_area(
                "회사 가치/문화",
                placeholder="예: 도전과 혁신을 추구하며..."
            )

        # 사용자 프로필 입력
        with st.expander("지원자 프로필", expanded=True):
            st.info("* 표시된 항목은 필수 입력사항입니다")
            user_profile = {
                "education": st.text_area(
                    "교육사항 *",
                    placeholder="예: 컴퓨터공학과 학사 (2019-2023)"
                ),
                "experience": st.text_area(
                    "경력사항 *",
                    placeholder="예: ABC 회사 인턴 (2022.07-2022.12)\n신입의 경우 '신입'으로 작성"
                ),
                "skills": st.text_area(
                    "보유기술 *",
                    placeholder="예: Python, Java, Spring Boot, React..."
                ),
                "certificates": st.text_area(
                    "자격증",
                    placeholder="예: 정보처리기사, SQLD..."
                ),
                "projects": st.text_area(
                    "주요 프로젝트 *",
                    placeholder="예: 쇼핑몰 백엔드 개발 (2022.09-2022.12)\n- Spring Boot 기반 REST API 개발\n- JPA를 활용한 데이터 모델링"
                ),
                "achievements": st.text_area(
                    "주요 성과",
                    placeholder="예: 서비스 응답속도 30% 개선, 교내 해커톤 대상..."
                )
            }
            
        # 자기소개서 문항 입력
        with st.expander("자기소개서 문항", expanded=True):
            st.info("최소 1개 이상의 문항을 입력해주세요 *")
            questions = []
            for i in range(1):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    question = st.text_area(
                        f"문항 {i+1} *" if i == 0 else f"문항 {i+1}",
                        placeholder="예: 지원동기를 작성해주세요",
                        key=f"question_{i}"
                    )
                
               
                with col2:
                    max_length = st.number_input(
                        "최대 글자수 *",
                        min_value=100,
                        max_value=2000,
                        value=500,
                        key=f"max_length_{i}"
                    )
                    min_length = st.number_input(
                        "최소 글자수 *",
                        min_value=0,
                        max_value=1000,
                        value=200,
                        key=f"min_length_{i}"
                    )
                
                questions.append({
                    "question_id": i+1,
                    "content": question,
                    "max_length": max_length,
                    "min_length": min_length,
                    "category": st.selectbox(
                        "카테고리 *",
                        ["지원동기", "직무역량", "성장과정", "기타"],
                        key=f"category_{i}"
                    )
                })
        
        # 제출 버튼
        submitted = st.form_submit_button("자기소개서 작성 시작", type="primary")
        
        if submitted:
            # 필수 항목 검증
            required_fields = {
                "회사/조직명": organization,
                "직무/포지션": position,
                "주요 요구사항": requirements,
                "교육사항": user_profile["education"],
                "경력사항": user_profile["experience"],
                "보유기술": user_profile["skills"],
                "주요 프로젝트": user_profile["projects"]
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if not questions:
                st.error("최소 1개 이상의 자기소개서 문항을 입력해주세요.")
                return None
                
            if missing_fields:
                st.error(f"다음 필수 항목을 입력해주세요: {', '.join(missing_fields)}")
                return None
                
            # 유효성 검사를 통과하면 데이터 반환
            return {
                "organization": organization,
                "position": position,
                "requirements": requirements,
                "description": description,
                "company_values": company_values,
                "user_profile": user_profile,
                "questions": questions,
                "submit_clicked": True
            }
    
    return {"submit_clicked": False}

def render_sidebar():
    """현재 탭에 따라 적절한 사이드바를 렌더링합니다."""
    current_tab = st.session_state.get("current_tab", "new")
    
    if current_tab == "new":
        return render_new_resume_form()
    return None