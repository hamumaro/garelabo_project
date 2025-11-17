// --- カスタム内容の要素 ---
const customContent = document.getElementById("custom-content");

// --- ページ読み込み時にAIカスタム自動生成 ---
document.addEventListener("DOMContentLoaded", () => {
    loadCustomData();
});

// --- AIによるカスタム内容取得（最終形を想定した構造）---
async function loadCustomData() {

    customContent.innerHTML = "AIがカスタム内容を生成しています...";

    try {
        // ▼ 後で本番APIに変更する ▼
        // const response = await fetch("/api/auto_custom");
        // const data = await response.json();

        // ------ 仮AI結果 ------
        const data = {
            bodyColor: "ステルスグレー",
            wheel: "RAYS鍛造 20インチ（ブラック）",
            light: "LEDプロジェクター＋NISMO仕様",
            bumper: "NISMO専用エアロ（フロント＆リア）",
            aero: "カーボンウィング＋サイドスカート"
        };
        // ---------------------

        customContent.innerHTML = formatCustomHTML(data);

    } catch (err) {
        console.error("AI読み込み失敗:", err);
        window.location.href = "main_error.html?type=switchFail";
    }
}

// --- カスタム内容のHTML生成 ---
function formatCustomHTML(data) {
    return `
        <div class="item"><strong>🎨 ボディカラー：</strong><br>${data.bodyColor}</div>
        <div class="item"><strong>⚙ ホイール：</strong><br>${data.wheel}</div>
        <div class="item"><strong>💡 ライト：</strong><br>${data.light}</div>
        <div class="item"><strong>🛠 バンパー：</strong><br>${data.bumper}</div>
        <div class="item"><strong>🪽 エアロ：</strong><br>${data.aero}</div>
    `;
}

// function saveCustom() {
//     alert("カスタム内容を保存しました（仮）");
// }

function goMenu() {
    window.location.href = "";
}
