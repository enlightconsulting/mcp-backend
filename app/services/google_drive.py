from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Optional
import os
import json
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from app.models.document import DocumentType, DocumentMetadata

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'

class FileType(str, Enum):
    FOLDER = "folder"
    FILE = "file"

class FileInfo(BaseModel):
    id: str
    name: str
    type: FileType
    mime_type: Optional[str] = None
    size: Optional[int] = None
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None
    web_view_link: Optional[str] = None

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """サービスアカウントを使用して認証"""
        try:
            # 環境変数から認証情報を取得
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if service_account_json:
                # 環境変数から認証
                service_account_info = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=SCOPES
                )
            elif os.path.exists(SERVICE_ACCOUNT_FILE):
                # ファイルから認証
                credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE,
                    scopes=SCOPES
                )
            else:
                raise Exception("認証情報が見つかりません。環境変数GOOGLE_SERVICE_ACCOUNT_JSONまたはservice_account.jsonファイルが必要です。")

            self.service = build("drive", "v3", credentials=credentials)
        except Exception as e:
            raise Exception(f"Google Driveの認証に失敗しました: {str(e)}")

    def list_files(self, folder_id: Optional[str] = None, page_size: int = 100) -> List[FileInfo]:
        """指定されたフォルダ内のファイル一覧を取得"""
        try:
            if not self.service:
                self.authenticate()

            query = f"'{folder_id}' in parents" if folder_id else None
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)"
            ).execute()

            files = []
            for item in results.get("files", []):
                file_type = FileType.FOLDER if item.get("mimeType") == "application/vnd.google-apps.folder" else FileType.FILE
                files.append(FileInfo(
                    id=item["id"],
                    name=item["name"],
                    type=file_type,
                    mime_type=item.get("mimeType"),
                    size=int(item.get("size", 0)) if item.get("size") else None,
                    created_time=datetime.fromisoformat(item.get("createdTime").replace("Z", "+00:00")) if item.get("createdTime") else None,
                    modified_time=datetime.fromisoformat(item.get("modifiedTime").replace("Z", "+00:00")) if item.get("modifiedTime") else None,
                    web_view_link=item.get("webViewLink")
                ))
            return files
        except Exception as e:
            raise Exception(f"ファイル一覧の取得に失敗しました: {str(e)}")

    def get_file(self, file_id: str) -> FileInfo:
        """指定されたIDのファイル情報を取得"""
        try:
            if not self.service:
                self.authenticate()

            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink"
            ).execute()

            file_type = FileType.FOLDER if file.get("mimeType") == "application/vnd.google-apps.folder" else FileType.FILE
            return FileInfo(
                id=file["id"],
                name=file["name"],
                type=file_type,
                mime_type=file.get("mimeType"),
                size=int(file.get("size", 0)) if file.get("size") else None,
                created_time=datetime.fromisoformat(file.get("createdTime").replace("Z", "+00:00")) if file.get("createdTime") else None,
                modified_time=datetime.fromisoformat(file.get("modifiedTime").replace("Z", "+00:00")) if file.get("modifiedTime") else None,
                web_view_link=file.get("webViewLink")
            )
        except Exception as e:
            raise Exception(f"ファイル情報の取得に失敗しました: {str(e)}")

    def classify_document(self, file_name: str) -> DocumentType:
        """ファイル名からドキュメントの種類を分類します"""
        file_name_lower = file_name.lower()
        
        if any(keyword in file_name_lower for keyword in ['請求書', 'invoice']):
            return DocumentType.INVOICE
        elif any(keyword in file_name_lower for keyword in ['領収書', 'receipt']):
            return DocumentType.RECEIPT
        elif any(keyword in file_name_lower for keyword in ['契約書', 'contract']):
            return DocumentType.CONTRACT
        elif any(keyword in file_name_lower for keyword in ['申告書', 'tax']):
            return DocumentType.TAX_RETURN
        else:
            return DocumentType.OTHER

    def get_document_metadata(self, file_id: str) -> DocumentMetadata:
        """ファイルの詳細なメタデータを取得します"""
        file_info = self.get_file(file_id)
        
        return DocumentMetadata(
            id=file_info.id,
            name=file_info.name,
            type=self.classify_document(file_info.name),
            created_at=file_info.created_time,
            updated_at=file_info.modified_time
        ) 