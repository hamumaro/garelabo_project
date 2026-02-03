console.log("NEW wheel.js LOADED (RESET FIX)");

document.addEventListener("DOMContentLoaded", () => {
    /* =========================
       基本：画像表示（回転/選択）
    ========================= */
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    const wheelBtns = document.querySelectorAll(".wheel-btn");

    if (!img) {
        console.error("car-image が見つかりません");
        return;
    }

    /* =========================
       共通：フォルダ名抽出
    ========================= */
    function getFolderName(path) {
        if (!path) return "";
        const v = String(path).replace(/\\/g, "/").split("/").filter(Boolean);
        return v.length ? v[v.length - 1] : "";
    }

    /* =========================
       サーバーセッション更新
       - views.py の update_session_parts は
         vehicle_id/color_id... を期待してる版もあるので、
         ここでは part_type + folder_name を送る（あなたのJS仕様）
         ※サーバ側が別仕様なら views.py 側も合わせる必要あり
    ========================= */
    function updateServerSession(partType, folderName) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) return;

        fetch("/update_session_parts/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ part_type: partType, folder_name: folderName }),
            keepalive: true,
        }).catch((err) => console.error("Session update error:", err));
    }

    /* =========================
       サーバ初期値（hidden input）
    ========================= */
    const serverCar = document.getElementById("server-car-folder")?.value;
    const serverColor = document.getElementById("server-color-folder")?.value;
    const serverWheel = document.getElementById("server-wheel-folder")?.value;
    const serverBumper = document.getElementById("server-bumper-folder")?.value;

    /* =========================
       1. 初期値の決定とリセット処理
    ========================= */
    const params = new URLSearchParams(window.location.search);
    const resetParam = params.get("reset");
    const urlCar = params.get("car");
    const storedCar = sessionStorage.getItem("selectedCar");

    // reset=true もしくは URL車種が変わったら、パーツ選択をクリア
    if (resetParam === "true" || (urlCar && storedCar && urlCar !== storedCar)) {
        console.log("リセット要求を検知: セッションストレージをクリアします");

        sessionStorage.removeItem("currentColor");
        sessionStorage.removeItem("currentWheel");
        sessionStorage.removeItem("currentBumper");

        if (urlCar) {
            sessionStorage.setItem("selectedCar", urlCar);
        }

        if (resetParam === "true") {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete("reset");
            window.history.replaceState(null, "", newUrl);
        }
    }

    // 車フォルダ確定（URL > sessionStorage > server）
    let carFolder = urlCar;
    if (!carFolder) carFolder = sessionStorage.getItem("selectedCar");
    if (!carFolder && serverCar) carFolder = getFolderName(serverCar);

    if (!carFolder) {
        console.error("車情報(car)が取得できません");
        return;
    }
    sessionStorage.setItem("selectedCar", carFolder);

    // 初回だけ server 値で埋める（sessionStorage が空なら）
    if (serverColor && !sessionStorage.getItem("currentColor")) {
        sessionStorage.setItem("currentColor", getFolderName(serverColor));
    }
    if (serverWheel && !sessionStorage.getItem("currentWheel")) {
        sessionStorage.setItem("currentWheel", getFolderName(serverWheel));
    }
    if (serverBumper && !sessionStorage.getItem("currentBumper")) {
        sessionStorage.setItem("currentBumper", getFolderName(serverBumper));
    }

    // 現在値
    let currentColor = getFolderName(sessionStorage.getItem("currentColor")) || "white";
    let currentWheel = getFolderName(sessionStorage.getItem("currentWheel")) || "wheel1";
    let currentBumper = getFolderName(sessionStorage.getItem("currentBumper")) || "bumper1";

    sessionStorage.setItem("currentColor", currentColor);
    sessionStorage.setItem("currentWheel", currentWheel);
    sessionStorage.setItem("currentBumper", currentBumper);

    /* =========================
       回転角度
       ※あなたの構成に合わせて 4方向
    ========================= */
    const angles = ["front", "side_right", "rear", "side_left"];
    let angleIndex = 0;

    /* =========================
       画像更新
    ========================= */
    function updateImage() {
        const cleanColor = getFolderName(currentColor) || "white";
        const cleanWheel = getFolderName(currentWheel) || "wheel1";
        const cleanBumper = getFolderName(currentBumper) || "bumper1";

        const path =
            `/media/uploads/vehicles/${carFolder}` +
            `/${cleanColor}/${cleanWheel}/${cleanBumper}/${angles[angleIndex]}.png`;

        img.src = path;
        img.alt = `${carFolder} ${cleanColor} ${cleanWheel} ${cleanBumper} ${angles[angleIndex]}`;

        console.log("表示中:", {
            car: carFolder,
            color: cleanColor,
            wheel: cleanWheel,
            bumper: cleanBumper,
            angle: angles[angleIndex],
        });
    }

    updateImage();

    /* =========================
       ホイール変更
    ========================= */
    wheelBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const wheelPath = btn.dataset.wheel || btn.dataset.value;
            if (!wheelPath) return;

            currentWheel = getFolderName(wheelPath);
            sessionStorage.setItem("currentWheel", currentWheel);

            angleIndex = 0;

            // サーバーへ通知
            updateServerSession("wheel", currentWheel);

            console.log("ホイール変更:", currentWheel);
            updateImage();
        });
    });

    /* =========================
       回転
    ========================= */
    prevBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex - 1 + angles.length) % angles.length;
        updateImage();
    });

    nextBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex + 1) % angles.length;
        updateImage();
    });

    /* =========================
       お気に入りトグル
       ※二重登録しないようにここで1回だけ
    ========================= */
    const favoriteToggle = document.getElementById("favorite-toggle");
    const isFavoriteInput = document.getElementById("is-favorite");

    if (favoriteToggle && isFavoriteInput) {
        favoriteToggle.addEventListener("click", (e) => {
            e.preventDefault();

            const isCurrentlyFavorite = (isFavoriteInput.value === "true");
            const newState = !isCurrentlyFavorite;

            isFavoriteInput.value = newState ? "true" : "false";
            favoriteToggle.innerText = newState ? "✔ お気に入り" : "お気に入り";
            favoriteToggle.classList.toggle("is-favorite", newState);

            const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
            if (!csrf) return;

            fetch("/update_session_favorite/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ is_favorite: newState }),
                keepalive: true,
            }).catch((err) => console.error("通信エラー:", err));
        });
    }

    /* =========================
       UI：パネル/ドロワー（既存に合わせる）
    ========================= */
    const bumperOpenBtn = document.getElementById("open-bumper");
    const bumperPanel = document.getElementById("bumper-panel");
    const bumperPalette = document.getElementById("bumperPalette");
    const bumperValue = document.getElementById("bumperValue");

    const wheelOpenBtn = document.getElementById("open-wheel");
    const wheelPanel = document.getElementById("wheel-panel");
    const wheelPalette = document.getElementById("wheelPalette");
    const wheelValue = document.getElementById("wheelValue");

    const menuBtn = document.getElementById("menu-open");
    const menuHint = document.getElementById("menu-hint");
    const drawerOverlay = document.getElementById("drawer-overlay");
    const drawer = document.getElementById("drawer");
    const drawerCloseBtn = document.getElementById("drawer-close");

    // バンパーパネル
    const openBumperPanel = () => {
        if (!bumperPanel) return;
        bumperPanel.classList.add("is-open", "panel-enter");
        bumperPanel.setAttribute("aria-hidden", "false");
    };
    const closeBumperPanel = () => {
        if (!bumperPanel) return;
        bumperPanel.classList.remove("is-open", "panel-enter");
        bumperPanel.setAttribute("aria-hidden", "true");
    };

    bumperOpenBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!bumperPanel) return;

        if (bumperPanel.classList.contains("is-open")) closeBumperPanel();
        else openBumperPanel();
    });

    bumperPanel?.addEventListener("click", (e) => e.stopPropagation());

    bumperPalette?.addEventListener("click", (e) => {
        e.stopPropagation();
        const btn = e.target.closest(".bumper-btn");
        if (!btn) return;

        const bumper = btn.dataset.bumper;
        if (!bumper) return;

        bumperPalette.querySelectorAll(".bumper-btn").forEach((b) => b.classList.remove("is-selected"));
        btn.classList.add("is-selected");
        if (bumperValue) bumperValue.value = bumper;
    });

    // ホイールパネル
    const openWheelPanel = () => {
        if (!wheelPanel) return;
        wheelPanel.classList.add("is-open", "panel-enter");
        wheelPanel.setAttribute("aria-hidden", "false");
    };
    const closeWheelPanel = () => {
        if (!wheelPanel) return;
        wheelPanel.classList.remove("is-open", "panel-enter");
        wheelPanel.setAttribute("aria-hidden", "true");
    };

    wheelOpenBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!wheelPanel) return;

        if (wheelPanel.classList.contains("is-open")) closeWheelPanel();
        else openWheelPanel();
    });

    wheelPanel?.addEventListener("click", (e) => e.stopPropagation());

    wheelPalette?.addEventListener("click", (e) => {
        e.stopPropagation();
        const btn = e.target.closest(".wheel-btn");
        if (!btn) return;

        const wheelRaw = btn.dataset.wheel || btn.dataset.value;
        if (!wheelRaw) return;

        wheelPalette.querySelectorAll(".wheel-btn").forEach((b) => b.classList.remove("is-selected"));
        btn.classList.add("is-selected");
        if (wheelValue) wheelValue.value = wheelRaw;
    });

    // ドロワー
    const openDrawer = () => {
        if (!drawer || !drawerOverlay) return;
        drawer.classList.add("is-open");
        drawerOverlay.classList.add("is-open");
        drawer.setAttribute("aria-hidden", "false");
        drawerOverlay.setAttribute("aria-hidden", "false");
        menuBtn?.setAttribute("aria-expanded", "true");
    };

    const closeDrawer = () => {
        if (!drawer || !drawerOverlay) return;
        drawer.classList.remove("is-open");
        drawerOverlay.classList.remove("is-open");
        drawer.setAttribute("aria-hidden", "true");
        drawerOverlay.setAttribute("aria-hidden", "true");
        menuBtn?.setAttribute("aria-expanded", "false");
    };

    menuBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (drawer?.classList.contains("is-open")) closeDrawer();
        else openDrawer();
    });

    drawer?.addEventListener("click", (e) => e.stopPropagation());

    drawerCloseBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeDrawer();
    });

    drawerOverlay?.addEventListener("click", (e) => {
        e.preventDefault();
        closeDrawer();
    });

    const showHint = () => menuHint?.setAttribute("aria-hidden", "false");
    const hideHint = () => menuHint?.setAttribute("aria-hidden", "true");

    menuBtn?.addEventListener("mouseenter", showHint);
    menuBtn?.addEventListener("mouseleave", hideHint);
    menuBtn?.addEventListener("focus", showHint);
    menuBtn?.addEventListener("blur", hideHint);

    document.addEventListener("click", (e) => {
        const t = e.target;

        if (drawer?.classList.contains("is-open")) {
            const inDrawer = drawer.contains(t);
            const onMenuBtn = menuBtn?.contains(t);
            const onOverlay = drawerOverlay?.contains(t);
            if (!inDrawer && !onMenuBtn && !onOverlay) closeDrawer();
        }

        if (bumperPanel?.classList.contains("is-open")) {
            const inPanel = bumperPanel.contains(t);
            const onBtn = bumperOpenBtn?.contains(t);
            if (!inPanel && !onBtn) closeBumperPanel();
        }

        if (wheelPanel?.classList.contains("is-open")) {
            const inPanel = wheelPanel.contains(t);
            const onBtn = wheelOpenBtn?.contains(t);
            if (!inPanel && !onBtn) closeWheelPanel();
        }

        hideHint();
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeDrawer();
            closeBumperPanel();
            closeWheelPanel();
            hideHint();
        }
    });

    /* =========================
       Fullscreen（強制表示 + 保存時に右下GARELABO+）
    ========================= */
    const fullscreenOverlay = document.getElementById("fullscreen-overlay");
    const fullscreenImage = document.getElementById("fullscreen-image");
    const fullscreenClose = document.getElementById("fullscreen-close");
    const fullscreenSave = document.getElementById("fullscreen-save");

    if (!fullscreenOverlay || !fullscreenImage || !fullscreenClose) {
        console.log("fullscreen elements not found -> skip", {
            fullscreenOverlay: !!fullscreenOverlay,
            fullscreenImage: !!fullscreenImage,
            fullscreenClose: !!fullscreenClose,
        });
        return;
    }

    const openFullscreen = () => {
        if (!img.src) return;

        fullscreenImage.src = img.src;

        fullscreenOverlay.classList.add("is-open");
        fullscreenOverlay.setAttribute("aria-hidden", "false");

        fullscreenOverlay.style.display = "flex";
        fullscreenOverlay.style.alignItems = "center";
        fullscreenOverlay.style.justifyContent = "center";
        fullscreenOverlay.style.position = "fixed";
        fullscreenOverlay.style.inset = "0";
        fullscreenOverlay.style.zIndex = "99999";

        document.body.style.overflow = "hidden";
        console.log("fullscreen OPEN", { src: fullscreenImage.src });
    };

    const closeFullscreen = () => {
        fullscreenOverlay.classList.remove("is-open");
        fullscreenOverlay.setAttribute("aria-hidden", "true");

        fullscreenOverlay.style.display = "";
        fullscreenOverlay.style.alignItems = "";
        fullscreenOverlay.style.justifyContent = "";
        fullscreenOverlay.style.position = "";
        fullscreenOverlay.style.inset = "";
        fullscreenOverlay.style.zIndex = "";

        document.body.style.overflow = "";
        console.log("fullscreen CLOSE");
    };

    const frame = img.closest(".car-frame");
    frame?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openFullscreen();
    });

    img.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openFullscreen();
    });

    fullscreenClose.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeFullscreen();
    });

    fullscreenOverlay.addEventListener("click", (e) => {
        if (e.target === fullscreenOverlay) closeFullscreen();
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && fullscreenOverlay.classList.contains("is-open")) {
            closeFullscreen();
        }
    });

    // ✅ 保存：fullscreenImageをcanvasへ描画し右下にGARELABO+
    fullscreenSave?.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();

        try {
            if (!fullscreenImage.src) {
                console.error("fullscreenImage.src が空です");
                return;
            }

            // 画像ロード待ち
            if (!fullscreenImage.complete || fullscreenImage.naturalWidth === 0) {
                await new Promise((resolve, reject) => {
                    const t = setTimeout(() => reject(new Error("image load timeout")), 4000);
                    fullscreenImage.onload = () => {
                        clearTimeout(t);
                        resolve();
                    };
                    fullscreenImage.onerror = () => {
                        clearTimeout(t);
                        reject(new Error("image load error"));
                    };
                });
            }

            const w = fullscreenImage.naturalWidth;
            const h = fullscreenImage.naturalHeight;

            const canvas = document.createElement("canvas");
            canvas.width = w;
            canvas.height = h;

            const ctx = canvas.getContext("2d");
            if (!ctx) return;

            ctx.drawImage(fullscreenImage, 0, 0, w, h);

            const text = "GARELABO+";

            const fontSize = Math.max(22, Math.round(w * 0.035));
            const bgPadX = Math.round(fontSize * 0.6);
            const bgPadY = Math.round(fontSize * 0.45);
            const pad = Math.max(10, Math.round(fontSize * 0.6));

            ctx.font = `700 ${fontSize}px "Noto Sans JP", system-ui, sans-serif`;
            ctx.textBaseline = "bottom";
            ctx.textAlign = "right";

            const metrics = ctx.measureText(text);
            const textW = Math.ceil(metrics.width);
            const textH = fontSize;

            const xText = w - pad - bgPadX;
            const yText = h - pad - bgPadY;

            const bgW = textW + bgPadX * 2;
            const bgH = textH + bgPadY * 2;

            const bgX = xText - textW - bgPadX;
            const bgY = yText - textH - bgPadY;

            const r = Math.round(fontSize * 0.35);
            ctx.save();
            ctx.globalAlpha = 0.55;
            ctx.fillStyle = "#000";
            ctx.beginPath();
            ctx.moveTo(bgX + r, bgY);
            ctx.lineTo(bgX + bgW - r, bgY);
            ctx.quadraticCurveTo(bgX + bgW, bgY, bgX + bgW, bgY + r);
            ctx.lineTo(bgX + bgW, bgY + bgH - r);
            ctx.quadraticCurveTo(bgX + bgW, bgY + bgH, bgX + bgW - r, bgY + bgH);
            ctx.lineTo(bgX + r, bgY + bgH);
            ctx.quadraticCurveTo(bgX, bgY + bgH, bgX, bgY + bgH - r);
            ctx.lineTo(bgX, bgY + r);
            ctx.quadraticCurveTo(bgX, bgY, bgX + r, bgY);
            ctx.closePath();
            ctx.fill();
            ctx.restore();

            ctx.save();
            ctx.fillStyle = "#fff";
            ctx.shadowColor = "rgba(0,0,0,0.6)";
            ctx.shadowBlur = Math.round(fontSize * 0.25);
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = Math.round(fontSize * 0.08);
            ctx.fillText(text, xText, yText);
            ctx.restore();

            canvas.toBlob((outBlob) => {
                if (!outBlob) {
                    console.error("toBlob失敗（canvasが汚染扱いの可能性）");
                    return;
                }

                const outUrl = URL.createObjectURL(outBlob);
                const a = document.createElement("a");
                a.href = outUrl;
                a.download = "garelabo_custom.png";
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(outUrl);
            }, "image/png");
        } catch (err) {
            console.error("画像保存失敗:", err);
        }
    });
});
