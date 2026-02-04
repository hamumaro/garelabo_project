console.log("NEW aeroparts.js LOADED (WITH PANEL TOGGLE)");

document.addEventListener("DOMContentLoaded", () => {
    /* =================================================================
       1. 要素の取得 & ヘルパー関数
    ================================================================= */
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    
    // エアロ特有
    const aeroBtns = document.querySelectorAll(".aero-btn");
    const aeroPanel = document.getElementById("aero-panel");
    const aeroOpenBtn = document.getElementById("open-aero"); // 追加
    const aeroValue = document.getElementById("aeroValue"); // 追加

    const currentVehicleIdInput = document.getElementById('current-vehicle-id');
    const currentVehicleId = currentVehicleIdInput ? currentVehicleIdInput.value : null;
    const autoLink = document.getElementById('auto-custom-link');

    if (!img) {
        console.error("car-image が見つかりません");
        return;
    }

    function getFolderName(path) {
        if (!path) return "";
        let name = String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop();
        return name.replace(/\.[^/.]+$/, "");
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function setSrcWithFallback(imgEl, urls) {
        let i = 0;
        imgEl.onload = null;
        const tryLoad = () => {
            if (i >= urls.length) {
                console.error("全ての画像候補が見つかりませんでした", urls);
                imgEl.onerror = null;
                return;
            }
            imgEl.onerror = () => {
                i++;
                tryLoad();
            };
            imgEl.src = urls[i];
        };
        tryLoad();
    }

    /* =================================================================
       2. 初期化 & リセットロジック
    ================================================================= */
    const params = new URLSearchParams(window.location.search);
    const resetParam = params.get("reset");
    const urlCar = params.get("car");
    
    const serverCar = document.getElementById("server-car-folder")?.value;
    const serverColor = document.getElementById("server-color-folder")?.value;
    const serverWheel = document.getElementById("server-wheel-folder")?.value;
    const serverBumper = document.getElementById("server-bumper-folder")?.value;
    const serverAero = document.getElementById("server-aero-folder")?.value;

    const storedCar = sessionStorage.getItem("selectedCar");

    if (resetParam === "true" || (urlCar && storedCar && urlCar !== storedCar)) {
        sessionStorage.removeItem("currentColor");
        sessionStorage.removeItem("currentWheel");
        sessionStorage.removeItem("currentBumper");
        sessionStorage.removeItem("currentAero");
        if (urlCar) sessionStorage.setItem("selectedCar", urlCar);

        if (resetParam === "true") {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete("reset");
            window.history.replaceState(null, "", newUrl);
        }
    }

    let carFolder = urlCar || sessionStorage.getItem("selectedCar");
    if (!carFolder && serverCar) carFolder = getFolderName(serverCar);
    if (!carFolder) carFolder = "CompactSedan";
    sessionStorage.setItem("selectedCar", carFolder);

    const initPart = (key, serverVal, defaultVal) => {
        if (!sessionStorage.getItem(key)) {
            const val = getFolderName(serverVal) || defaultVal;
            sessionStorage.setItem(key, val);
        }
        return sessionStorage.getItem(key);
    };

    let currentColor = initPart("currentColor", serverColor, "white");
    let currentWheel = initPart("currentWheel", serverWheel, "wheel1");
    let currentBumper = initPart("currentBumper", serverBumper, "bumper1");
    let currentAero = initPart("currentAero", serverAero, "aero1");

    const angles = ["front", "side_right", "rear", "side_left"];
    let angleIndex = 0;

    /* =================================================================
       3. 表示更新 & サーバー同期
    ================================================================= */
    function updateState() {
        const c = currentColor;
        const w = currentWheel;
        
        let b = currentBumper;
        if (!b || b === "normal") b = "bumper1";

        let a = currentAero;
        if (!a || a === "normal") a = "aero1";

        const angle = angles[angleIndex];

        let urls = [];
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${b}/${a}/${angle}.png`);
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${b}/${angle}.png`);

        setSrcWithFallback(img, urls);
        img.alt = `${carFolder} ${c} ${w} ${b} ${a} ${angle}`;

        // エアロボタン選択状態
        if (aeroBtns) {
            aeroBtns.forEach(btn => {
                const btnVal = getFolderName(btn.dataset.aero);
                const isSelected = (btnVal === currentAero) || (currentAero === "normal" && btnVal === "aero1");
                btn.classList.toggle('is-selected', isSelected);
            });
        }
        if (aeroValue) aeroValue.value = a;

        updateAutoCustomLink();
    }

    function updateAutoCustomLink() {
        if (!autoLink) return;
        const url = new URL(autoLink.href, window.location.origin);
        if (currentVehicleId) url.searchParams.set('vehicle_id', currentVehicleId);
        url.searchParams.set('color', currentColor);
        url.searchParams.set('wheel', currentWheel);
        
        if (currentBumper && currentBumper !== "normal" && currentBumper !== "bumper1") {
            url.searchParams.set('bumper', currentBumper);
        } else {
            url.searchParams.delete('bumper');
        }

        if (currentAero && currentAero !== "normal" && currentAero !== "aero1") {
            url.searchParams.set('aero', currentAero);
        } else {
            url.searchParams.delete('aero');
        }
        autoLink.href = url.toString();
    }

    async function updateServerSession(type, value) {
        try {
            await fetch('/update_session_parts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ part_type: type, folder_name: value })
            });
        } catch (e) {
            console.error("Session sync failed:", e);
        }
    }

    updateState();

    /* =================================================================
       4. イベントリスナー
    ================================================================= */
    
    // エアロ変更
    aeroBtns.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const rawPath = btn.dataset.aero;
            if (!rawPath) return;

            const folderName = getFolderName(rawPath);
            currentAero = folderName;
            sessionStorage.setItem("currentAero", currentAero);

            updateState();
            await updateServerSession("aero", currentAero);
        });
    });

    prevBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex - 1 + angles.length) % angles.length;
        updateState();
    });
    nextBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex + 1) % angles.length;
        updateState();
    });

    const favoriteToggle = document.getElementById("favorite-toggle");
    const isFavoriteInput = document.getElementById("is-favorite");
    if (favoriteToggle && isFavoriteInput) {
        favoriteToggle.addEventListener("click", (e) => {
            e.preventDefault();
            const isFav = (isFavoriteInput.value === "true");
            const newState = !isFav;
            isFavoriteInput.value = newState ? "true" : "false";
            favoriteToggle.innerText = newState ? "✔ お気に入り" : "お気に入り";
            favoriteToggle.classList.toggle("is-favorite", newState);

            fetch("/update_session_favorite/", {
                method: "POST",
                headers: { "X-CSRFToken": getCookie('csrftoken'), "Content-Type": "application/json" },
                body: JSON.stringify({ is_favorite: newState }),
                keepalive: true,
            }).catch(console.error);
        });
    }

    /* =================================================================
       5. UI機能 (パネル開閉・ドロワー・フルスクリーン)
    ================================================================= */
    
    // ★追加: エアロパネル開閉
    const toggleAeroPanel = (open) => {
        if (!aeroPanel) return;
        const action = open ? 'add' : 'remove';
        aeroPanel.classList[action]("is-open", "panel-enter");
        aeroPanel.setAttribute("aria-hidden", !open);
    };

    aeroOpenBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const isOpen = aeroPanel?.classList.contains("is-open");
        toggleAeroPanel(!isOpen);
    });

    // パネル内クリックで閉じない
    aeroPanel?.addEventListener("click", (e) => e.stopPropagation());

    // ドロワー
    const menuBtn = document.getElementById("menu-open");
    const drawer = document.getElementById("drawer");
    const drawerOverlay = document.getElementById("drawer-overlay");
    const drawerCloseBtn = document.getElementById("drawer-close");
    const menuHint = document.getElementById("menu-hint");

    const toggleDrawer = (open) => {
        if (!drawer || !drawerOverlay) return;
        const action = open ? 'add' : 'remove';
        drawer.classList[action]("is-open");
        drawerOverlay.classList[action]("is-open");
        drawer.setAttribute("aria-hidden", !open);
        drawerOverlay.setAttribute("aria-hidden", !open);
        menuBtn?.setAttribute("aria-expanded", open);
        if(open && menuHint) menuHint.setAttribute("aria-hidden", "true");
    };

    menuBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleDrawer(!drawer.classList.contains("is-open"));
    });

    drawerCloseBtn?.addEventListener("click", () => toggleDrawer(false));
    drawerOverlay?.addEventListener("click", () => toggleDrawer(false));

    // 全体クリック監視（パネル外クリックで閉じる）
    document.addEventListener("click", (e) => {
        // エアロパネルが開いていて、パネル外かつボタン外なら閉じる
        if (aeroPanel?.classList.contains("is-open") && !aeroPanel.contains(e.target) && !aeroOpenBtn?.contains(e.target)) {
            toggleAeroPanel(false);
        }
        
        // ドロワーが開いていて... (既存ロジックと統合可だが個別記述)
        if (drawer?.classList.contains("is-open") && !drawer.contains(e.target) && !menuBtn?.contains(e.target) && !drawerOverlay?.contains(e.target)) {
            toggleDrawer(false);
        }
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            toggleDrawer(false);
            toggleAeroPanel(false);
            closeFullscreen();
        }
    });

    // フルスクリーン & 保存
    const fsOverlay = document.getElementById("fullscreen-overlay");
    const fsImage = document.getElementById("fullscreen-image");
    const fsClose = document.getElementById("fullscreen-close");
    const fsSave = document.getElementById("fullscreen-save");

    const openFullscreen = () => {
        if (!img.src || !fsOverlay) return;
        fsImage.src = img.src;
        fsOverlay.classList.add("is-open");
        fsOverlay.setAttribute("aria-hidden", "false");
        fsOverlay.style.display = "flex";
        document.body.style.overflow = "hidden";
    };

    const closeFullscreen = () => {
        if (!fsOverlay) return;
        fsOverlay.classList.remove("is-open");
        fsOverlay.setAttribute("aria-hidden", "true");
        fsOverlay.style.display = "";
        document.body.style.overflow = "";
    };

    img.addEventListener("click", (e) => { e.stopPropagation(); openFullscreen(); });
    img.closest(".car-frame")?.addEventListener("click", (e) => { e.preventDefault(); openFullscreen(); });
    
    fsClose?.addEventListener("click", closeFullscreen);
    fsOverlay?.addEventListener("click", (e) => {
        if (e.target === fsOverlay) closeFullscreen();
    });

    fsSave?.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (!fsImage.src) return;

        try {
            if (!fsImage.complete || fsImage.naturalWidth === 0) {
                await new Promise((resolve, reject) => {
                    fsImage.onload = resolve;
                    fsImage.onerror = reject;
                    setTimeout(() => reject(new Error("Timeout")), 3000);
                });
            }
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const w = fsImage.naturalWidth;
            const h = fsImage.naturalHeight;
            canvas.width = w;
            canvas.height = h;

            ctx.drawImage(fsImage, 0, 0, w, h);

            const text = "GARELABO+";
            const fontSize = Math.max(20, Math.round(w * 0.04));
            ctx.font = `bold ${fontSize}px sans-serif`;
            ctx.textAlign = "right";
            ctx.textBaseline = "bottom";
            const padding = Math.round(fontSize * 0.5);
            ctx.shadowColor = "rgba(0,0,0,0.7)";
            ctx.shadowBlur = 4;
            ctx.fillStyle = "#ffffff";
            ctx.fillText(text, w - padding, h - padding);

            canvas.toBlob(blob => {
                if(blob) {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `garelabo_aero_${new Date().getTime()}.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
            }, "image/png");

        } catch (err) {
            console.error("保存エラー:", err);
            alert("画像の保存に失敗しました。");
        }
    });
});