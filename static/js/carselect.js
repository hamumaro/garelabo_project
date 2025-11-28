// let currentIndex = 0;

// const carImage = document.querySelector('.car-image');
// const carName = document.querySelector('.car-name span[data-bind="car-name"]');
// const leftBtn = document.querySelector('.arrow-btn.left');
// const rightBtn = document.querySelector('.arrow-btn.right');
// const selectBtn = document.getElementById('select-btn');

// // 表示更新
// function updateCar(){
//     const car = vehicles[currentIndex];
//     carImage.src = car.image;
//     carName.textContent = car.name; 
// }

// // 左右ボタン
// leftBtn.addEventListener('click', () => {
//     currentIndex = (currentIndex - 1 + vehicles.length) % vehicles.length;
//     updateCar();
// });

// rightBtn.addEventListener('click', () => {
//     currentIndex = (currentIndex + 1) % vehicles.length;
//     updateCar();
// });

// selectBtn.addEventListener('click', () => {
//     const selectedCarId = vehicles[currentIndex].id;
//     window.location.href = `/custom_menu/?car_id=${selectedCarId}`;
// });

// // 初期表示
// updateCar();
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
//   const numToShow = 3; //表示する枚数
  const vehiclesToLoop = vehicles.slice(startIndex);
  let index = 1;
  prevBtn.addEventListener("click", () => {
    index = (index - 3 + vehiclesToLoop.length) % vehiclesToLoop.length;
    console.log("prev clicked, index =", index);
    img.src = vehiclesToLoop[index].url;
    img.alt = vehiclesToLoop[index].name;
  });

  nextBtn.addEventListener("click", () => {
    index = (index + 3) % vehiclesToLoop.length;
    console.log("prev clicked, index =", index);
    img.src = vehiclesToLoop[index].url;
    img.alt = vehiclesToLoop[index].name;
  });
});
