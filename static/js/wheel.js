console.log("NEW wheel.js LOADED");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const wheelBtns = document.querySelectorAll(".wheel-btn");

  if (!img) {
    console.error("car-image が見つかりません");
    return;
  }

  // ===== お気に入りトグル処理 (そのまま維持) =====
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

      // サーバー側のセッションにも即座に反映
      fetch('/update_session_favorite/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_favorite: newState })
      })
      .then(response => {
        if (!response.ok) console.error("セッション更新失敗");
      })
      .catch(err => console.error("通信エラー:", err));
    });
  }

  // ===== ★修正ポイント1: 車情報の取得 (優先順位を変更) =====
  
  // 1. HTMLに埋め込まれた「サーバーからの正しい値」を最優先で取得
  const serverCarFolderInput = document.getElementById("server-car-folder");
  let carFolder = serverCarFolderInput ? serverCarFolderInput.value : null;

  // 2. HTMLになければ、URLパラメータを見る
  if (!carFolder) {
    const params = new URLSearchParams(window.location.search);
    carFolder = params.get("car");
  }

  // 3. それでもなければ、セッションを見る
  if (!carFolder) {
    carFolder = sessionStorage.getItem("selectedCar");
  }

  // 4. 取得した値をセッションに上書き保存 (これで古い「Rocky」が消えます)
  if (carFolder) {
    sessionStorage.setItem("selectedCar", carFolder);
    console.log("車フォルダを確定:", carFolder);
  } else {
    console.error("車情報(car)が取得できません");
    return;
  }

  // ===== 固定設定 =====
  const angles = ["front", "side", "rear"];

  // ===== 状態（並列） =====
  let currentColor = sessionStorage.getItem("currentColor");
  if (!currentColor) {
    currentColor = "white";
    sessionStorage.setItem("currentColor", currentColor);
  }

  let currentWheel = sessionStorage.getItem("currentWheel");
  if (!currentWheel) {
    currentWheel = "wheel1";
    sessionStorage.setItem("currentWheel", currentWheel);
  }

  let currentBumper = sessionStorage.getItem("currentBumper");
  if (!currentBumper) {
    currentBumper = "bumper1";
    sessionStorage.setItem("currentBumper", currentBumper);
    console.log("初期バンパーを設定:", currentBumper);
  }

  let angleIndex = 0;

  // ===== ★修正ポイント2: パスのクリーニング関数を追加 =====
  function getFolderName(path) {
      if (!path) return "";
      // パスから最後のフォルダ名だけを取り出す (例: "uploads/.../wheel1" -> "wheel1")
      return path.replace(/\\/g, '/').split('/').pop();
  }

  // ===== 表示更新 =====
  function updateImage() {
    // クリーニング関数を通してから使用する
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

  // ===== ホイール変更（バンパー保持） =====
  wheelBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const wheel = btn.dataset.wheel;
      if (!wheel) return;

      currentWheel = wheel;
      angleIndex = 0;
      sessionStorage.setItem("currentWheel", currentWheel);

      console.log("ホイール変更:", currentWheel);
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