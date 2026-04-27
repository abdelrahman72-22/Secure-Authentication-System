function setupNav() {
  document.querySelectorAll("[data-logout]").forEach((btn) => {
    btn.addEventListener("click", () => {
      clearAuthState();
      window.location.href = "/login";
    });
  });
}

async function bootProtectedPage() {
  setupNav();
  const content = document.getElementById("content");
  const route = content.dataset.route;
  const requiredRole = content.dataset.requiredRole;

  try {
    const dashboard = await apiGetProtected("/api/dashboard");
    if (requiredRole && dashboard.user.role !== requiredRole) {
      throw new Error(`Forbidden: page requires ${requiredRole} role`);
    }

    const data = await apiGetProtected(route);
    document.getElementById("whoami").textContent = `${dashboard.user.name} (${dashboard.user.role})`;
    document.getElementById("api-response").textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    if (error.message.toLowerCase().includes("token") || error.message.toLowerCase().includes("unauthorized")) {
      clearAuthState();
      window.location.href = "/login";
      return;
    }
    showMessage("status", error.message, true);
  }
}

bootProtectedPage();
