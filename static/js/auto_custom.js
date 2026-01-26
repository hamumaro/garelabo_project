/**
 * GARELABO+ 自動カスタム制御スクリプト
 */
console.log("🚗 自動カスタムJS読み込み開始");

// 角度の定義を共通化
// const ANGLES = ["front", "front_right", "side_right", "rear_left", "rear", "rear_right","side_left", "front_left"];
const  ANGLES = ["side","rear","front"]
let angleIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM読み込み完了");
    
    // 1. 初回表示
    renderVehicle();

    // 2. 回転ボタンのイベント登録（ここで行うことで重複を防ぐ）
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (prevBtn && nextBtn) {
        prevBtn.onclick = () => {
            angleIndex = (angleIndex - 1 + ANGLES.length) % ANGLES.length;
            renderVehicle();
        };
        nextBtn.onclick = () => {
            angleIndex = (angleIndex + 1) % ANGLES.length;
            renderVehicle();
        };
    }

    loadInitialCustom();
});

/**
 * 画像のみを再描画する関数
 */
function renderVehicle() {
    const img = document.getElementById("car-image");
    if (!img || !window.autoCustomResult) return;

    const config = window.autoCustomResult;
    // const path = `/media/uploads/vehicles/${config.carFolder}/${config.color}/${ANGLES[angleIndex]}.png`;
    const path = `/media/uploads/vehicles/${config.carFolder}/${config.color}/${config.wheel}/${ANGLES[angleIndex]}.png`;
    console.log("🎬 表示更新:", path);
    img.src = path;

    img.onerror = () => {
        console.error("❌ 画像が見つかりません:", path);
    };
}

/**
 * APIからランダムデータを取得
 */
function loadCustomData() {
    const carName = window.autoCustomResult.carName;
    const url = `${window.API_URLS.auto_custom}?carName=${encodeURIComponent(carName)}`;

    console.log("📡 APIリクエスト送信中...");

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("✅ API受信:", data);

            // 車種フォルダ名とカラーを両方更新！
            window.autoCustomResult.carFolder = data.carFolder; 
            window.autoCustomResult.color = data.color;
            window.autoCustomResult.wheel = data.wheel;
            window.autoCustomResult.carName = data.carName;

            // リストのテキストも更新
            window.initialSelected.vehicle.name = data.carName;
            window.initialSelected.color.name = data.color_name;
            window.initialSelected.wheel.name = data.wheel_name;
            window.initialSelected.bumper.name = data.bumper_name;

            // 隠しフィールドの値を更新（保存ボタンを押したときに反映されるようにする）
            const favInput = document.getElementById('is-favorite');
            if (favInput) {
                favInput.value = data.is_favorite ? 'true' : 'false';
            }
            
            // お気に入りボタンの表示も更新
            const favToggle = document.getElementById('favorite-toggle');
            if (favToggle) {
                favToggle.innerText = data.is_favorite ? '✔ お気に入り' : 'お気に入り';
            }
            
            // 描画実行
            renderVehicle(); 
            loadInitialCustom();
        })
        .catch(error => console.error("❌ APIエラー:", error));
}

/**
 * パーツリスト表示
 */
function loadInitialCustom() {
    const container = document.getElementById("custom-content");
    const selectedData = window.initialSelected;
    if (!selectedData || !container) return;

    container.innerHTML = `
        <h3>選択中のカスタム</h3>
        <ul class="custom-list">
            <li>車種：${selectedData.vehicle.name}</li>
            <li>カラー：${selectedData.color.name}</li>
            <li>ホイール：${selectedData.wheel.name}</li>
            <li>バンパー：${selectedData.bumper.name}</li>
        </ul>
    `;
}
const favToggle = document.getElementById('favorite-toggle');
if (favToggle) {
    favToggle.addEventListener('click', function(e) {
        e.preventDefault();

        const isNowFav = this.innerText.includes('✔');
        const nextState = !isNowFav;

        fetch('/update_session_favorite/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_favorite: nextState })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                // 見た目の更新
                favToggle.innerText = data.is_favorite ? '✔ お気に入り' : 'お気に入り';
                
                // ★ここを追加：保存フォーム用の隠しフィールドも更新する
                const hiddenInput = document.getElementById('is-favorite');
                if (hiddenInput) {
                    hiddenInput.value = data.is_favorite ? 'true' : 'false';
                }
            }
        });
    });
}