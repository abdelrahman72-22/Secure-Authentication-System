document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const identifier = document.getElementById("identifier").value.trim();
  const password = document.getElementById("password").value;

  try {
    const data = await apiPost("/api/auth/login", { identifier, password });
    sessionStorage.setItem("tempToken", data.tempToken);
    window.location.href = "/verify-2fa";
  } catch (error) {
    showMessage("status", error.message, true);
  }
});
