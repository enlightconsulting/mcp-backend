# MCP Backend

税理士事務所向け業務効率化システムのバックエンド

## セットアップ

1. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
.\venv\Scripts\activate  # Windowsの場合
```

2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

3. 環境変数の設定
`.env`ファイルを作成し、必要な環境変数を設定してください。

4. サーバーの起動
```bash
uvicorn app.main:app --reload
```

## API ドキュメント

サーバー起動後、以下のURLでAPIドキュメントにアクセスできます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 