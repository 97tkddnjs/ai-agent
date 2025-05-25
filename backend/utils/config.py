import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# .env 파일에서 환경 변수 로드
load_dotenv()


class Settings(BaseSettings):
    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = 'gpt-4-turbo',  # 모델명
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Langfuse 설정
    # LANGFUSE_PUBLIC_KEY: str
    # LANGFUSE_SECRET_KEY: str
    # LANGFUSE_HOST: str

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Debate Arena API"

    # CORS 설정
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # SQLite 데이터베이스 설정
    DB_PATH: str = "history.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///./{DB_PATH}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def get_llm(self):
        """OpenAI LLM 인스턴스를 반환합니다."""
        return ChatOpenAI(
            api_key=self.OPENAI_API_KEY,
            model=self.OPENAI_MODEL_NAME,
            temperature=0.7,
            streaming=True,  # 스트리밍 활성화
        )

    def get_embeddings(self):
        """OpenAI Embeddings 인스턴스를 반환합니다."""
        return OpenAIEmbeddings(
            model=self.OPENAI_EMBEDDING_MODEL,
            api_key=self.OPENAI_API_KEY,
        )
    

# 설정 인스턴스 생성
settings = Settings()


# 편의를 위한 함수들, 하위 호환성을 위해 유지
def get_llm():
    """LLM 인스턴스를 생성하고 반환합니다."""
    print("============= MODEL NAME",settings.OPENAI_MODEL_NAME)
    try:
        llm = ChatOpenAI(
            model_name="gpt-4-turbo",  # "gpt-3.5-turbo"
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
            streaming=True
        )
        return llm
    except Exception as e:
        print(f"LLM 초기화 중 에러 발생: {str(e)}")
        raise


def get_embeddings():
    """임베딩 모델 인스턴스를 생성하고 반환합니다."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY
    )
