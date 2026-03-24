window.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("registerForm");

    form.addEventListener("submit", function(e) {
        e.preventDefault();

        // 入力要素
        const nickname = document.getElementById("nickname");
        const email = document.getElementById("email");
        const password = document.getElementById("password");

        // エラー表示要素
        const nicknameError = document.getElementById("nickname-error");
        const emailError = document.getElementById("email-error");
        const passwordError = document.getElementById("password-error");

        // エラー初期化
        if (nicknameError) nicknameError.textContent = "";
        if (emailError) emailError.textContent = "";
        if (passwordError) passwordError.textContent = "";

        let hasError = false;
        const halfWidthAlphaNum = /^[A-Za-z0-9]+$/;

        // ニックネーム
        if (!nickname.value.trim()) {
            if (nicknameError) nicknameError.textContent = "ニックネームを入力してください。";
            hasError = true;
        }

        // メールアドレス
        if (!email.value.trim()) {
            if (emailError) emailError.textContent = "メールアドレスを入力してください。";
            hasError = true;
        }

        // パスワード
        if (!password.value.trim()) {
            if (passwordError) passwordError.textContent = "パスワードを入力してください。";
            hasError = true;
        } else if (!halfWidthAlphaNum.test(password.value)) {
            if (passwordError) passwordError.textContent = "パスワードは半角英数字で入力してください。";
            hasError = true;
        }

        // バリデーションOKなら送信
        if (!hasError) {
            form.submit();
        }
    });

    // キャンセルボタン
    const cancelBtn = document.querySelector(".cancel");
    if (cancelBtn) {
        cancelBtn.addEventListener("click", function() {
            window.location.href = "{% url 'login' %}";
        });
    }
});