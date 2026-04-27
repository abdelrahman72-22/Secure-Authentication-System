document.getElementById("verify-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const code = document.getElementById("code").value.trim();
  const tempToken = sessionStorage.getItem("tempToken");

  if (!tempToken) {
    showMessage("status", "Login step is missing. Please login first.", true);
    return;
  }

  try {
    const data = await apiPost("/api/auth/verify-2fa", { tempToken, code });
    setAccessToken(data.accessToken);
    sessionStorage.removeItem("tempToken");
    window.location.href = "/dashboard";
  } catch (error) {
    showMessage("status", error.message, true);
  }
});
