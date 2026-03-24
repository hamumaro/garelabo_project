document.addEventListener("DOMContentLoaded", () => {
  const vehicles = JSON.parse(
    document.getElementById("vehicles-data").textContent
  );

  const link = document.getElementById("auto-custom-link");
  const carImage = document.getElementById("car-image"); // 画像要素を取得
  let currentIndex = 0;

  function updateDisplay() {
    // 1. 画像のsrcを更新（これで回転/切り替えができるようになります）
    if (vehicles[currentIndex]) {
      carImage.src = vehicles[currentIndex].url;
      carImage.alt = vehicles[currentIndex].name;
      
      // 2. 自動カスタムリンクのURLを更新 (idを使用)
      link.href = `/auto_custom/${vehicles[currentIndex].id}/`;
    }
  }

  document.getElementById("prev-btn").addEventListener("click", () => {
    currentIndex = (currentIndex - 1 + vehicles.length) % vehicles.length;
    updateDisplay(); // 表示更新
  });

  document.getElementById("next-btn").addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % vehicles.length;
    updateDisplay(); // 表示更新
  });

  // 初期表示の反映
  updateDisplay();
});

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dots = document.querySelectorAll(".color-dot");

  if (!img) {
    return;
  }

  // ===== 固定・初期設定 =====
  const carFolder = "Rocky";
  const angles = ["front", "side", "rear"];

  let currentColor = "white";
  let angleIndex = 0;

  // ===== 表示更新 =====
  function updateImage() {
    const path = `/media/uploads/vehicles/${carFolder}/${currentColor}/${angles[angleIndex]}.png`;
    img.src = path;
    img.alt = `${carFolder} ${currentColor} ${angles[angleIndex]}`;
  }

  // 初期表示
  updateImage();

  // ===== 回転 =====
  prevBtn?.addEventListener("click", () => {
    angleIndex = (angleIndex - 1 + angles.length) % angles.length;
    updateImage();
  });

  nextBtn?.addEventListener("click", () => {
    angleIndex = (angleIndex + 1) % angles.length;
    updateImage();
  });
});