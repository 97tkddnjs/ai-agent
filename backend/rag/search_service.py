from typing import List, Literal
from langchain.schema import Document, HumanMessage, SystemMessage
from duckduckgo_search import DDGS
from backend.utils.config import get_llm
from backend.workflow.state import AgentType

def improve_search_query(
    content: str,
    role: AgentType,
) -> List[str]:
    
    template = """
    다음 자기소개서 내용을 {perspective}의 관점에서 분석하기 위한 
    핵심 키워드나 주제를 3개 추출해주세요:
    
    내용:
    {content}
    
    키워드/주제를 쉼표로 구분하여 나열해주세요.
    """

    perspective_map = {
        AgentType.RESUME_WRITER: "자기소개서 작성자",
        AgentType.CONTENT_ANALYZER: "자기소개서 내용 분석가",
        AgentType.TECHNICAL_EVALUATOR: "기술 평가자",
        AgentType.CULTURE_EVALUATOR: "문화 적합성 평가자",
        AgentType.FINAL_REVIEWER: "최종 검토자"
    }

    prompt = template.format(
        content=content, 
        perspective=perspective_map[role]
    )

    messages = [
        SystemMessage(
            content="당신은 자기소개서 검증 전문가입니다. 주어진 내용에서 검증이 필요한 핵심 키워드를 추출해주세요."
        ),
        HumanMessage(content=prompt),
    ]

    response = get_llm().invoke(messages)
    
    suggested_queries = [q.strip() for q in response.content.split(",")]

    return suggested_queries[:3]

def get_search_content(
    improved_queries: List[str],
    language: str = "ko",
    max_results: int = 5,
) -> List[Document]:
    try:
        documents = []
        ddgs = DDGS()
        
        for query in improved_queries:
            try:
                results = ddgs.text(
                    query,
                    region=language,
                    safesearch="moderate",
                    timelimit="y",
                    max_results=max_results,
                )

                if not results:
                    continue
                
                for result in results:
                    
                    title = result.get("title", "")
                    body = result.get("body", "")
                    url = result.get("href", "")

                    if body:

                        documents.append(
                            Document(
                                page_content=body,
                                metadata={
                                    "source": url,
                                    "section": "content",
                                    "topic": title,
                                    "query": query,
                                },
                            )
                        )

            except Exception as e:
                print(f"검색 중 오류 발생: {str(e)}")
                continue
        
        return documents

    except Exception as e:
        print(f"검색 서비스 오류 발생: {str(e)}")
        return [] 