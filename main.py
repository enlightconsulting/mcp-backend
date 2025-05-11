print("✅ FastAPI アプリのロード開始")

from fastapi import FastAPI

print("✅ FastAPI インポート完了")

app = FastAPI(
    title="TEST",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

print("✅ FastAPI インスタンス作成完了")

@app.get("/")
def root():
    return {"message": "ok"}

print("✅ ルートエンドポイント定義完了")