from langchain_community.vectorstores import FAISS
from typing import Any, Dict, Optional, List
from backend.rag.search_service import get_search_content, improve_search_query
from backend.utils.config import get_embeddings

def get_resume_vector_store(
    content: str,
    role: str,
    language: str = "ko"
) -> Optional[FAISS]:
    """자소서 내용에 대한 벡터 스토어 생성"""
    
    # 검증이 필요한 키워드 추출 및 검색어 개선
    improved_queries = improve_search_query(content, role)
    
    # 개선된 검색어로 검색 콘텐츠 가져오기
    documents = get_search_content(improved_queries, language)
    
    if not documents:
        return None
    
    try:
        return FAISS.from_documents(documents, get_embeddings())
    except Exception as e:
        print(f"Vector DB 생성 중 오류 발생: {str(e)}")
        return None

def search_info(
    content: str,
    role: str,
    query: str,
    k: int = 5
) -> List[Dict[str, Any]]:
    """자소서 내용 검증을 위한 정보 검색"""

    print("===== search_info ",content, role, query, k)

    # 벡터 스토어 생성
    vector_store = get_resume_vector_store(content, role)
    if not vector_store:
        return []
        
    try:
        # 유사도 검색 수행
        results = vector_store.similarity_search(query, k=k)
        print("===== search_info results ",results)
        # 검색 결과 포맷팅
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "topic": doc.metadata.get("topic", ""),
                "query": doc.metadata.get("query", "")
            })
            
        return formatted_results
        
    except Exception as e:
        print(f"검색 중 오류 발생: {str(e)}")
        return [] 