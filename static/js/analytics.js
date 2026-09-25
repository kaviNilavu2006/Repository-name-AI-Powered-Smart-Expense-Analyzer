/**
 * Analytics JS
 * Loads detailed analytics for a selected period and renders
 * stat tiles + category percentage bars.
 */

async function loadAnalytics(period = "current_month") {
  try {
    const res = await fetch(`/api/analytics/summary?period=${period}`);
    const result = await res.json();
    if (!result.success) {
      showToast(result.error || "Failed to load analytics.", "error");
      return;
    }
    renderAnalytics(result.data);
  } catch (err) {
    console.error(err);
    showToast("Network error while loading analytics.", "error");
  }
}

function renderAnalytics(data) {
  document.getElementById("an-total").textContent = formatCurrency(data.total_spending);
  document.getElementById("an-avg-daily").textContent = formatCurrency(data.average_daily_spending);
  document.getElementById("an-avg-transaction").textContent = formatCurrency(data.average_transaction_value);
  document.getElementById("an-highest").textContent = formatCurrency(data.highest_expense);
  document.getElementById("an-lowest").textContent = formatCurrency(data.lowest_expense);
  document.getElementById("an-top-category").textContent = data.top_category || "N/A";
  document.getElementById("an-transactions").textContent = data.transaction_count;

  const container = document.getElementById("category-percentage-list");
  container.innerHTML = "";

  const entries = Object.entries(data.category_percentages || {}).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    container.innerHTML = '<div class="empty-state"><i class="bi bi-bar-chart-line"></i><p>No data for this period yet.</p></div>';
    return;
  }

  entries.forEach(([category, pct]) => {
    const amount = data.category_totals[category] || 0;
    const row = document.createElement("div");
    row.className = "mb-3";
    row.innerHTML = `
      <div class="d-flex justify-content-between mb-1">
        <span class="fw-semibold">${category}</span>
        <span class="text-muted">${formatCurrency(amount)} (${pct}%)</span>
      </div>
      <div class="progress" style="height: 8px;">
        <div class="progress-bar" role="progressbar" style="width: ${pct}%; background-color: #4f46e5;"></div>
      </div>`;
    container.appendChild(row);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadAnalytics();

  const periodSelect = document.getElementById("period-select");
  if (periodSelect) {
    periodSelect.addEventListener("change", () => loadAnalytics(periodSelect.value));
  }
});
