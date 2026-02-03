console.log("NEW bodycolor.js LOADED (INTEGRATED)");

document.addEventListener("DOMContentLoaded", () => {
    /* =================================================================
       1. 要素の取得 & ヘルパー関数
    ================================================================= */
    const img = document.getElementById("car-image");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    
    // 隠しフィールドから基本情報を取得
    const currentVehicleIdInput = document.getElementById('current-vehicle-id');
    const currentVehicleId = currentVehicleIdInput ? currentVehicleIdInput.value : null;
    
    // 自動カスタムリンク
    const autoLink = document.getElementById('auto-custom-link');

    if (!img) {
        console.error("car-image が見つかりません");
        return;
    }

    /**
     * パスからフォルダ名（最後の要素）を取得する
     * 拡張子(.png等)がついている場合は除去する
     */
    function getFolderName(path) {
        if (!path) return "";
        // パス区切りを統一し、最後の要素を取得
        let name = String(path).replace(/\\/g, "/").split("/").filter(Boolean).pop();
        // 拡張子除去
        return name.replace(/\.[^/.]+$/, "");
    }

    /**
     * CSRFトークン取得
     */
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

    /**
     * 画像ロード失敗時のフォールバック処理
     */
    function setSrcWithFallback(imgEl, urls) {
        let i = 0;
        imgEl.onerror = () => {
            i++;
            if (i < urls.length) {
                console.warn(`画像読み込み失敗、次を試行: ${urls[i]}`);
                imgEl.src = urls[i];
            } else {
                imgEl.onerror = null;
                console.error("全ての画像候補が見つかりませんでした", urls);
            }
        };
        imgEl.src = urls[0];
    }

    /* =================================================================
       2. 初期化 & リセットロジック (Base機能)
    ================================================================= */
    const params = new URLSearchParams(window.location.search);
    const resetParam = params.get("reset");
    const urlCar = params.get("car");
    
    // サーバーからの初期値（HTML内のhidden input）
    const serverCar = document.getElementById("server-car-folder")?.value;
    const serverColor = document.getElementById("server-color-folder")?.value;
    const serverWheel = document.getElementById("server-wheel-folder")?.value;
    const serverBumper = document.getElementById("server-bumper-folder")?.value;

    const storedCar = sessionStorage.getItem("selectedCar");

    // リセット条件: URLパラメータ reset=true または 車種変更時
    if (resetParam === "true" || (urlCar && storedCar && urlCar !== storedCar)) {
        console.log("リセット実行: セッションストレージをクリア");
        sessionStorage.removeItem("currentColor");
        sessionStorage.removeItem("currentWheel");
        sessionStorage.removeItem("currentBumper");
        
        if (urlCar) {
            sessionStorage.setItem("selectedCar", urlCar);
        }

        // URLからresetパラメータを削除
        if (resetParam === "true") {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete("reset");
            window.history.replaceState(null, "", newUrl);
        }
    }

    // 現在のステートを確定
    let carFolder = urlCar || sessionStorage.getItem("selectedCar");
    if (!carFolder && serverCar) carFolder = getFolderName(serverCar);
    
    if (!carFolder) {
        // フォールバック
        carFolder = "CompactSedan"; 
    }
    sessionStorage.setItem("selectedCar", carFolder);

    // 各パーツの初期値決定 (セッション > サーバー値 > デフォルト)
    const initPart = (key, serverVal, defaultVal) => {
        if (!sessionStorage.getItem(key)) {
            const val = getFolderName(serverVal) || defaultVal;
            sessionStorage.setItem(key, val);
        }
        return sessionStorage.getItem(key);
    };

    let currentColor = initPart("currentColor", serverColor, "white");
    let currentWheel = initPart("currentWheel", serverWheel, "wheel1");
    let currentBumper = initPart("currentBumper", serverBumper, "normal");

    // 角度管理
    const angles = ["front", "side_right", "rear", "side_left"];
    let angleIndex = 0;

    /* =================================================================
       3. 表示更新 & サーバー同期
    ================================================================= */
    
    /**
     * 画像とリンクの更新
     */
    function updateState() {
        // 1. 画像更新
        const c = currentColor;
        const w = currentWheel;
        const b = currentBumper;
        const angle = angles[angleIndex];

        // 画像パスの候補を作成 (バンパー有無や階層の違いに対応)
        let urls = [];
        
        // パターンA: 標準的なフルパス
        if (b && b !== "normal") {
            urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${b}/${angle}.png`);
        }
        // パターンB: バンパーなし(normal) or 階層省略
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${w}/${angle}.png`);
        // パターンC: ホイール省略 (念のため)
        urls.push(`/media/uploads/vehicles/${carFolder}/${c}/${angle}.png`);

        setSrcWithFallback(img, urls);
        img.alt = `${carFolder} ${c} ${w} ${b} ${angle}`;

        // 2. チップの選択状態更新
        document.querySelectorAll('.garelabo-palette__chip, .color-dot').forEach(btn => {
            const btnColor = getFolderName(btn.dataset.color);
            btn.classList.toggle('is-selected', btnColor === currentColor);
        });

        // 3. 自動カスタムリンクの更新
        updateAutoCustomLink();
    }

    /**
     * 自動カスタムボタンのリンク先パラメータを更新
     */
    function updateAutoCustomLink() {
        if (!autoLink) return;
        const url = new URL(autoLink.href, window.location.origin);
        
        if (currentVehicleId) {
            url.searchParams.set('vehicle_id', currentVehicleId);
        }
        
        url.searchParams.set('color', currentColor);
        url.searchParams.set('wheel', currentWheel);
        // バンパーが normal の場合はパラメータを含めない、または明示する（サーバー側の仕様に合わせる）
        if (currentBumper && currentBumper !== "normal") {
            url.searchParams.set('bumper', currentBumper);
        } else {
            url.searchParams.delete('bumper');
        }

        autoLink.href = url.toString();
    }

    /**
     * サーバーセッションの非同期更新
     */
    async function updateServerSession(type, value) {
        try {
            const response = await fetch('/update_session_selection/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ type: type, value: value })
            });
            if (!response.ok) throw new Error("Network response was not ok");
            console.log(`Session Synced: ${type} = ${value}`);
        } catch (e) {
            console.error("Session sync failed:", e);
        }
    }

    // 初回表示反映
    updateState();

    /* =================================================================
       4. イベントリスナー (パーツ操作)
    ================================================================= */
    
    // カラー・ホイール・バンパーボタンの共通ハンドラ
    // (bodycolorページにはカラーしかありませんが、将来的な拡張や共通化に対応)
    const partBtns = document.querySelectorAll(".garelabo-palette__chip, .color-dot, .wheel-btn, .bumper-btn");
    
    partBtns.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            
            // データ属性からパスまたは名前を取得
            const rawPath = btn.dataset.color || btn.dataset.wheel || btn.dataset.bumper;
            if (!rawPath) return;

            const folderName = getFolderName(rawPath);
            
            // ボタンの種類を判定
            let type = "color"; // デフォルト
            if (btn.dataset.wheel || btn.classList.contains("wheel-btn")) type = "wheel";
            if (btn.dataset.bumper || btn.classList.contains("bumper-btn")) type = "bumper";

            // 状態更新
            if (type === "color") {
                currentColor = folderName;
                sessionStorage.setItem("currentColor", currentColor);
                angleIndex = 0; // 色変更時は正面に戻すのが一般的
            } else if (type === "wheel") {
                currentWheel = folderName;
                sessionStorage.setItem("currentWheel", currentWheel);
            } else if (type === "bumper") {
                currentBumper = folderName;
                sessionStorage.setItem("currentBumper", currentBumper);
            }

            // 画面反映
            updateState();

            // サーバー同期
            await updateServerSession(type, folderName);
        });
    });

    // 回転ボタン
    prevBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex - 1 + angles.length) % angles.length;
        updateState();
    });
    nextBtn?.addEventListener("click", () => {
        angleIndex = (angleIndex + 1) % angles.length;
        updateState();
    });

    // お気に入り登録
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
                headers: {
                    "X-CSRFToken": getCookie('csrftoken'),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ is_favorite: newState }),
                keepalive: true,
            }).catch((err) => console.error("通信エラー:", err));
        });
    }

    /* =================================================================
       5. UI機能 (ドロワー・フルスクリーン)
    ================================================================= */
    
    // --- ドロワーメニュー ---
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

    // --- ボディカラーパネル (SP用) ---
    const bodyBtn = document.getElementById("open-bodycolor");
    const bodyPanel = document.getElementById("bodycolor-panel");
    if (bodyBtn && bodyPanel) {
        bodyBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            bodyPanel.classList.toggle("is-open");
            bodyPanel.setAttribute("aria-hidden", !bodyPanel.classList.contains("is-open"));
        });
        bodyPanel.addEventListener("click", (e) => e.stopPropagation());
    }

    // --- エスケープキーで閉じる ---
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            toggleDrawer(false);
            if (bodyPanel?.classList.contains("is-open")) {
                bodyPanel.classList.remove("is-open");
            }
            closeFullscreen();
        }
    });

    // --- フルスクリーン & 画像保存 ---
    const fsOverlay = document.getElementById("fullscreen-overlay");
    const fsImage = document.getElementById("fullscreen-image");
    const fsClose = document.getElementById("fullscreen-close");
    const fsSave = document.getElementById("fullscreen-save");

    const openFullscreen = () => {
        if (!img.src || !fsOverlay) return;
        fsImage.src = img.src;
        fsOverlay.classList.add("is-open");
        fsOverlay.setAttribute("aria-hidden", "false");
        fsOverlay.style.display = "flex"; // CSSがない場合の保険
        document.body.style.overflow = "hidden";
    };

    const closeFullscreen = () => {
        if (!fsOverlay) return;
        fsOverlay.classList.remove("is-open");
        fsOverlay.setAttribute("aria-hidden", "true");
        fsOverlay.style.display = "";
        document.body.style.overflow = "";
    };

    // 画像クリックまたは枠クリックでフルスクリーン
    img.addEventListener("click", (e) => { e.stopPropagation(); openFullscreen(); });
    img.closest(".car-frame")?.addEventListener("click", (e) => { e.preventDefault(); openFullscreen(); });
    
    fsClose?.addEventListener("click", closeFullscreen);
    fsOverlay?.addEventListener("click", (e) => {
        if (e.target === fsOverlay) closeFullscreen();
    });

    // --- 画像保存機能 (Canvas合成) ---
    fsSave?.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (!fsImage.src) return;

        try {
            // 画像読み込み完了を待機
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

            // 車を描画
            ctx.drawImage(fsImage, 0, 0, w, h);

            // GARELABO+ ロゴ描画
            const text = "GARELABO+";
            const fontSize = Math.max(20, Math.round(w * 0.04));
            ctx.font = `bold ${fontSize}px sans-serif`;
            ctx.textAlign = "right";
            ctx.textBaseline = "bottom";
            
            const padding = Math.round(fontSize * 0.5);
            const x = w - padding;
            const y = h - padding;

            // 文字の影 (視認性向上)
            ctx.shadowColor = "rgba(0,0,0,0.7)";
            ctx.shadowBlur = 4;
            ctx.fillStyle = "#ffffff";
            ctx.fillText(text, x, y);

            // ダウンロード処理
            canvas.toBlob(blob => {
                if(blob) {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `garelabo_custom_${new Date().getTime()}.png`;
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