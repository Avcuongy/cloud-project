document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page !== "login") return;

  const form = document.getElementById("login-form");
  const userNameInput = document.getElementById("user-name");
  const passwordInput = document.getElementById("password");

  if (!form || !userNameInput || !passwordInput) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const userName = userNameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!userName || !password) {
      showToast("Vui lòng nhập tài khoản và mật khẩu");
      return;
    }

    try {
      await apiSend("/api/login", "POST", {
        userName,
        password,
      });
      window.location.href = "/dashboard";
    } catch (err) {
      console.error(err);
      showToast(err.message || "Đăng nhập thất bại");
    }
  });

  userNameInput.focus();
});
