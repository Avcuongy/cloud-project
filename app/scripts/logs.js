document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page !== "logs") return;

  const logsTableBody = document.querySelector("#logs-table tbody");
  const logsEmpty = document.getElementById("logs-empty");
  if (!logsTableBody) return;

  const logs = loadLogs();
  logsTableBody.innerHTML = "";

  logs.forEach((log) => {
    const row = document.createElement("tr");

    const colCustomer = document.createElement("td");
    colCustomer.textContent = log.customerName;
    row.appendChild(colCustomer);

    const colType = document.createElement("td");
    colType.textContent = log.type;
    row.appendChild(colType);

    const colStatus = document.createElement("td");
    colStatus.textContent = log.status;
    row.appendChild(colStatus);

    const colMessageId = document.createElement("td");
    colMessageId.textContent = log.messageId;
    row.appendChild(colMessageId);

    const colSentAt = document.createElement("td");
    colSentAt.textContent = new Date(log.sentAt).toLocaleString();
    row.appendChild(colSentAt);

    logsTableBody.appendChild(row);
  });

  logsEmpty.classList.toggle("hidden", logs.length > 0);
});
