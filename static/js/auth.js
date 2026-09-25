/**
 * Auth JS
 * Handles login and registration form submission via the REST API.
 */

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) {
    alert(message);
    return;
  }
  const toastEl = document.createElement("div");
  toastEl.className = `toast align-items-center text-bg-${type === "error" ? "danger" : "success"} border-0 show mb-2`;
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  container.appendChild(toastEl);
  setTimeout(() => toastEl.remove(), 4000);
}

function setButtonLoading(button, loading, loadingText = "Please wait...") {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${loadingText}`;
    button.disabled = true;
  } else {
    button.innerHTML = button.dataset.originalText || button.innerHTML;
    button.disabled = false;
  }
}

function formatCurrency(value) {
  return "₹" + Number(value || 0).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = loginForm.querySelector("button[type='submit']");
      setButtonLoading(submitBtn, true, "Signing in...");

      const payload = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      };

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await res.json();

        if (result.success) {
          showToast("Login successful! Redirecting...", "success");
          setTimeout(() => (window.location.href = "/dashboard"), 700);
        } else {
          showToast(result.error || "Login failed.", "error");
        }
      } catch (err) {
        showToast("Network error. Please try again.", "error");
      } finally {
        setButtonLoading(submitBtn, false);
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = registerForm.querySelector("button[type='submit']");
      setButtonLoading(submitBtn, true, "Creating account...");

      const payload = {
        full_name: document.getElementById("full_name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        confirm_password: document.getElementById("confirm_password").value,
      };

      try {
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await res.json();

        if (result.success) {
          showToast("Account created! Redirecting...", "success");
          setTimeout(() => (window.location.href = "/dashboard"), 700);
        } else {
          showToast(result.error || "Registration failed.", "error");
        }
      } catch (err) {
        showToast("Network error. Please try again.", "error");
      } finally {
        setButtonLoading(submitBtn, false);
      }
    });
  }

  const logoutButtons = document.querySelectorAll(".logout-btn");
  logoutButtons.forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      await fetch("/api/auth/logout", { method: "POST" });
      window.location.href = "/login";
    });
  });
});
