// ================================================================
// アカウント編集ページ専用 script.js（完全新規版）
// ================================================================

window.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");
  if (!form) {
    return;
  }

  form.addEventListener("submit", function (e) {
    // e.preventDefault();

    // 入力要素の取得
    const nickname = document.getElementById("nickname");
    // const email = document.getElementById("email");
    const password = document.getElementById("password");

    // エラー表示用要素
    const nicknameError = document.getElementById("nickname-error");
    // const emailError = document.getElementById("email-error");
    const passwordError = document.getElementById("password-error");

    // 事前エラーリセット
    nicknameError.textContent = "";
    // emailError.textContent = "";
    passwordError.textContent = "";

    let hasError = false;
    const halfWidthAlphaNum = /^[A-Za-z0-9]+$/;

    // ------------------------
    // 各項目バリデーション
    // ------------------------

    if (!nickname.value.trim()) {
      nicknameError.textContent = "ニックネームを入力してください。";
      hasError = true;
    }

    if (!password.value.trim()) {
      passwordError.textContent = "パスワードを入力してください。";
      hasError = true;
    } else if (!halfWidthAlphaNum.test(password.value)) {
      passwordError.textContent = "パスワードは半角英数字で入力してください。";
      hasError = true;
    }

    // ------------------------
    // バリデーション成功 → 送信
    // ------------------------

    if (hasError) {
      e.preventDefault();
    }
  });
});