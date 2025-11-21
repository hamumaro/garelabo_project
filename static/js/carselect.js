let currentIndex = 0;

const carImage = document.querySelector('.car-image');
const carName = document.querySelector('.car-name span[data-bind="car-name"]');
const leftBtn = document.querySelector('.arrow-btn.left');
const rightBtn = document.querySelector('.arrow-btn.right');
const selectBtn = document.getElementById('select-btn');

// 表示更新
function updateCar(){
    const car = vehicles[currentIndex];
    carImage.src = car.image;
    carName.textContent = car.name; 
}

// 左右ボタン
leftBtn.addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + vehicles.length) % vehicles.length;
    updateCar();
});

rightBtn.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % vehicles.length;
    updateCar();
});

// 車選択
function selectCar() {
    const selected = vehicles[currentIndex];
    window.location.href = `/custom_menu/${selected.id}/`;
}

// 選択ボタンと画像クリック
if(selectBtn){
    selectBtn.addEventListener('click', selectCar);
}
carImage.addEventListener('click', selectCar);

// ページ読み込み時に初期表示
window.addEventListener('DOMContentLoaded', updateCar);
