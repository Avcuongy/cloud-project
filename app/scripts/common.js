// Shared helpers for all pages
const STORAGE_KEYS = {
  customers: "cloud_customers",
  logs: "cloud_logs",
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

function loadCustomers() {
  const raw = localStorage.getItem(STORAGE_KEYS.customers);
  if (raw) {
    try {
      return JSON.parse(raw);
    } catch {
      // ignore and reseed
    }
  }
  const seed = [
    {
      id: 1,
      fullName: "Nguyen Van A",
      address: "Ho Chi Minh City",
      phone: "+84 901 234 567",
      email: "nguyenvana@example.com",
      createdAt: new Date().toISOString(),
    },
    {
      id: 2,
      fullName: "Tran Thi B",
      address: "Ha Noi",
      phone: "+84 912 345 678",
      email: "tranthib@example.com",
      createdAt: new Date().toISOString(),
    },
  ];
  localStorage.setItem(STORAGE_KEYS.customers, JSON.stringify(seed));
  return seed;
}

function saveCustomers(customers) {
  localStorage.setItem(STORAGE_KEYS.customers, JSON.stringify(customers));
}

function loadLogs() {
  const raw = localStorage.getItem(STORAGE_KEYS.logs);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function saveLogs(logs) {
  localStorage.setItem(STORAGE_KEYS.logs, JSON.stringify(logs));
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

function activateNavByPage() {
  const currentPage = document.body.dataset.page;
  const navLinks = document.querySelectorAll(".nav-link");
  if (!currentPage || !navLinks.length) return;
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.view === currentPage);
  });
}

document.addEventListener("DOMContentLoaded", activateNavByPage);
