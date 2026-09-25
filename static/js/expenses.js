/**
 * Expenses JS
 * Handles the expense list page (search/filter/sort/edit/delete)
 * and the add/edit expense form submission.
 */

function formatDate(dateStr) {
  if (!dateStr) return "";
  const [y, m, d] = dateStr.split("-");
  return `${d}-${m}-${y}`;
}

async function loadExpenses() {
  const tableBody = document.getElementById("expenses-table-body");
  const emptyState = document.getElementById("expenses-empty-state");
  if (!tableBody) return;

  const params = new URLSearchParams();
  const category = document.getElementById("filter-category")?.value;
  const search = document.getElementById("filter-search")?.value;
  const dateFrom = document.getElementById("filter-date-from")?.value;
  const dateTo = document.getElementById("filter-date-to")?.value;
  const sortBy = document.getElementById("filter-sort-by")?.value;

  if (category) params.set("category", category);
  if (search) params.set("search", search);
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  if (sortBy) params.set("sort_by", sortBy);

  tableBody.innerHTML = `<tr><td colspan="7"><div class="loading-overlay"><span class="spinner-border spinner-border-sm me-2"></span>Loading expenses...</div></td></tr>`;

  try {
    const res = await fetch(`/api/expenses?${params.toString()}`);
    const result = await res.json();

    if (!result.success) {
      showToast(result.error || "Failed to load expenses.", "error");
      return;
    }

    const expenses = result.data.expenses;
    tableBody.innerHTML = "";

    if (expenses.length === 0) {
      emptyState.classList.remove("d-none");
      document.getElementById("expenses-table-wrapper").classList.add("d-none");
      return;
    }

    emptyState.classList.add("d-none");
    document.getElementById("expenses-table-wrapper").classList.remove("d-none");

    expenses.forEach((exp) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${formatDate(exp.date)}</td>
        <td>${exp.description || "-"}</td>
        <td><span class="category-badge">${exp.category}</span></td>
        <td>${formatCurrency(exp.amount)}</td>
        <td>${exp.payment_method}</td>
        <td>${exp.receipt_url ? `<a href="${exp.receipt_url}" target="_blank"><i class="bi bi-receipt"></i> View</a>` : "—"}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1 edit-btn" data-id="${exp.expense_id}"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${exp.expense_id}"><i class="bi bi-trash"></i></button>
        </td>`;
      tableBody.appendChild(row);
    });

    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () => deleteExpense(btn.dataset.id));
    });
    document.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", () => (window.location.href = `/add-expense?edit=${btn.dataset.id}`));
    });
  } catch (err) {
    console.error(err);
    showToast("Network error while loading expenses.", "error");
  }
}

async function deleteExpense(expenseId) {
  if (!confirm("Are you sure you want to delete this expense?")) return;
  try {
    const res = await fetch(`/api/expenses/${expenseId}`, { method: "DELETE" });
    const result = await res.json();
    if (result.success) {
      showToast("Expense deleted.", "success");
      loadExpenses();
    } else {
      showToast(result.error || "Failed to delete expense.", "error");
    }
  } catch (err) {
    showToast("Network error while deleting expense.", "error");
  }
}

async function loadExpenseForEdit(expenseId) {
  try {
    const res = await fetch(`/api/expenses/${expenseId}`);
    const result = await res.json();
    if (!result.success) return;

    const exp = result.data.expense;
    document.getElementById("amount").value = exp.amount;
    document.getElementById("category").value = exp.category;
    document.getElementById("description").value = exp.description;
    document.getElementById("date").value = exp.date;
    document.getElementById("payment_method").value = exp.payment_method;
    document.getElementById("expense-form").dataset.editId = expenseId;
    document.getElementById("form-title").textContent = "Edit Expense";
    document.getElementById("submit-btn-text").textContent = "Update Expense";
  } catch (err) {
    console.error(err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadExpenses();

  ["filter-category", "filter-search", "filter-date-from", "filter-date-to", "filter-sort-by"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", loadExpenses);
  });
  const searchInput = document.getElementById("filter-search");
  if (searchInput) searchInput.addEventListener("keyup", () => loadExpenses());

  const expenseForm = document.getElementById("expense-form");
  if (expenseForm) {
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get("edit");
    if (editId) loadExpenseForEdit(editId);

    expenseForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = expenseForm.querySelector("button[type='submit']");
      setButtonLoading(submitBtn, true, "Saving...");

      const formData = new FormData(expenseForm);
      const editingId = expenseForm.dataset.editId;
      const url = editingId ? `/api/expenses/${editingId}` : "/api/expenses";
      const method = editingId ? "PUT" : "POST";

      try {
        const res = await fetch(url, { method, body: formData });
        const result = await res.json();

        if (result.success) {
          showToast(result.message || "Expense saved.", "success");
          setTimeout(() => (window.location.href = "/expenses"), 700);
        } else {
          showToast(result.error || "Failed to save expense.", "error");
        }
      } catch (err) {
        showToast("Network error while saving expense.", "error");
      } finally {
        setButtonLoading(submitBtn, false);
      }
    });
  }
});
