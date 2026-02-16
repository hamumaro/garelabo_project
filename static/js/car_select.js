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
    let imageUrl = vehicle.url;

    // 【修正点】URLが画像拡張子で終わっていない場合、代表画像(0.png)を付与する
    // ※ サーバー内の実際のファイル名に合わせて '0.png' や '1.png' に変更してください
    if (imageUrl && !imageUrl.match(/\.(png|jpg|jpeg|gif)$/i)) {
        // 末尾にスラッシュがない場合は追加
        if (!imageUrl.endsWith('/')) {
            imageUrl += '/';
        }
        imageUrl += 'side_left.png'; // ここでフォルダ内のファイル名を指定
    }

    img.src = imageUrl;
    img.alt = vehicle.name;

    if (nameDisplay) {
      nameDisplay.textContent = vehicle.name;
    }

    if (hiddenNameEn) {
      hiddenNameEn.value = vehicle.name_en;
    }
  }

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

