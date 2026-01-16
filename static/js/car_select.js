console.log("car_select.js loaded!");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("carImage");
  const nameDisplay = document.getElementById("carName");

  // name_en を保持する hidden input
  const hiddenNameEn = document.getElementById("selectedCarNameEn");

  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  // JSONデータ取得
  const dataElement = document.getElementById("vehicles-data");
  if (!dataElement) {
    console.error("車両データが見つかりません");
    return;
  }

  const vehicles = JSON.parse(dataElement.textContent);
  if (vehicles.length === 0) return;

  // 現在の選択インデックス
  let index = 0;

  // 表示更新
  function updateDisplay() {
    const vehicle = vehicles[index];

    img.src = vehicle.url;
    img.alt = vehicle.name;

    if (nameDisplay) {
      nameDisplay.textContent = vehicle.name;
    }

    if (hiddenNameEn) {
      hiddenNameEn.value = vehicle.name_en;
    }

    console.log(
      "現在の選択:",
      index,
      vehicle.name,
      "name_en:",
      vehicle.name_en
    );
  }

  // 初期表示
  updateDisplay();

  // 前へ
  prevBtn.addEventListener("click", () => {
    index = (index - 1 + vehicles.length) % vehicles.length;
    updateDisplay();
  });

  // 次へ
  nextBtn.addEventListener("click", () => {
    index = (index + 1) % vehicles.length;
    updateDisplay();
  });
});
