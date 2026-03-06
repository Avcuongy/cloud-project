document.addEventListener("DOMContentLoaded", () => {
	if (document.body.dataset.page !== "composer") return;

	const composerSelectedList = document.getElementById("composer-selected-list");
	const composerHint = document.getElementById("composer-hint");
	const deliveryToggle = document.getElementById("delivery-toggle");
	const composerMessage = document.getElementById("composer-message");
	const btnSendNow = document.getElementById("btn-send-now");

	if (!composerSelectedList || !deliveryToggle) return;

	const customers = loadCustomers();
	const selectedIds = new Set(loadSelection());

	function renderComposerSelection() {
		composerSelectedList.innerHTML = "";
		const selectedCustomers = customers.filter((c) => selectedIds.has(c.id));

		selectedCustomers.forEach((c) => {
			const li = document.createElement("li");
			li.className = "pill";
			li.textContent = c.fullName;
			composerSelectedList.appendChild(li);
		});

		const hasSelection = selectedCustomers.length > 0;
		composerHint.style.display = hasSelection ? "none" : "block";
		btnSendNow.disabled = !hasSelection || !composerMessage.value.trim();
	}

	composerMessage.addEventListener("input", () => {
		const hasSelection = Array.from(selectedIds).length > 0;
		btnSendNow.disabled = !hasSelection || !composerMessage.value.trim();
	});

	deliveryToggle.addEventListener("click", (e) => {
		const btn = e.target.closest(".toggle-btn");
		if (!btn) return;
		const type = btn.dataset.type;
		deliveryToggle
			.querySelectorAll(".toggle-btn")
			.forEach((b) => b.classList.toggle("active", b === btn));
		deliveryToggle.dataset.activeType = type;
	});

	btnSendNow.addEventListener("click", () => {
		const type = deliveryToggle.dataset.activeType || "EMAIL";
		const message = composerMessage.value.trim();
		if (!message) return;

		const selectedCustomers = customers.filter((c) => selectedIds.has(c.id));
		if (!selectedCustomers.length) return;

		const logs = loadLogs();
		selectedCustomers.forEach((c) => {
			logs.push({
				customerId: c.id,
				customerName: c.fullName,
				type,
				status: "Success",
				messageId: `${type}-${Date.now()}-${c.id}`,
				sentAt: new Date().toISOString(),
			});
		});
		saveLogs(logs);

		composerMessage.value = "";
		btnSendNow.disabled = true;
		showToast(`Sent ${type} to ${selectedCustomers.length} customer(s)`);
		window.location.href = "logs.html";
	});

	renderComposerSelection();
});
