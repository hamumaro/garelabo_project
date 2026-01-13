console.log("NEW bodycolor.js LOADED");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dots = document.querySelectorAll(".color-dot");

  if (!img) {
    console.error("car-image が見つかりません");
    return;
  }

  // ===== 固定・初期設定 =====
  const carFolder = "Rocky";
  const angles = ["front", "side", "rear"];

  let currentColor = sessionStorage.getItem("currentColor");
  if (!currentColor) {
    currentColor = "white";
    sessionStorage.setItem("currentColor", currentColor);
  }
  let angleIndex = 0;

  // ===== 表示更新 =====
  function updateImage() {
    const path = `/media/uploads/vehicles/${carFolder}/${currentColor}/${angles[angleIndex]}.png`;
    img.src = path;
    img.alt = `${carFolder} ${currentColor} ${angles[angleIndex]}`;

    console.log("表示中:", path);
  }

  // 初期表示
  updateImage();

  // ===== カラー変更 =====
  dots.forEach((btn) => {
    btn.addEventListener("click", () => {
      const color = btn.dataset.color;
      if (!color) return;

      currentColor = color;
      angleIndex = 0; // 色変えたら正面に戻す
      sessionStorage.setItem("currentColor", currentColor);
      updateImage();
    });
  });

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
