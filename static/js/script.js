document.getElementById("registerForm").addEventListener("submit", function (e) {
    e.preventDefault();

    // 各要素
    const nickname = document.getElementById("nickname");
    const email = document.getElementById("email");
    const password = document.getElementById("password");

    // エラーメッセージ要素
    const nicknameError = document.getElementById("nickname-error");
    const emailError = document.getElementById("email-error");
    const passwordError = document.getElementById("password-error");

    // エラー初期化
    nicknameError.style.display = "none";
    emailError.style.display = "none";
    passwordError.style.display = "none";

    let hasError = false;

    // 半角英数字の正規表現
    const halfWidthAlphaNum = /^[A-Za-z0-9]+$/;

    // ニックネーム
    if (nickname.value.trim() === "") {
        nicknameError.textContent ="ニックネームを入力してください。";
        nicknameError.style.display = "block";
        hasError = true;
    }

    // メールアドレス
    if (email.value.trim() === "") {
        emailError.textContent = "メールアドレスを入力してください。";
        emailError.style.display = "block";
        hasError = true;
    } 

    // パスワード
    if (password.value.trim() === "") {
        passwordError.textContent = "パスワードを入力してください。";
        passwordError.style.display = "block";
        hasError = true;
    } else if (!halfWidthAlphaNum.test(password.value)) {
        passwordError.textContent = "パスワードは半角英数字で入力してください。";
        passwordError.style.display = "block";
        hasError = true;
    }

    // エラーがなければフォーム送信
    if (!hasError) {
        this.submit();
    }
});