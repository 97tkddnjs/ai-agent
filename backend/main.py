import uvicorn
from fastapi import FastAPI
from backend.routers.resume import router as resume_router


# 데이터베이스 초기화를 위한 임포트 추가
# from db.database import Base, engine

# 데이터베이스 초기화
# Base.metadata.create_all(bind=engine)

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Debate Arena API",
    description="AI Debate Arena 서비스를 위한 API",
    version="0.1.0",
)

# /resume prefix 추가
app.include_router(resume_router, prefix="/resume")


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)