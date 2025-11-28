console.log("car_select.js loaded!");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("carImage"); // HTMLのIDと一致させる
  const nameDisplay = document.getElementById("carName"); 
  const hiddenInput = document.getElementById("selectedCarId"); // ★追加: 隠しフォーム
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  // JSONデータの取得
  const dataElement = document.getElementById("vehicles-data");
  if (!dataElement) {
      console.error("車両データが見つかりません");
      return;
  }
  const vehicles = JSON.parse(dataElement.textContent);

  if (vehicles.length === 0) return;

  // 初期インデックス
  let index = 0;

  // 表示＆データを更新する関数
  function updateDisplay() {
      // 1. 画像と名前の更新
      img.src = vehicles[index].url;
      img.alt = vehicles[index].name;
      
      if (nameDisplay) {
          nameDisplay.textContent = vehicles[index].name;
      }

      // 2. ★重要: フォームの隠しIDを更新する
      if (hiddenInput) {
          hiddenInput.value = vehicles[index].id;
      }
      
      console.log("現在の選択:", index, vehicles[index].name, "ID:", vehicles[index].id);
  }

  // 前へボタン
  prevBtn.addEventListener("click", () => {
    // 1つ戻る（0より小さくなったら最後にループ）
    index = (index - 1 + vehicles.length) % vehicles.length;
    updateDisplay();
  });

  // 次へボタン
  nextBtn.addEventListener("click", () => {
    // 1つ進む（要素数を超えたら最初にループ）
    index = (index + 1) % vehicles.length;
    updateDisplay();
  });
});