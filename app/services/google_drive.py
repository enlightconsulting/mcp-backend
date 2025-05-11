from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import socket
from typing import List, Dict, Any
from app.models.document import DocumentType, DocumentMetadata
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def find_free_port():
    """空いているポートを見つけます"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

class GoogleDriveService:
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.service = None

    def authenticate(self) -> None:
        """Google Drive APIの認証を行います"""
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                # 認証URLを表示して、ユーザーに手動で認証を促す
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f'以下のURLにアクセスして認証を完了してください: {auth_url}')
                code = input('認証コードを入力してください: ')
                creds = flow.fetch_token(code=code)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size: int = 10) -> List[Dict[str, Any]]:
        """ファイルの一覧を取得します"""
        if not self.service:
            self.authenticate()

        try:
            results = self.service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            # 認証エラーの場合は再認証を試みる
            if 'invalid_grant' in str(e):
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                self.authenticate()
                return self.list_files(page_size)
            raise e

    def search_files(self, query: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """ファイルを検索します"""
        if not self.service:
            self.authenticate()

        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, createdTime)"
        ).execute()
        
        return results.get('files', [])

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """ファイルのメタデータを取得します"""
        if not self.service:
            self.authenticate()

        return self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, createdTime, modifiedTime, description"
        ).execute()

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
        metadata = self.get_file_metadata(file_id)
        
        return DocumentMetadata(
            id=metadata['id'],
            name=metadata['name'],
            type=self.classify_document(metadata['name']),
            created_at=datetime.fromisoformat(metadata['createdTime'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(metadata['modifiedTime'].replace('Z', '+00:00'))
        ) 