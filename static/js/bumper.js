console.log("bumper.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const bumperBtns = document.querySelectorAll(".bumper-btn");

  // 固定
  const carFolder = "Rocky";
  const angles = ["front", "side", "rear"];

  // bodycolor.js / wheel.js から引き継ぎ
  const currentColor = sessionStorage.getItem("currentColor") || "white";
  const currentWheel = sessionStorage.getItem("currentWheel") || "wheel1";

  let currentBumper = sessionStorage.getItem("currentBumper");
  if (!currentBumper) {
    currentBumper = "bumper1";
    sessionStorage.setItem("currentBumper", currentBumper);
  }
  let angleIndex = 0;

  function updateImage() {
    const path = `/media/uploads/vehicles/${carFolder}/${currentColor}/${currentWheel}/${currentBumper}/${angles[angleIndex]}.png`;
    img.src = path;
    img.alt = `${carFolder} ${currentColor} ${currentWheel} ${currentBumper}`;
    console.log(path);
  }

  // 初期表示
  updateImage();

  // バンパー切り替え
  bumperBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      currentBumper = btn.dataset.bumper;
      angleIndex = 0;
      sessionStorage.setItem("currentBumper", currentBumper);
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
