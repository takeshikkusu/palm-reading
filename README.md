# Palm AI — 手相AI診断

手のひら画像をアップロードすると、Geminiが手相を読み、生命線・知能線・感情線などを解説するWebアプリです。

---

## 1. アーキテクチャ概要

### 全体構成

```
palm-reading/
├── backend/          # Flask + Clean Architecture
│   ├── domain/       # エンティティ・ビジネスルール
│   ├── usecases/     # アプリケーションのユースケース
│   ├── interfaces/   # ポート・コントローラ（Flask, LLM抽象）
│   ├── infrastructure/ # 外部サービス（Gemini実装）
│   ├── config.py
│   └── app.py        # エントリ・DI組み立て
├── frontend/         # React + Vite
│   └── src/
│       ├── components/
│       ├── services/
│       ├── App.jsx
│       └── main.jsx
├── .env.example
└── README.md
```

### Backend: Clean Architecture

| 層 | 役割 | 依存方向 |
|----|------|----------|
| **Domain** | `PalmReadingResult` エンティティ。フレームワーク非依存。 | なし |
| **Use cases** | 診断のオーケストレーション。LLMはPort経由で注入。 | Domain, Interfaces(Port) |
| **Interfaces** | `LLMPort`（抽象）、Flaskルート。HTTP入出力のみ。 | Use cases |
| **Infrastructure** | `GeminiLLMAdapter`（LLMPort実装）。APIキー・HTTPはここだけ。 | Interfaces(Port) |
| **app.py** | 依存性の組み立て・Flask起動。 | 全層 |

- **Controllerから直接Geminiを呼ばない**: 必ず `DiagnosePalmUseCase` 経由で `LLMPort` を呼ぶ。
- **LLMの差し替え**: 別のLLM（OpenAI, Claude等）を使う場合は、`LLMPort` を実装したアダプタを Infrastructure に追加し、`app.py` で差し替えるだけ。

### Frontend

- **React + Vite**: SPA、開発時は `/api` をバックエンドにプロキシ。
- **状態管理**: `useState` ベース（将来 Redux/Zustand に拡張しやすい構成）。
- **API**: `services/api.js` で集約。本番では `VITE_API_BASE_URL` でベースURLを指定可能。

### セキュリティ

- APIキーは **Backend のみ**（.env / 環境変数）。フロントに秘密情報を持たせない。
- CORS は `CORS_ORIGINS` で制御。本番ではフロントのオリジンを明示することを推奨。
- 本番は gunicorn で起動。

---

## 2. Backend コード一式

主要ファイルは以下のとおりです。

- `backend/domain/entities.py` — 診断結果エンティティ
- `backend/interfaces/llm_port.py` — LLM抽象
- `backend/interfaces/flask_controller.py` — `/api/health`, `/api/diagnose`
- `backend/usecases/diagnose_palm.py` — 診断ユースケース
- `backend/infrastructure/gemini_llm.py` — Gemini実装
- `backend/config.py` — 設定
- `backend/app.py` — アプリ・DI
- `backend/requirements.txt` — 依存関係

---

## 3. Frontend コード一式

- `frontend/package.json` — 依存関係・スクリプト
- `frontend/vite.config.js` — Vite・プロキシ
- `frontend/index.html` — エントリHTML
- `frontend/src/main.jsx` — Reactエントリ
- `frontend/src/App.jsx` — ルートコンポーネント
- `frontend/src/services/api.js` — 診断API・ヘルスチェック
- `frontend/src/components/DiagnosisForm.jsx` — 画像選択・送信・ローディング
- `frontend/src/components/ResultCard.jsx` — 診断結果表示
- 各種 `*.css` — ミニマル・占いらしいスタイル

---

## 4. requirements.txt

`backend/requirements.txt` を参照してください。

```
flask>=3.0.0
flask-cors>=4.0.0
gunicorn>=21.0.0
google-generativeai>=0.8.0
```

---

## 5. package.json

`frontend/package.json` を参照してください。  
React 18 / Vite 6 / スクリプト: `dev`, `build`, `preview`。

---

## 6. .env.example

リポジトリには `.env.example` をコミットし、本番用の `.env` はコミットしないでください。  
必要な変数は README の「8. ローカル起動手順」を参照。

---

## 7. README

このファイルです。

---

## 8. ローカル起動手順

### 前提

- Python 3.11+
- Node.js 18+

### 1) リポジトリのルートで

```bash
cd palm-reading
```

### 2) 環境変数

```bash
cp .env.example .env
# .env を編集し、GEMINI_API_KEY を設定
```

### 3) Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cd ..
```

プロジェクトルート（`palm-reading`）でFlaskを起動する場合:

```bash
# プロジェクトルートで
# Windows (PowerShell):
$env:PYTHONPATH = "."
# Windows (cmd):
# set PYTHONPATH=.
# macOS/Linux:
# export PYTHONPATH=.

flask --app backend.app:app run --port 5000
```

または:

```bash
cd backend
set PYTHONPATH=..   # Windows（backend から見て親がルート）
# export PYTHONPATH=..  # macOS/Linux
flask --app app:app run --port 5000
```

※ `backend.app:app` は「ルートから見て backend パッケージの app モジュールの app」なので、**プロジェクトルートで `PYTHONPATH=.` を付けて実行**するか、`backend` で `PYTHONPATH=..` で `app:app` で実行してください。

### 4) Frontend

別ターミナルで:

```bash
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:5173` を開き、手のひら画像を選択して「手相を診断する」を押すと、APIが呼ばれ結果が表示されます。

---

## 9. Render デプロイ手順

### Backend（Web Service）

1. Render ダッシュボードで **New → Web Service**。
2. リポジトリを接続（GitHub等）。
3. 設定例:
   - **Root Directory**: 空のまま（リポジトリルート）
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT "backend.app:app"`
   - 実行時カレントはリポジトリルートのため、`backend.app:app` で正しく読み込めます。
4. **Environment**: `GEMINI_API_KEY` を追加。必要なら `CORS_ORIGINS` にフロントのURL（例: `https://palm-ai-frontend.onrender.com`）を設定。
5. デプロイ後、**Backend URL**（例: `https://palm-ai-backend.onrender.com`）を控える。

### Frontend（Static Site または Web Service）

1. **New → Static Site**（または Web Service で Node を使う）。
2. リポジトリを接続。
3. 設定例:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Environment**:  
   - `VITE_API_BASE_URL=https://palm-ai-backend.onrender.com`  
   （上で控えたBackend URL。末尾スラッシュなし）
5. デプロイ後、表示されるフロントURLを `CORS_ORIGINS` に追加（必要ならBackendの環境変数を再デプロイ）。

---

## 10. 将来の拡張方法

- **LLMの差し替え**: `LLMPort` を実装した別アダプタ（例: `OpenAILLMAdapter`）を `infrastructure` に追加し、`app.py` で環境変数に応じて切り替える。
- **認証**: Flask のブループリント前にミドルウェアでトークン検証を追加。フロントはログイン後にトークンを付与。
- **履歴保存**: Use case に「診断結果を保存」を追加し、Infrastructure に DB アダプタ（SQLAlchemy等）を追加。Controller は現状のまま「結果を返す」だけに保つ。
- **状態管理**: フロントで複数画面・履歴一覧が出てきたら、Context API や Zustand/Redux を導入し、`api.js` はそのまま利用可能。
- **テスト**: Backend は `LLMPort` のモックで `DiagnosePalmUseCase` のユニットテスト、Flask は `app.test_client()` で結合テスト。Frontend は React Testing Library でコンポーネントテスト。

---

## 品質方針

- 実務レベルの責務分離（Controller は HTTP のみ、ビジネスロジックは Use case / Domain）。
- 拡張時も既存層を壊さない設計。
- APIキーはバックエンドのみ、CORS 適切設定で技術的負債を抑える。
