console.log("NEW bumper.js LOADED (RESET FIX)");

document.addEventListener("DOMContentLoaded", () => {
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    const bumperBtns = document.querySelectorAll(".bumper-btn");

    if (!img) {
        console.error("car-image が見つかりません");
        return;
    }

    // ===== パスからフォルダ名だけを取り出す関数（共通） =====
    function getFolderName(path) {
        if (!path) return "";
        return String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop();
    }

    // ===== お気に入りトグル処理 =====
    const favoriteToggle = document.getElementById("favorite-toggle");
    const isFavoriteInput = document.getElementById("is-favorite");

    if (favoriteToggle && isFavoriteInput) {
        favoriteToggle.addEventListener("click", function (e) {
            e.preventDefault();
            const isCurrentlyFavorite = (isFavoriteInput.value === "true");
            const newState = !isCurrentlyFavorite;

            isFavoriteInput.value = newState ? "true" : "false";
            this.innerText = newState ? "✔ お気に入り" : "お気に入り";
            this.classList.toggle("is-favorite", newState);

            fetch("/update_session_favorite/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ is_favorite: newState }),
            }).catch((err) => console.error("通信エラー:", err));
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
    let currentColor = getFolderName(sessionStorage.getItem("currentColor")) || "white";
    let currentWheel = getFolderName(sessionStorage.getItem("currentWheel")) || "wheel1";
    let currentBumper = getFolderName(sessionStorage.getItem("currentBumper")) || "bumper1";

    // きれいになった値を保存し直す
    sessionStorage.setItem("currentColor", currentColor);
    sessionStorage.setItem("currentWheel", currentWheel);
    sessionStorage.setItem("currentBumper", currentBumper);

    let angleIndex = 0;

    // ===== 表示更新 =====
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

    // 初期表示
    updateImage();

    // ===== バンパー変更 =====
    bumperBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const bumperPath = btn.dataset.bumper;
            if (!bumperPath) return;

            currentBumper = getFolderName(bumperPath);

            angleIndex = 0;
            sessionStorage.setItem("currentBumper", currentBumper);

            console.log("バンパー変更:", currentBumper);
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

// ===== ここから追記（UI操作：メニュー/パネル/ツールチップ） =====
document.addEventListener("DOMContentLoaded", () => {
    console.log("UI controls for bumper loaded ✅");

    // ---- バンパーパネル開閉 ----
    const bumperOpenBtn = document.getElementById("open-bumper");
    const bumperPanel = document.getElementById("bumper-panel");
    const bumperPalette = document.getElementById("bumperPalette");
    const bumperValue = document.getElementById("bumperValue");

    // ---- メニュー（ドロワー） ----
    const menuBtn = document.getElementById("menu-open");
    const menuHint = document.getElementById("menu-hint");
    const overlay = document.getElementById("drawer-overlay");
    const drawer = document.getElementById("drawer");
    const closeBtn = document.getElementById("drawer-close");

    // =========================
    // バンパーパネル：開閉
    // =========================
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
        const isOpen = bumperPanel.classList.contains("is-open");
        if (isOpen) closeBumperPanel();
        else openBumperPanel();
    });

    bumperPanel?.addEventListener("click", (e) => e.stopPropagation());

    // バンパーボタン：見た目 + hidden 更新
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

    // =========================
    // メニュー（ドロワー）：開閉
    // =========================
    const openDrawer = () => {
        if (!drawer || !overlay) return;
        drawer.classList.add("is-open");
        overlay.classList.add("is-open");
        drawer.setAttribute("aria-hidden", "false");
        overlay.setAttribute("aria-hidden", "false");
        menuBtn?.setAttribute("aria-expanded", "true");
    };

    const closeDrawer = () => {
        if (!drawer || !overlay) return;
        drawer.classList.remove("is-open");
        overlay.classList.remove("is-open");
        drawer.setAttribute("aria-hidden", "true");
        overlay.setAttribute("aria-hidden", "true");
        menuBtn?.setAttribute("aria-expanded", "false");
    };

    // ドロワー内クリックで閉じない
    drawer?.addEventListener("click", (e) => e.stopPropagation());

    menuBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const isOpen = drawer && drawer.classList.contains("is-open");
        if (isOpen) closeDrawer();
        else openDrawer();
    });

    closeBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeDrawer();
    });

    overlay?.addEventListener("click", (e) => {
        e.preventDefault();
        closeDrawer();
    });

    // ツールチップ
    const showHint = () => menuHint?.setAttribute("aria-hidden", "false");
    const hideHint = () => menuHint?.setAttribute("aria-hidden", "true");

    menuBtn?.addEventListener("mouseenter", showHint);
    menuBtn?.addEventListener("mouseleave", hideHint);
    menuBtn?.addEventListener("focus", showHint);
    menuBtn?.addEventListener("blur", hideHint);

    // 外側クリックで閉じる（雑に全部閉じない）
    document.addEventListener("click", (e) => {
        const t = e.target;

        if (drawer?.classList.contains("is-open")) {
            const inDrawer = drawer.contains(t);
            const onMenuBtn = menuBtn?.contains(t);
            const onOverlay = overlay?.contains(t);
            if (!inDrawer && !onMenuBtn && !onOverlay) closeDrawer();
        }

        if (bumperPanel?.classList.contains("is-open")) {
            const inPanel = bumperPanel.contains(t);
            const onBtn = bumperOpenBtn?.contains(t);
            if (!inPanel && !onBtn) closeBumperPanel();
        }

        hideHint();
    });

    // ESCで閉じる
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeDrawer();
            closeBumperPanel();
            hideHint();
        }
    });
});

// =========================
// ✅ Fullscreen + 保存（右下GARELABO+印字 / はみ出し修正）
// =========================
document.addEventListener("DOMContentLoaded", () => {
    const carImg = document.getElementById("car-image");
    const overlay = document.getElementById("fullscreen-overlay");
    const fsImg = document.getElementById("fullscreen-image");
    const closeBtn = document.getElementById("fullscreen-close");
    const saveBtn = document.getElementById("fullscreen-save");

    if (!carImg || !overlay || !fsImg || !closeBtn) {
        console.log("fullscreen elements not found -> skip", {
            carImg: !!carImg,
            overlay: !!overlay,
            fsImg: !!fsImg,
            closeBtn: !!closeBtn,
        });
        return;
    }

    const openFullscreen = () => {
        if (!carImg.src) return;

        fsImg.src = carImg.src;

        overlay.classList.add("is-open");
        overlay.setAttribute("aria-hidden", "false");

        // ✅ CSSが display:none でも強制表示する
        overlay.style.display = "flex";
        overlay.style.position = "fixed";
        overlay.style.inset = "0";
        overlay.style.zIndex = "99999";

        document.body.style.overflow = "hidden";
    };

    const closeFullscreen = () => {
        overlay.classList.remove("is-open");
        overlay.setAttribute("aria-hidden", "true");

        overlay.style.display = "";
        overlay.style.position = "";
        overlay.style.inset = "";
        overlay.style.zIndex = "";

        document.body.style.overflow = "";
    };

    // 画像クリック取りこぼし対策：枠ごと拾う
    const frame = carImg.closest(".car-frame");
    frame?.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openFullscreen();
    });

    carImg.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openFullscreen();
    });

    closeBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeFullscreen();
    });

    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeFullscreen();
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && overlay.classList.contains("is-open")) {
            closeFullscreen();
        }
    });

    // ✅ 保存：右下に "GARELABO+" を印字してダウンロード
    if (saveBtn) {
        saveBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();

            try {
                if (!fsImg.src) return;

                // 1) 画像を取得
                const res = await fetch(fsImg.src, { cache: "no-store" });
                if (!res.ok) {
                    console.error("画像取得失敗:", res.status);
                    return;
                }
                const blob = await res.blob();

                // 2) Blob -> Image -> Canvas
                const imgUrl = URL.createObjectURL(blob);
                const tempImg = new Image();
                tempImg.decoding = "async";
                tempImg.crossOrigin = "anonymous";

                tempImg.onload = () => {
                    try {
                        const w = tempImg.naturalWidth || tempImg.width;
                        const h = tempImg.naturalHeight || tempImg.height;

                        const canvas = document.createElement("canvas");
                        canvas.width = w;
                        canvas.height = h;

                        const ctx = canvas.getContext("2d");
                        if (!ctx) {
                            URL.revokeObjectURL(imgUrl);
                            return;
                        }

                        // 元画像
                        ctx.drawImage(tempImg, 0, 0, w, h);

                        // 3) 右下ウォーターマーク（はみ出さない版）
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

                        // ✅ 右端基準（背景込みで確実に収める）
                        const xText = w - pad - bgPadX;
                        const yText = h - pad - bgPadY;

                        const bgW = textW + bgPadX * 2;
                        const bgH = textH + bgPadY * 2;

                        const bgX = xText - textW - bgPadX;
                        const bgY = yText - textH - bgPadY;

                        // 背景（角丸）
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

                        // 文字（白 + 影）
                        ctx.save();
                        ctx.fillStyle = "#fff";
                        ctx.shadowColor = "rgba(0,0,0,0.6)";
                        ctx.shadowBlur = Math.round(fontSize * 0.25);
                        ctx.shadowOffsetX = 0;
                        ctx.shadowOffsetY = Math.round(fontSize * 0.08);
                        ctx.fillText(text, xText, yText);
                        ctx.restore();

                        // 4) Canvas -> Blob -> Download
                        canvas.toBlob((outBlob) => {
                            try {
                                if (!outBlob) return;

                                const outUrl = URL.createObjectURL(outBlob);
                                const a = document.createElement("a");
                                a.href = outUrl;
                                a.download = "garelabo_custom.png";
                                document.body.appendChild(a);
                                a.click();
                                a.remove();
                                URL.revokeObjectURL(outUrl);
                            } finally {
                                URL.revokeObjectURL(imgUrl);
                            }
                        }, "image/png");
                    } catch (err) {
                        console.error("合成保存失敗:", err);
                        URL.revokeObjectURL(imgUrl);
                    }
                };

                tempImg.onerror = () => {
                    console.error("画像読み込み失敗");
                    URL.revokeObjectURL(imgUrl);
                };

                tempImg.src = imgUrl;
            } catch (err) {
                console.error("画像保存失敗:", err);
            }
        });
    }
});
