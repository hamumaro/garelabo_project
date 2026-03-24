// エラーメッセージ表示
const errorMeaages = {
    menuLoad : "メニューを開くことができません \n読み込みに差失敗しました",
    switchFail : "画面の切り替えに失敗しました",
    saveFail : "データの保存に失敗しました",
    deleteFail : "カスタムデータの削除に失敗しました",
};

const params = new URLSearchParams(window.location.search);
const type = params.get("type");

// エラーメッセージの表示切り替え
const message = errorMeaages[type] || "不明なエラーが発生しました";
document.getElementById("error-message").textContent = message;

// 戻る／再試行ボタン
function goBack() {
    window.history.back();
}

function reloadPage() {
    window.location.reload();
}