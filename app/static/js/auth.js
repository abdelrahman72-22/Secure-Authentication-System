function setAccessToken(token) {
  localStorage.setItem("accessToken", token);
}

function getAccessToken() {
  return localStorage.getItem("accessToken");
}

function clearAuthState() {
  localStorage.removeItem("accessToken");
  sessionStorage.removeItem("tempToken");
}

async function apiPost(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

async function apiGetProtected(url) {
  const token = getAccessToken();
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Unauthorized");
  }

  return data;
}

function showMessage(targetId, text, isError = false) {
  const el = document.getElementById(targetId);
  el.className = isError ? "error" : "notice";
  el.textContent = text;
}
