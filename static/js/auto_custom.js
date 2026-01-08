console.log("🚗 自動カスタムJS読み込み完了");

const vehiclesData = JSON.parse(
    document.getElementById("vehicles-data").textContent
);

function showVehicle(id) {
    const vehicle = vehiclesData.find(v => v.id === id);
    document.getElementById("vehicle-image").src = vehicle.image;
}

function gotoAutoCustom() {
    const id = document.getElementById("vehicle-select").value;
    window.location.href = `/custom_menu/auto_custom/?vehicle_id=${id}`;
}

function loadInitialCustom() {

    const container = document.getElementById("custom-content");
    const selectedData = window.initialSelected;  // ← Django側で埋め込む

    if (!selectedData) {
        container.innerHTML = "<p>初期データなし</p>";
        return;
    }

    container.innerHTML = `
        <h3>選択中のカスタム</h3>

        ${selectedData.vehicle ? `<p>車種：${selectedData.vehicle.name}</p>` : ""}
        ${selectedData.color   ? `<p>カラー：${selectedData.color.name}</p>` : ""}
        ${selectedData.wheel   ? `<p>ホイール：${selectedData.wheel.name}</p>` : ""}
        ${selectedData.bumper  ? `<p>バンパー：${selectedData.bumper.name}</p>` : ""}
        ${selectedData.light   ? `<p>ライト：${selectedData.light.name}</p>` : ""}
        ${selectedData.aero    ? `<p>エアロ：${selectedData.aero.name}</p>` : ""}
    `;
}

function loadCustomData() {
    fetch("/auto_custom/api/")
        .then(res => res.json())
        .then(data => {

            if (data.error) {
                document.getElementById("custom-content").innerHTML =
                    `<p style="color:red">${data.error}</p>`;
                return;
            }

            document.getElementById("custom-content").innerHTML = `
                <p>カラー：${data.color}</p>
                <p>ホイール：${data.wheel}</p>
                <p>バンパー：${data.bumper}</p>
                <p>ライト：${data.light}</p>
                <p>エアロ：${data.aero}</p>
            `;
        })
        .catch(err => console.error("❌ エラー:", err));
}


window.onload = loadInitialCustom;