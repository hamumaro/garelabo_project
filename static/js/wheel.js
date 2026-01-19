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

  // ===== お気に入りトグル処理 =====
    const favoriteToggle = document.getElementById("favorite-toggle");
    const isFavoriteInput = document.getElementById("is-favorite");

    if (favoriteToggle && isFavoriteInput) {
      // 1. ボタンがクリックされた時のイベント
      favoriteToggle.addEventListener("click", function(e) {
        e.preventDefault(); // 画面遷移を防ぐ

        // 2. 現在の状態を取得して反転させる
        // inputの値が "true" なら次は false、そうでなければ true
        const isCurrentlyFavorite = (isFavoriteInput.value === "true");
        const newState = !isCurrentlyFavorite;

        // 3. HTML上の値を更新 (保存ボタン用)
        isFavoriteInput.value = newState ? "true" : "false";

        // 4. ボタンの見た目を更新
        this.innerText = newState ? "✔ お気に入り" : "お気に入り";

        // ⭐ これを追加するだけ
        this.classList.toggle("is-favorite", newState);

        // (オプション) デバッグ用ログ
        console.log("お気に入り状態を切り替えました:", newState);

        // 5. サーバー側のセッションにも即座に反映（他のページへ移動しても維持するため）
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

  // ===== 表示更新 =====
  function updateImage() {
    const path =
      `/media/uploads/vehicles/${carFolder}` +
      `/${currentColor}/${currentWheel}/${currentBumper}/${angles[angleIndex]}.png`;

    img.src = path;
    img.alt = `${carFolder} ${currentColor} ${currentWheel} ${currentBumper} ${angles[angleIndex]}`;

    console.log("表示中:", {
      car: carFolder,
      color: currentColor,
      wheel: currentWheel,
      bumper: currentBumper,
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
