※　ガレラボ＋


githubのURL: https://github.com/hamumaro/garelabo_project


１，GitHubからリポジトリをクローン
git clone https://github.com/hamumaro/garelabo_project.git



２，クローン済みのプロジェクトにディレクトリに移動
cd garelabo_project



３，ローカルのデータをEC2へアップロード
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo docker compose up -d --build


動作確認URL： http://


----- 工夫した点 -----

・CSSや画像が読み込まれるよう、collectstatic コマンドを
起動時に実行する仕組みを作りました。

・環境変数（.env）を用いてデータベースの接続設定などを
切り出すことで、本番環境と開発環境の管理をしやすくしました。

・ローカルのSQLiteデータと画像ファイルをコンテナに
マウント（配置）させることで、開発したデータを
そのまま本番環境で表示できるようにしました。

----- 苦労した点 -----

・デプロイ直後にトップページでCSSが上手く読み込めず、
デザインが適用されていない状態で開かれたため、
原因究明と静的ファイルの配信設定
（WhiteNoiseの導入など）に苦労しました。

・Dockerコンテナ内からSQLiteのファイルを正しく読み込ませるため
のパス指定（sqlite:////app/db.sqlite3 の設定など）や、
ホストとコンテナ間での権限・パスのズレによるエラー解決に
非常に苦労しました。

---------------------