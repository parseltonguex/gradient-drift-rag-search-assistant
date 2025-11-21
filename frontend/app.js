document.getElementById("askBtn").addEventListener("click", async () => {
  const query = document.getElementById("query").value.trim();
  const model = document.getElementById("model").value;
  const k = parseInt(document.getElementById("k").value, 10) || 5;

  const accessToken = sessionStorage.getItem("access_token");
  if (!accessToken || !auth.isSignedIn()) {
    alert("Please sign in to use the assistant.");
    return;
  }

  const res = await fetch("/api/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${accessToken}`
    },
    body: JSON.stringify({ query, model, k }),
    credentials: "omit" // 👈 reinforces no cookie reliance
  });

  if (res.status === 401) {
    alert("Session expired. Please sign in again.");
    return;
  }
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`API ${res.status}: ${t}`);
  }

  const data = await res.json();

  const answerDiv = document.getElementById("answer");
  answerDiv.classList.remove("hidden");
  answerDiv.innerHTML = `<h2>Answer</h2><p>${escapeHtml(data.answer || "")}</p>`;

  const sourcesDiv = document.getElementById("sources");
  sourcesDiv.classList.remove("hidden");
  const items = (data.matches || [])
    .map(m => `<li><div>${escapeHtml(m.text || "")}</div><div class="score">score: ${typeof m.score === "number" ? m.score.toFixed(3) : ""}</div></li>`)
    .join("");
  sourcesDiv.innerHTML = `<h2>Sources</h2><ul>${items}</ul>`;
});

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
