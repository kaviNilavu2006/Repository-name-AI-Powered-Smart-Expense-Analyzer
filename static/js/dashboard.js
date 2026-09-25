/**
 * Dashboard JS
 * Fetches summary + category + monthly analytics and renders
 * the four required Chart.js charts plus the stat cards.
 */

const CHART_COLORS = ["#4f46e5", "#7c3aed", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#db2777", "#0ea5e9", "#65a30d", "#9333ea"];

async function loadDashboard() {
  try {
    const [summaryRes, categoryRes, monthlyRes] = await Promise.all([
      fetch("/api/analytics/summary"),
      fetch("/api/analytics/category"),
      fetch("/api/analytics/monthly"),
    ]);

    const [summary, category, monthly] = await Promise.all([
      summaryRes.json(),
      categoryRes.json(),
      monthlyRes.json(),
    ]);

    if (!summaryRes.ok || !categoryRes.ok || !monthlyRes.ok || !summary.success || !category.success || !monthly.success) {
      showToast(summary.error || "Failed to load dashboard data.", "error");
      return;
    }

    renderStats(summary.data);
    renderCategoryDoughnut(category.data.category_totals);
    renderPaymentPie(summary.data.payment_method_totals);
    renderMonthlyBar(monthly.data.monthly_totals);
    renderDailyLine(monthly.data.daily_totals);

    // Fetch expense list for payment method chart (already in summary)
  } catch (err) {
    console.error(err);
    showToast("Unable to load dashboard. Please refresh.", "error");
  }
}

function renderStats(data) {
  document.getElementById("stat-total").textContent = formatCurrency(data.total_spending);
  document.getElementById("stat-month").textContent = formatCurrency(data.this_month_total);
  document.getElementById("stat-top-category").textContent = data.top_category || "N/A";
  document.getElementById("stat-transactions").textContent = data.transaction_count;
}

function renderCategoryDoughnut(categoryTotals) {
  const ctx = document.getElementById("categoryChart");
  if (!ctx) return;
  const labels = Object.keys(categoryTotals || {});
  const values = Object.values(categoryTotals || {});

  if (labels.length === 0) {
    ctx.parentElement.innerHTML = '<div class="empty-state"><i class="bi bi-pie-chart"></i><p>No category data yet. Add an expense to see this chart.</p></div>';
    return;
  }

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: CHART_COLORS }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
}

function renderPaymentPie(paymentTotals) {
  const ctx = document.getElementById("paymentChart");
  if (!ctx) return;
  const labels = Object.keys(paymentTotals || {});
  const values = Object.values(paymentTotals || {});

  if (labels.length === 0) {
    ctx.parentElement.innerHTML = '<div class="empty-state"><i class="bi bi-cash-coin"></i><p>No payment data yet.</p></div>';
    return;
  }

  new Chart(ctx, {
    type: "pie",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: CHART_COLORS }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
}

function renderMonthlyBar(monthlyTotals) {
  const ctx = document.getElementById("monthlyChart");
  if (!ctx) return;
  const labels = Object.keys(monthlyTotals || {}).sort();
  const values = labels.map((l) => monthlyTotals[l]);

  if (labels.length === 0) {
    ctx.parentElement.innerHTML = '<div class="empty-state"><i class="bi bi-bar-chart"></i><p>No monthly data yet.</p></div>';
    return;
  }

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Monthly Spending (₹)", data: values, backgroundColor: "#4f46e5" }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });
}

function renderDailyLine(dailyTotals) {
  const ctx = document.getElementById("dailyChart");
  if (!ctx) return;
  const labels = Object.keys(dailyTotals || {}).sort();
  const values = labels.map((l) => dailyTotals[l]);

  if (labels.length === 0) {
    ctx.parentElement.innerHTML = '<div class="empty-state"><i class="bi bi-graph-up"></i><p>No daily data yet.</p></div>';
    return;
  }

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Daily Spending (₹)",
        data: values,
        borderColor: "#4f46e5",
        backgroundColor: "rgba(79,70,229,0.1)",
        tension: 0.35,
        fill: true,
      }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });
}

document.addEventListener("DOMContentLoaded", loadDashboard);
