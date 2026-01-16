// custom_slider.js
console.log("custom_slider.js 読み込まれたよ！");

document.addEventListener("DOMContentLoaded", () => {
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    const dataElement = document.getElementById("vehicles-data");

    if (!dataElement) {
        console.error("❌ slider: vehicles-data が見つかりません。");
        return;
    }

    const vData = JSON.parse(dataElement.textContent);
    const numToShow = 3;
    const vehiclesToLoop = vData.slice(0, numToShow);
    
    let index = 0; 

    if (img && vehiclesToLoop.length > 0) {
        img.src = vehiclesToLoop[index].url;
        img.alt = vehiclesToLoop[index].name;
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener("click", () => {
            index = (index - 1 + vehiclesToLoop.length) % vehiclesToLoop.length;
            img.src = vehiclesToLoop[index].url;
            img.alt = vehiclesToLoop[index].name;
        });

        nextBtn.addEventListener("click", () => {
            index = (index + 1) % vehiclesToLoop.length;
            img.src = vehiclesToLoop[index].url;
            img.alt = vehiclesToLoop[index].name;
        });
    }
});