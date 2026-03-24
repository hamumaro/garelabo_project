FROM python:3.10-slim

### 環境変数の設定
# Pythonが.pycファイルを書き込まないようにする
ENV PYTHONDONTWRITEBYTECODE 1

# 標準出力・標準エラー出力をバッファリングしない
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリの設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# 依存パッケージのインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


# プロジェクトのソースコードをコピー
COPY . /app/


# デフォルトのコマンド
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]