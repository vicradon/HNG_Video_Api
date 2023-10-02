import uvicorn
import os
from typing import List
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware

import cloudinary.uploader
from fastapi import FastAPI
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import engine, get_db
from app.config import settings


models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

cloudinary.config(
    cloud_name=settings.cloud_name,
    api_key=settings.api_key,
    api_secret=settings.api_secret
)
app = FastAPI(middleware=middleware,)


@app.post("/api")
async def upload_video(file: UploadFile = File(...), email: str = Form(), db: Session = Depends(get_db),):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email)
        db.add(user)
        db.commit()
    try:
        data = cloudinary.uploader.upload(file.file, resource_type="video")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Cloudinary Upload Error: "+str(e))
    new_video = models.Video(
        **{"user_id": user.id, "video_url": data["url"], "public_id": data["public_id"], "created_at": data["created_at"]})
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video


@app.put("/api/{id}", response_model=schemas.Video)
def update_playback_time(id: int, time: schemas.VideoTimeUpdate, db: Session = Depends(get_db),):
    video_query = db.query(models.Video).filter(
        models.Video.id == id)
    video = video_query.first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"video with id -> {id} not found")
    video_query.update(time.model_dump(), synchronize_session=False)
    db.commit()
    return video_query.first()


@app.delete("/api/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(id: int, db: Session = Depends(get_db),):
    video_query = db.query(models.Video).filter(
        models.Video.id == id)
    video = video_query.first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"video with id -> {id} not found")
    try:
        result = cloudinary.uploader.destroy(
            video.public_id, resource_type="video")
        if result.get("result") == "ok":
            video_query.delete(synchronize_session=False)
            db.commit()
            return
        else:
            raise HTTPException(
                status_code=400, detail="Failed to delete video")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{email}/videos", response_model=List[schemas.Video])
def get_user_videos(email: str, db: Session = Depends(get_db),):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with email -> {email} not found")
    videos = db.query(models.Video).filter(
        models.Video.user_id == user.id).all()
    return videos


@app.get("/api/users/{email}/videos/latest", response_model=schemas.Video)
def get_latest_video(email: str, db: Session = Depends(get_db),):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with email -> {email} not found")
    video = db.query(models.Video).filter(models.Video.user_id == user.id).order_by(
        desc(models.Video.created_at)).first()
    return video


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", port=port, log_level="info", reload=True)