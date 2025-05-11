from fastapi import APIRouter, HTTPException, Depends, Response
from app.services.google_drive import GoogleDriveService
from app.models.document import DocumentMetadata, DocumentType
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

router = APIRouter(
    prefix="/drive",
    tags=["drive"]
)

drive_service = GoogleDriveService()

async def get_drive_service():
    """Google Driveサービスのインスタンスを取得します"""
    try:
        drive_service.authenticate()
        return drive_service
    except Exception as e:
        if 'token.pickle' in str(e):
            # トークンファイルが存在しない場合は認証を促す
            raise HTTPException(
                status_code=401,
                detail="Google Driveの認証が必要です。ブラウザで認証を完了してください。"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Google Driveの認証に失敗しました: {str(e)}"
        )

@router.get("/files", response_model=List[Dict[str, Any]])
async def list_files(
    page_size: int = 10,
    service: GoogleDriveService = Depends(get_drive_service)
):
    """Google Driveのファイル一覧を取得します"""
    try:
        return service.list_files(page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_files(
    query: str,
    page_size: int = 10,
    service: GoogleDriveService = Depends(get_drive_service)
):
    """Google Driveのファイルを検索します"""
    try:
        return service.search_files(query, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/metadata", response_model=DocumentMetadata)
async def get_file_metadata(
    file_id: str,
    service: GoogleDriveService = Depends(get_drive_service)
):
    """ファイルの詳細なメタデータを取得します"""
    try:
        return service.get_document_metadata(file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/type/{doc_type}", response_model=List[DocumentMetadata])
async def get_files_by_type(
    doc_type: DocumentType,
    page_size: int = 10,
    service: GoogleDriveService = Depends(get_drive_service)
):
    """指定された種類のドキュメントを取得します"""
    try:
        files = service.list_files(page_size)
        return [
            service.get_document_metadata(file['id'])
            for file in files
            if service.classify_document(file['name']) == doc_type
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 