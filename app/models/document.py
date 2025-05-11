from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "invoice"  # 請求書
    RECEIPT = "receipt"  # 領収書
    CONTRACT = "contract"  # 契約書
    TAX_RETURN = "tax_return"  # 税務申告書
    OTHER = "other"  # その他

class DocumentMetadata(BaseModel):
    id: str  # Google DriveのファイルID
    name: str  # ファイル名
    type: DocumentType
    client_name: Optional[str] = None  # 取引先名
    amount: Optional[float] = None  # 金額
    date: Optional[datetime] = None  # 日付
    description: Optional[str] = None  # 説明
    tags: list[str] = []  # タグ
    created_at: datetime
    updated_at: datetime

class Document(BaseModel):
    metadata: DocumentMetadata
    content: str  # テキスト内容
    created_at: datetime
    updated_at: datetime