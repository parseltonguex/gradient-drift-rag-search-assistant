document.getElementById("askBtn").addEventListener("click", async () => {
  const query = document.getElementById("query").value.trim();
  const model = document.getElementById("model").value;
  const k = parseInt(document.getElementById("k").value, 10) || 5;

  if (!auth.isSignedIn()) {
    alert("Please sign in to use the assistant.");
    return;
  }

  try {
    const data = await auth.askApi( query, model, k );

    const answerDiv = document.getElementById("answer");
    answerDiv.classList.remove("hidden");
    const hasAnswer = typeof data.answer === "string" && data.answer.trim().length > 0;
    answerDiv.innerHTML = `<h2>Answer</h2><p>${escapeHtml(hasAnswer ? data.answer : "[No answer found]")}</p>`;


    const sourcesDiv = document.getElementById("sources");
    sourcesDiv.classList.remove("hidden");
    const items = (data.matches || [])
      .map(m => `<li><div>${escapeHtml(m.text || "")}</div><div class="score">score: ${typeof m.score === "number" ? m.score.toFixed(3) : "N/A"}</div></li>`)
      .join("");
    sourcesDiv.innerHTML = `<h2>Sources</h2><ul>${items}</ul>`;
  } catch (err) {
    console.error("Fetch failed:", err);
    alert("Something went wrong while fetching the answer.");
  }
});

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[c]));
}
