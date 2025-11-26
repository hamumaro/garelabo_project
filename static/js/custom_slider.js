console.log("custom_slider.js 読み込まれたよ！");
document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("car-image");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  // vehicles 配列はHTML側で JSON にして渡す
  const vehicles = JSON.parse(
    document.getElementById("vehicles-data").textContent
  );
  const startIndex = 0; //初期値設定
  const numToShow = 3; //表示する枚数
  const vehiclesToLoop = vehicles.slice(startIndex, startIndex + numToShow);
  let index = 3;
  prevBtn.addEventListener("click", () => {
    index = (index - 1 + vehiclesToLoop.length) % vehiclesToLoop.length;
    console.log("prev clicked, index =", index);
    img.src = vehiclesToLoop[index].url;
    img.alt = vehiclesToLoop[index].name;
  });

  nextBtn.addEventListener("click", () => {
    index = (index + 1) % vehiclesToLoop.length;
    console.log("prev clicked, index =", index);
    img.src = vehiclesToLoop[index].url;
    img.alt = vehiclesToLoop[index].name;
  });
});
