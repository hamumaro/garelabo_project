ガレラボ＋

# 概要
ガレラボ＋は、実際の見た目を確認しながら車をカスタムできるWebアプリです。
ユーザーと企業のイメージのズレを減らし、満足度の高いカスタムを実現することを目的としています。

# 使用技術
言語
- Python 3.12.10
- Javascript (ES6)
- HTML5
- CSS3

フレームワーク
- Django 5.2.8

OSはWindowsを前提

# 主な機能
- ユーザー登録 
- ログイン/ログアウト機能
- 車両選択
- ボディカラー変更
- ホイール変更
- バンパー変更
- エアロパーツ変更
- 車体の回転（4枚画像による回転表示）
- 自動カスタム機能
- お気に入り登録
- カスタム内容保存
- 保存データの再編集/削除

# セットアップ方法
Githabのリポジトリのクローン方法
コマンドを入力するツールはコマンドプロンプトを使用

クローンしたい場所に移動

一つ上の階層に移動
cd フォルダー名

一つ下の階層に移動
cd ..\

クローンしたい場所に移動できたらクローンコマンドを入力
git clone　https://github.com/hamumaro/garelabo_project.git

クローンが作成できたらプロジェクトに入る
cd garelabo_project

仮想環境作成
python -m venv venv

作成が終了したら

有効化
venv\Scripts\activate

パッケージ一括インストール
pip install -r requirements.txt

# 起動方法
サーバー起動
python manage.py runserver
