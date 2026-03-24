/**
 * GARELABO+ 自動カスタム制御スクリプト
 */

// 角度の定義
const ANGLES = ["front", "side_right", "rear", "side_left"];
let angleIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    
    // 1. 初回表示
    renderVehicle();

    // 2. 回転ボタンのイベント登録
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

    // 3. 初期リスト表示
    loadInitialCustom();
});

/**
 * 画像のみを再描画する関数
 */
function renderVehicle() {
    const img = document.getElementById("car-image");
    if (!img || !window.autoCustomResult) return;

    const config = window.autoCustomResult;
    
    // パス生成: エアロパーツを含めた構成
    const path = `/media/uploads/vehicles/${config.carFolder}/${config.color}/${config.wheel}/${config.bumper}/${config.aero}/${ANGLES[angleIndex]}.png`;
    
    img.src = path;

    img.onerror = () => {
        // エラーログ削除
    };
}

/**
 * APIからランダムデータを取得
 */
function loadCustomData() {
    const carName = window.autoCustomResult.carName;
    const url = `${window.API_URLS.auto_custom}?carName=${encodeURIComponent(carName)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {

            // 車種フォルダ名とカラーを両方更新！
            window.autoCustomResult.carFolder = data.carFolder; 
            window.autoCustomResult.color = data.color;
            window.autoCustomResult.wheel = data.wheel;
            window.autoCustomResult.bumper = data.bumper;
            window.autoCustomResult.aero = data.aero;
            window.autoCustomResult.carName = data.carName;
            

            // リストのテキストも更新
            window.initialSelected.vehicle.name = data.carName;
            window.initialSelected.color.name = data.color_name;
            window.initialSelected.wheel.name = data.wheel_name;
            window.initialSelected.bumper.name = data.bumper_name;
            window.initialSelected.aero = window.initialSelected.aero || {};
            window.initialSelected.aero.name = data.aero_name;

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
        .catch(() => {});
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
            <li>エアロ：${selectedData.aero.name}</li>
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