/**
 * GARELABO+ 自動カスタム制御スクリプト 完全版
 */
console.log("🚗 自動カスタムJS読み込み開始");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM読み込み完了");

    // 初回表示の実行
    if (window.autoCustomResult) {
        updateCarDisplay();
    }
    loadInitialCustom();
});

/**
 * 車両画像と名前を表示・更新するメイン関数
 */
function updateCarDisplay() {
    const img = document.getElementById("car-image");
    const nameLabel = document.getElementById("display-vehicle-name");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (!img) return;

    const config = window.autoCustomResult;
    const angles = ["front", "side", "rear"];
    let angleIndex = 0;

    const render = () => {
    // パスの組み立て
        const path = `/media/uploads/vehicles/${config.carFolder}/${config.color}/${angles[angleIndex]}.png`;
        
        // 【重要】これを追加してコンソール（F12）で確認してください
        console.log("🎬 ブラウザがアクセスしようとしているURL:", path);

        img.src = path;

        // 画像が読み込めなかった時のエラーログ
        img.onerror = () => {
            console.error("❌ 画像が見つかりません。パスを確認してください:", path);
            console.log("実際のフォルダが Rocky なら、config.carFolder が Rocky になっている必要があります。");
        };
    };

    render();

    // ボタンにイベントを登録
    prevBtn.onclick = () => {
        angleIndex = (angleIndex - 1 + angles.length) % angles.length;
        render();
    };
    nextBtn.onclick = () => {
        angleIndex = (angleIndex + 1) % angles.length;
        render();
    };
}

/**
 * 「自動カスタム」ボタンが押された時のAPI連携
 */
function loadCustomData() {
    const url = window.API_URLS.auto_custom;
    console.log("📡 APIリクエスト送信中...");

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("✅ API受信成功:", data);

            // 1. 画面上のデータ(windowオブジェクト)を更新
            window.autoCustomResult = {
                carFolder: data.carFolder,
                carName: data.carName,
                color: data.color
            };

            // 2. テキストリスト用のデータを更新
            window.initialSelected.vehicle.name = data.carName;
            window.initialSelected.color.name = data.color_name;

            // 3. 表示をリフレッシュ
            updateCarDisplay();
            loadInitialCustom();
        })
        .catch(error => {
            console.error("❌ APIエラー:", error);
            alert("自動カスタムデータの取得に失敗しました。URL設定を確認してください。");
        });
}

/**
 * 右側のパーツリストを表示
 */
function loadInitialCustom() {
    const container = document.getElementById("custom-content");
    const selectedData = window.initialSelected;
    if (!selectedData || !container) return;

    container.innerHTML = `
        <h3>選択中のカスタム</h3>
        <ul class="custom-list">
            ${selectedData.vehicle?.name ? `<li>車種：${selectedData.vehicle.name}</li>` : ""}
            ${selectedData.color?.name ? `<li>カラー：${selectedData.color.name}</li>` : ""}
            <li>ホイール：ノーマル</li>
            <li>バンパー：ノーマル</li>
        </ul>
    `;
}