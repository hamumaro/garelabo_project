console.log("NEW bodycolor.js LOADED");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dots = document.querySelectorAll(".color-dot");

  const carFolder = "Rocky";
  const angles = ["front", "side", "rear"];

  let currentColor = "white";
  let angleIndex = 0;

  function updateImage() {
    img.src = `/media/uploads/vehicles/${carFolder}/${currentColor}/${angles[angleIndex]}.png`;
  }

  // 初期表示
  updateImage();

  dots.forEach((btn) => {
    btn.addEventListener("click", () => {
      currentColor = btn.textContent.trim();
      angleIndex = 0;
      updateImage();
    });
  });

  prevBtn.addEventListener("click", () => {
    angleIndex = (angleIndex - 1 + angles.length) % angles.length;
    updateImage();
  });

  nextBtn.addEventListener("click", () => {
    angleIndex = (angleIndex + 1) % angles.length;
    updateImage();
  });
});
