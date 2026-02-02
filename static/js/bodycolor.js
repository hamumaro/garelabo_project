console.log("NEW bodycolor.js LOADED (RESET FIX)");

document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dots = document.querySelectorAll(".color-dot");

  // ===== サーバーセッション更新 =====
  function updateServerSession(partType, folderName) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/update_session_parts/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ part_type: partType, folder_name: folderName }),
      keepalive: true
    }).catch(err => console.error("Session update error:", err));
  }

  if (!img) {
    console.error("car-image が見つかりません");
    return;
  }

  function getFolderName(path) {
      if (!path) return "";
      return path.replace(/\\/g, '/').split('/').pop();
  }

  const serverCar = document.getElementById("server-car-folder")?.value;
  const serverColor = document.getElementById("server-color-folder")?.value;
  const serverWheel = document.getElementById("server-wheel-folder")?.value;
  const serverBumper = document.getElementById("server-bumper-folder")?.value;

  // ===== 1. 初期値の決定とリセット処理 (★修正箇所) =====
  const params = new URLSearchParams(window.location.search);
  const resetParam = params.get("reset");
  const urlCar = params.get("car");
  const storedCar = sessionStorage.getItem("selectedCar");

  // リセット要求(reset=true)があるか、または車両が異なる場合はリセット
  if (resetParam === "true" || (urlCar && storedCar && urlCar !== storedCar)) {
      console.log("リセット要求を検知: セッションストレージをクリアします");
      sessionStorage.removeItem("currentColor");
      sessionStorage.removeItem("currentWheel");
      sessionStorage.removeItem("currentBumper");
      sessionStorage.setItem("selectedCar", urlCar); // 新しい車をセット
      
      // URLからresetパラメータのみ削除 (次回リロード時の意図しないリセットを防止)
      if (resetParam === "true") {
          const newUrl = new URL(window.location);
          newUrl.searchParams.delete("reset");
          window.history.replaceState(null, '', newUrl);
      }
  }

  // 車種フォルダの決定
  let carFolder = urlCar;
  if (!carFolder) carFolder = sessionStorage.getItem("selectedCar");
  if (!carFolder && serverCar) carFolder = serverCar;

  if (!carFolder) {
    console.error("車情報(car)が取得できません");
    return;
  }
  sessionStorage.setItem("selectedCar", carFolder);

  // ★修正: リセット直後や値がない場合のみサーバー値で初期化
  if (serverColor && !sessionStorage.getItem("currentColor")) {
      sessionStorage.setItem("currentColor", getFolderName(serverColor));
  }
  if (serverWheel && !sessionStorage.getItem("currentWheel")) {
      sessionStorage.setItem("currentWheel", getFolderName(serverWheel));
  }
  if (serverBumper && !sessionStorage.getItem("currentBumper")) {
      sessionStorage.setItem("currentBumper", getFolderName(serverBumper));
  }

  let currentColor = getFolderName(sessionStorage.getItem("currentColor")) || "white";
  let currentWheel = getFolderName(sessionStorage.getItem("currentWheel")) || "wheel1";
  let currentBumper = getFolderName(sessionStorage.getItem("currentBumper")) || "bumper1";
  
  const angles = ["front", "side_right", "rear","side_left"]; 
  let angleIndex = 0;

  // ===== 表示更新 =====
  function updateImage() {
    const cleanColor = getFolderName(currentColor);
    const cleanWheel = getFolderName(currentWheel);
    const cleanBumper = getFolderName(currentBumper);

    const path =
      `/media/uploads/vehicles/${carFolder}` +
      `/${cleanColor}/${cleanWheel}/${cleanBumper}/${angles[angleIndex]}.png`;

    img.src = path;
    img.alt = `${carFolder} ${cleanColor} ${cleanWheel} ${cleanBumper} ${angles[angleIndex]}`;
  }

  updateImage();

  // ===== カラー変更 =====
  dots.forEach((btn) => {
    btn.addEventListener("click", () => {
      const rawColor = btn.dataset.color;
      if (!rawColor) return;

      currentColor = getFolderName(rawColor);
      angleIndex = 0;
      sessionStorage.setItem("currentColor", currentColor);

      // サーバーへ通知
      updateServerSession('color', currentColor);

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

  // ===== お気に入りトグル =====
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
        body: JSON.stringify({ is_favorite: newState }),
        keepalive: true
      }).catch(err => console.error("通信エラー:", err));
    });
  }
});