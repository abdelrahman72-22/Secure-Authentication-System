document.getElementById("register-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.getElementById("name").value.trim();
  const identifier = document.getElementById("identifier").value.trim();
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;

  try {
    const data = await apiPost("/api/auth/register", {
      name,
      identifier,
      password,
      role,
    });

    showMessage("status", data.message);
    document.getElementById("qr-code").src = data.qrCodeDataUrl;
    document.getElementById("manual-secret").textContent = data.manualSecret;
  } catch (error) {
    showMessage("status", error.message, true);
  }
});
