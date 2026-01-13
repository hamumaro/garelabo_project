console.log("wheel.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const wheelBtns = document.querySelectorAll(".wheel-btn");

  // 固定（今はRocky + white）
  const carFolder = "Rocky";
  const angles = ["front", "side", "rear"];

  let currentColor = sessionStorage.getItem("currentColor") || "white";

  let currentWheel = sessionStorage.getItem("currentWheel");
  if (!currentWheel) {
    currentWheel = "wheel1";
    sessionStorage.setItem("currentWheel", currentWheel);
  }
  let angleIndex = 0;

  function updateImage() {
    img.src = `/media/uploads/vehicles/${carFolder}/${currentColor}/${currentWheel}/${angles[angleIndex]}.png`;
    console.log(img.src);
  }

  // 初期表示
  updateImage();

  // ホイール切り替え
  wheelBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      currentWheel = btn.dataset.wheel;
      angleIndex = 0;
      sessionStorage.setItem("currentWheel", currentWheel);
      updateImage();
    });
  });

  // 回転
  prevBtn.addEventListener("click", () => {
    angleIndex = (angleIndex - 1 + angles.length) % angles.length;
    updateImage();
  });

  nextBtn.addEventListener("click", () => {
    angleIndex = (angleIndex + 1) % angles.length;
    updateImage();
  });
});
