document.addEventListener("DOMContentLoaded", () => {
    /* =================================================================
       1. 要素の取得 & ヘルパー関数
    ================================================================= */
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    
    // バンパー特有の要素
    const bumperBtns = document.querySelectorAll(".bumper-btn");
    const bumperPanel = document.getElementById("bumper-panel");
    const bumperOpenBtn = document.getElementById("open-bumper");
    const bumperValue = document.getElementById("bumperValue");

    const currentVehicleIdInput = document.getElementById('current-vehicle-id');
    const currentVehicleId = currentVehicleIdInput ? currentVehicleIdInput.value : null;
    const autoLink = document.getElementById('auto-custom-link');

    if (!img) {
        return;
    }

    // パスからフォルダ名を抽出
    function getFolderName(path) {
        if (!path) return "";
        let name = String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop();
        return name.replace(/\.[^/.]+$/, "");
    }

    // CSRFトークン取得
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

    // 画像ロード処理（フォールバック付き）
    function setSrcWithFallback(imgEl, urls) {
        let i = 0;
        imgEl.onload = null;
        
        const tryLoad = () => {
            if (i >= urls.length) {
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

    // リセット条件
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
    // normal ではなく bumper1 をデフォルトに
    let currentBumper = initPart("currentBumper", serverBumper, "bumper1");
    // normal ではなく aero1 をデフォルトに
    let currentAero = initPart("currentAero", serverAero, "aero1");

    const angles = ["front", "side_right", "rear", "side_left"];
    let angleIndex = 0;

    /* =================================================================
       3. 表示更新 & サーバー同期
    ================================================================= */
    
    function updateState() {
        const c = currentColor;
        const w = currentWheel;
        
        // ★修正: normal除去ロジック
        let b = currentBumper;
        if (!b || b === "normal") b = "bumper1";

        let a = currentAero;
        if (!a || a === "normal") a = "aero1";

        const angle = angles[angleIndex];

        // 画像パス候補
        let urls = [];
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${b}/${a}/${angle}.png`);
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${b}/${angle}.png`); // エアロなし(aero1)フォールバック

        setSrcWithFallback(img, urls);
        img.alt = `${carFolder} ${c} ${w} ${b} ${a} ${angle}`;

        // バンパーボタンの選択状態更新
        if (bumperBtns) {
            bumperBtns.forEach(btn => {
                const btnVal = getFolderName(btn.dataset.bumper);
                // currentBumperがnormalの場合も考慮して比較
                const isSelected = (btnVal === currentBumper) || (currentBumper === "normal" && btnVal === "bumper1");
                btn.classList.toggle('is-selected', isSelected);
            });
        }
        
        if (bumperValue) bumperValue.value = b;

        updateAutoCustomLink();
    }

    function updateAutoCustomLink() {
        if (!autoLink) return;
        const url = new URL(autoLink.href, window.location.origin);
        
        if (currentVehicleId) url.searchParams.set('vehicle_id', currentVehicleId);
        url.searchParams.set('color', currentColor);
        url.searchParams.set('wheel', currentWheel);
        
        // bumper1 (実質normal) 以外の場合のみパラメータ付与
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
            // エラー処理削除
        }
    }

    updateState();

    /* =================================================================
       4. イベントリスナー
    ================================================================= */
    
    // バンパー変更
    bumperBtns.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const rawPath = btn.dataset.bumper;
            if (!rawPath) return;

            const folderName = getFolderName(rawPath);
            currentBumper = folderName;
            sessionStorage.setItem("currentBumper", currentBumper);
            
            angleIndex = 0; // パーツ変更時は正面へ
            updateState();
            await updateServerSession("bumper", currentBumper);
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

    // お気に入り
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
            }).catch(() => {});
        });
    }

    /* =================================================================
       5. UI機能 (ドロワー・パネル・フルスクリーン)
    ================================================================= */
    
    // バンパーパネル (SP/PC共通動作)
    const toggleBumperPanel = (open) => {
        if (!bumperPanel) return;
        const action = open ? 'add' : 'remove';
        bumperPanel.classList[action]("is-open", "panel-enter");
        bumperPanel.setAttribute("aria-hidden", !open);
    };

    bumperOpenBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const isOpen = bumperPanel?.classList.contains("is-open");
        toggleBumperPanel(!isOpen);
    });

    bumperPanel?.addEventListener("click", (e) => e.stopPropagation());

    // ドロワーメニュー
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
        if (bumperPanel?.classList.contains("is-open") && !bumperPanel.contains(e.target) && !bumperOpenBtn?.contains(e.target)) {
            toggleBumperPanel(false);
        }
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            toggleDrawer(false);
            toggleBumperPanel(false);
            closeFullscreen();
        }
    });

    // フルスクリーン & 画像保存 (Canvas合成)
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
            const x = w - padding;
            const y = h - padding;

            ctx.shadowColor = "rgba(0,0,0,0.7)";
            ctx.shadowBlur = 4;
            ctx.fillStyle = "#ffffff";
            ctx.fillText(text, x, y);

            canvas.toBlob(blob => {
                if(blob) {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `garelabo_bumper_${new Date().getTime()}.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
            }, "image/png");

        } catch (err) {
            alert("画像の保存に失敗しました。");
        }
    });
});