# backend/app/renew-main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from . import models
from .routers import auth, admin, schedules, applications, mypage, notices
import asyncio
from datetime import datetime, timedelta
import logging

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="서울올림픽파크텔 인력 관리 시스템 API (RENEWED)")

# CORS 설정
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 설정
api_router = FastAPI(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(schedules.router)
api_router.include_router(applications.router)
api_router.include_router(mypage.router)
api_router.include_router(notices.router)

app.mount("/api", api_router)

@app.get("/")
def read_root():
    return {"message": "서울올림픽파크텔 API - RENEWED VERSION", "status": "running"}

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
    asyncio.create_task(cleanup_old_schedules_periodic())
