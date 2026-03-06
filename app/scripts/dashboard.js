document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page !== "dashboard") return;

  const customersTableBody = document.querySelector("#customers-table tbody");
  const customersEmpty = document.getElementById("customers-empty");
  const searchInput = document.getElementById("search-input");
  const selectAllCheckbox = document.getElementById("select-all");
  const btnAddCustomer = document.getElementById("btn-add-customer");
  const btnSendSelected = document.getElementById("btn-send-selected");

  const modalBackdrop = document.getElementById("customer-modal-backdrop");
  const modalTitle = document.getElementById("customer-modal-title");
  const modalClose = document.getElementById("customer-modal-close");
  const modalCancel = document.getElementById("customer-modal-cancel");
  const modalSave = document.getElementById("customer-modal-save");
  const customerForm = document.getElementById("customer-form");
  const customerIdField = document.getElementById("customer-id");
  const fullNameField = document.getElementById("full-name");
  const addressField = document.getElementById("address");
  const phoneField = document.getElementById("phone");
  const emailField = document.getElementById("email");

  if (!customersTableBody || !btnAddCustomer) return;

  let customers = [];
  let selectedIds = new Set(loadSelection());

  async function loadCustomersFromApi() {
    try {
      customers = await apiGet("/api/customers");
      renderCustomers();
    } catch (err) {
      console.error(err);
      showToast("Failed to load customers");
    }
  }

  function openCustomerModal(mode, customer) {
    modalTitle.textContent = mode === "edit" ? "Edit Customer" : "Add Customer";
    if (mode === "edit" && customer) {
      customerIdField.value = customer.id;
      fullNameField.value = customer.fullName;
      addressField.value = customer.address;
      phoneField.value = customer.phone;
      emailField.value = customer.email;
    } else {
      customerIdField.value = "";
      customerForm.reset();
    }
    modalBackdrop.classList.remove("hidden");
    fullNameField.focus();
  }

  function closeCustomerModal() {
    modalBackdrop.classList.add("hidden");
  }

  function updateSelectionState() {
    btnSendSelected.disabled = selectedIds.size === 0;
    selectAllCheckbox.checked =
      customers.length > 0 && selectedIds.size === customers.length;
    saveSelection(Array.from(selectedIds));
  }

  function renderCustomers() {
    const query = searchInput.value.trim().toLowerCase();
    customersTableBody.innerHTML = "";
    let visibleCount = 0;

    customers.forEach((c) => {
      const searchable = `${c.fullName} ${c.phone} ${c.email}`.toLowerCase();
      if (query && !searchable.includes(query)) {
        return;
      }
      visibleCount += 1;
      const row = document.createElement("tr");

      const colCheck = document.createElement("td");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = selectedIds.has(c.id);
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
          selectedIds.add(c.id);
        } else {
          selectedIds.delete(c.id);
        }
        updateSelectionState();
      });
      colCheck.appendChild(checkbox);
      row.appendChild(colCheck);

      const colName = document.createElement("td");
      colName.textContent = c.fullName;
      row.appendChild(colName);

      const colAddress = document.createElement("td");
      colAddress.textContent = c.address;
      row.appendChild(colAddress);

      const colPhone = document.createElement("td");
      colPhone.textContent = c.phone;
      row.appendChild(colPhone);

      const colEmail = document.createElement("td");
      colEmail.textContent = c.email;
      row.appendChild(colEmail);

      const colActions = document.createElement("td");
      const editBtn = document.createElement("button");
      editBtn.textContent = "Edit";
      editBtn.className = "btn-ghost";
      editBtn.addEventListener("click", () => openCustomerModal("edit", c));

      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "Delete";
      deleteBtn.className = "btn-ghost";
      deleteBtn.addEventListener("click", () => {
        if (confirm("Delete this customer?")) {
          customers = customers.filter((x) => x.id !== c.id);
          selectedIds.delete(c.id);
          saveCustomers(customers);
          renderCustomers();
          showToast("Customer deleted");
        }
      });

      colActions.appendChild(editBtn);
      colActions.appendChild(deleteBtn);
      row.appendChild(colActions);

      customersTableBody.appendChild(row);
    });

    customersEmpty.classList.toggle("hidden", visibleCount > 0);
    updateSelectionState();
  }

  searchInput.addEventListener("input", renderCustomers);

  selectAllCheckbox.addEventListener("change", () => {
    if (selectAllCheckbox.checked) {
      customers.forEach((c) => selectedIds.add(c.id));
    } else {
      selectedIds.clear();
    }
    renderCustomers();
  });

  btnAddCustomer.addEventListener("click", () => openCustomerModal("add"));

  modalClose.addEventListener("click", closeCustomerModal);
  modalCancel.addEventListener("click", (e) => {
    e.preventDefault();
    closeCustomerModal();
  });

  modalBackdrop.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) {
      closeCustomerModal();
    }
  });

  modalSave.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!fullNameField.value.trim()) {
      fullNameField.focus();
      return;
    }

    const existingId = customerIdField.value
      ? parseInt(customerIdField.value, 10)
      : null;
    const data = {
      fullName: fullNameField.value.trim(),
      address: addressField.value.trim(),
      phone: phoneField.value.trim(),
      email: emailField.value.trim(),
    };

    try {
      if (existingId) {
        await apiSend(`/api/customers/${existingId}`, "PUT", data);
        showToast("Customer updated");
      } else {
        await apiSend("/api/customers", "POST", data);
        showToast("Customer added");
      }
      closeCustomerModal();
      await loadCustomersFromApi();
    } catch (err) {
      console.error(err);
      showToast("Failed to save customer");
    }
  });

  btnSendSelected.addEventListener("click", () => {
    saveSelection(Array.from(selectedIds));
    window.location.href = "composer.html";
  });

  loadCustomersFromApi();
});
