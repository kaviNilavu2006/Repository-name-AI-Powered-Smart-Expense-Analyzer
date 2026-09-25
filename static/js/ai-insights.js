/**
 * AI Insights JS
 * Fetches AI-generated spending analysis and powers the chat
 * assistant interface.
 */

function renderMarkdownLite(text) {
  // Minimal markdown-to-HTML for headings (###) and bold (**) —
  // enough to render the structured AI response nicely.
  return text
    .split("\n")
    .map((line) => {
      if (line.startsWith("### ")) {
        return `<h6 class="fw-bold mt-3 mb-1 text-primary">${line.replace("### ", "")}</h6>`;
      }
      return `<p class="mb-1">${line}</p>`;
    })
    .join("");
}

async function loadAIAnalysis() {
  const container = document.getElementById("ai-analysis-content");
  if (!container) return;

  container.innerHTML = `<div class="loading-overlay"><span class="spinner-border spinner-border-sm me-2"></span>Analyzing your spending with AI...</div>`;

  try {
    const res = await fetch("/api/ai/analyze");
    const result = await res.json();

    if (!result.success) {
      container.innerHTML = `<div class="text-danger">${result.error || "Failed to generate insights."}</div>`;
      return;
    }

    const { analysis, disclaimer, source } = result.data;
    container.innerHTML = renderMarkdownLite(analysis);

    const badge = document.getElementById("ai-source-badge");
    if (badge) {
      badge.textContent = source === "bedrock" ? "Powered by Amazon Bedrock" : "Fallback Analysis Mode";
      badge.className = `badge ${source === "bedrock" ? "bg-success" : "bg-secondary"}`;
    }

    const disclaimerEl = document.getElementById("ai-disclaimer");
    if (disclaimerEl && disclaimer) {
      disclaimerEl.textContent = disclaimer;
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = `<div class="text-danger">Network error while generating insights.</div>`;
  }
}

function appendChatBubble(text, sender) {
  const chatWindow = document.getElementById("chat-window");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${sender}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendChatMessage(message) {
  appendChatBubble(message, "user");

  const chatWindow = document.getElementById("chat-window");
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "chat-bubble ai";
  typingIndicator.id = "typing-indicator";
  typingIndicator.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
  chatWindow.appendChild(typingIndicator);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const result = await res.json();
    document.getElementById("typing-indicator")?.remove();

    if (result.success) {
      appendChatBubble(result.data.reply, "ai");
    } else {
      appendChatBubble(result.error || "Sorry, something went wrong.", "ai");
    }
  } catch (err) {
    document.getElementById("typing-indicator")?.remove();
    appendChatBubble("Network error. Please try again.", "ai");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadAIAnalysis();

  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.getElementById("chat-input");
      const message = input.value.trim();
      if (!message) return;
      sendChatMessage(message);
      input.value = "";
    });
  }

  document.querySelectorAll(".suggested-question").forEach((btn) => {
    btn.addEventListener("click", () => sendChatMessage(btn.textContent.trim()));
  });

  const refreshBtn = document.getElementById("refresh-analysis-btn");
  if (refreshBtn) refreshBtn.addEventListener("click", loadAIAnalysis);
});
