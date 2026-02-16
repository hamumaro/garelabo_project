document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("carImage");
  const nameDisplay = document.getElementById("carName");
  const hiddenNameEn = document.getElementById("selectedCarNameEn");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  const dataElement = document.getElementById("vehicles-data");
  if (!dataElement) {
    console.error("車両データが見つかりません");
    return;
  }

  let vehicles = [];
  try {
    vehicles = JSON.parse(dataElement.textContent);
  } catch (e) {
    console.error("JSON parse error", e);
    return;
  }
  
  if (vehicles.length === 0) return;

  let index = 0;

  function updateDisplay() {
    const vehicle = vehicles[index];
    const imageUrl = vehicle.url;

    if (!imageUrl) return;

    // HTML側でパスを完成させているため、ここでの文字列結合は不要です
    img.src = imageUrl;
    img.alt = vehicle.name;

    if (nameDisplay) {
      nameDisplay.textContent = vehicle.name;
    }

    if (hiddenNameEn) {
      hiddenNameEn.value = vehicle.name_en;
    }
  }

  // 初期化時の実行
  updateDisplay();

  prevBtn.addEventListener("click", () => {
    index = (index - 1 + vehicles.length) % vehicles.length;
    updateDisplay();
  });

  nextBtn.addEventListener("click", () => {
    index = (index + 1) % vehicles.length;
    updateDisplay();
  });
});