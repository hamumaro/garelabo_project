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

  // ===== ★追加: パスからフォルダ名だけを取り出す関数 =====
  function getFolderName(path) {
      if (!path) return "";
      return path.replace(/\\/g, '/').split('/').pop();
  }

  // ===== お気に入りトグル処理 =====
  const favoriteToggle = document.getElementById("favorite-toggle");
  const isFavoriteInput = document.getElementById("is-favorite");

  if (favoriteToggle && isFavoriteInput) {
    favoriteToggle.addEventListener("click", function(e) {
      e.preventDefault();
      const isCurrentlyFavorite = (isFavoriteInput.value === "true");
      const newState = !isCurrentlyFavorite;

      isFavoriteInput.value = newState ? "true" : "false";
      this.innerText = newState ? "✔ お気に入り" : "お気に入り";
      this.classList.toggle("is-favorite", newState);

      fetch('/update_session_favorite/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_favorite: newState })
      }).catch(err => console.error("通信エラー:", err));
    });
  }

  // ===== URL から車(name_en)取得 =====
  const params = new URLSearchParams(window.location.search);
  let carFolder = params.get("car");

  if (!carFolder) {
    carFolder = sessionStorage.getItem("selectedCar");
  }

  if (!carFolder) {
    console.error("車情報(car)が取得できません");
    return;
  }
  sessionStorage.setItem("selectedCar", carFolder);
  console.log("選択された車:", carFolder);

  // ===== 固定設定 =====
  const angles = ["front", "side", "rear"];

  // ===== 状態（並列） =====
  // ★修正: 読み込み時に getFolderName でパスをきれいにする (重要)
  // これにより、セッションに長いパスが残っていても、ここで修復されます。
  let currentColor = getFolderName(sessionStorage.getItem("currentColor")) || "white";
  let currentWheel = getFolderName(sessionStorage.getItem("currentWheel")) || "wheel1";
  let currentBumper = getFolderName(sessionStorage.getItem("currentBumper")) || "bumper1";

  // きれいになった値を保存し直す
  sessionStorage.setItem("currentColor", currentColor);
  sessionStorage.setItem("currentWheel", currentWheel);
  sessionStorage.setItem("currentBumper", currentBumper);

  let angleIndex = 0;

  // ===== 表示更新 =====
  function updateImage() {
    // 表示時も念のためクリーニングを通す
    const cleanColor = getFolderName(currentColor);
    const cleanWheel = getFolderName(currentWheel);
    const cleanBumper = getFolderName(currentBumper);

    const path =
      `/media/uploads/vehicles/${carFolder}` +
      `/${cleanColor}/${cleanWheel}/${cleanBumper}/${angles[angleIndex]}.png`;

    img.src = path;
    img.alt = `${carFolder} ${cleanColor} ${cleanWheel} ${cleanBumper} ${angles[angleIndex]}`;

    console.log("表示中:", {
      car: carFolder,
      color: cleanColor,
      wheel: cleanWheel,
      bumper: cleanBumper,
      angle: angles[angleIndex],
    });
  }

  // 初期表示
  updateImage();

  // ===== カラー変更（ホイール保持） =====
  dots.forEach((btn) => {
    btn.addEventListener("click", () => {
      const rawColor = btn.dataset.color;
      if (!rawColor) return;

      // ★修正: 保存前にフォルダ名だけにする
      currentColor = getFolderName(rawColor);
      
      angleIndex = 0; // 正面へ戻す
      sessionStorage.setItem("currentColor", currentColor);

      console.log("カラー変更:", currentColor);
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