# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from . import models
from .routers import auth, admin, schedules, applications, mypage, notices
import asyncio
from datetime import datetime, timedelta
import logging
import os

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="서울올림픽파크텔 인력 관리 시스템 API")

# 🔧 변경: CORS 설정 - 배포 환경에 맞게 조정
# Render 배포 시 자동으로 프론트엔드 도메인 허용
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # 🔧 변경: 환경변수로 제어
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔧 변경: API 라우터를 app에 직접 포함 (prefix 사용)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(mypage.router, prefix="/api/mypage", tags=["mypage"])
app.include_router(notices.router, prefix="/api/notices", tags=["notices"])

@app.get("/")
def read_root():
    return {"message": "서울올림픽파크텔 API", "status": "running", "version": "1.0"}

@app.get("/api")
def api_root():
    return {"message": "Parktel Schedule API", "status": "running"}

@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트 (Render 모니터링용)"""
    return {"status": "healthy"}

# 백그라운드: 45일 지난 스케줄 삭제
async def cleanup_old_schedules_periodic():
    while True:
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=45)
            old_schedules = db.query(models.Schedule).filter(models.Schedule.work_date < cutoff).all()
            if old_schedules:
                logging.info(f"Cleaning up {len(old_schedules)} old schedules (older than 45 days)")
                for s in old_schedules:
                    db.delete(s)  # CASCADE will delete related applications
                db.commit()
        except Exception as e:
            logging.error(f"Error during cleanup_old_schedules: {e}")
            db.rollback()
        finally:
            db.close()
        await asyncio.sleep(24 * 3600)

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    logging.info("Starting Parktel Schedule API...")
    
    # 🔧 추가: 초기 관리자 계정 생성
    try:
        from .init_db import init_database
        init_database()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
    
    # 백그라운드 작업 시작
    asyncio.create_task(cleanup_old_schedules_periodic())
