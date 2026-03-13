// Shared helpers for all pages
const STORAGE_KEYS = {
  selection: "cloud_selected_ids",
};

function showToast(message) {
  const toastEl = document.getElementById("toast");
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.classList.remove("hidden");
  setTimeout(() => {
    toastEl.classList.add("hidden");
  }, 2200);
}

async function apiGet(path) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiSend(path, method, body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    let message = `Request failed: ${res.status}`;
    try {
      const data = await res.json();
      if (data && data.error) message = data.error;
    } catch {}
    throw new Error(message);
  }
  return res.json().catch(() => ({}));
}

function loadSelection() {
  const raw = localStorage.getItem(STORAGE_KEYS.selection);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function saveSelection(ids) {
  localStorage.setItem(STORAGE_KEYS.selection, JSON.stringify(ids));
}

function clearClientState() {
  try {
    localStorage.removeItem(STORAGE_KEYS.selection);
  } catch (_) {
    // ignore storage errors
  }
}

function activateNavByPage() {
  const currentPage = document.body.dataset.page;
  const navLinks = document.querySelectorAll(".nav-link");
  if (!currentPage || !navLinks.length) return;
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.view === currentPage);
  });
}
async function handleLogoutClick() {
  try {
    await apiSend("/api/logout", "POST");
  } catch (err) {
    console.error(err);
    // Dù lỗi vẫn xóa client state và chuyển về trang login
  }
  clearClientState();
  window.location.href = "/login";
}

document.addEventListener("DOMContentLoaded", () => {
  activateNavByPage();

  const logoutBtn = document.getElementById("btn-logout");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogoutClick);
  }
});
