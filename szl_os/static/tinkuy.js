"use strict";
const el = id => document.getElementById(id);
async function refresh() {
  const button = el("run"), status = el("mode");
  try {
    const r = await fetch("/api/tinkuy/status", {cache: "no-store"});
    if (!r.ok) throw Error("status-unavailable");
    const v = await r.json();
    const enabled = v.local_inference_opted_in === true;
    button.disabled = !enabled;
    button.textContent = enabled ? "Run bounded local review" : "Local review requires opt-in";
    status.textContent = enabled
      ? "Local operator opted in · provider availability remains unverified"
      : "Local inference disabled · not AGI · no publication authority";
  } catch {
    button.disabled = true;
    status.textContent = "Status unavailable · inference remains disabled";
  }
}
el("round-form").addEventListener("submit", async event => {
  event.preventDefault();
  const button = el("run");
  if (button.disabled) return;
  button.disabled = true;
  const body = {
    round_id: el("round_id").value,
    objective: el("objective").value,
    source_repo: el("source_repo").value,
    source_sha: el("source_sha").value,
    passes: 1
  };
  el("result").textContent = "Research review in progress; production not authorized…";
  try {
    const response = await fetch("/api/tinkuy/round", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      cache: "no-store",
      body: JSON.stringify(body)
    });
    const result = await response.json();
    el("result").textContent = JSON.stringify({http_status: response.status, result}, null, 2);
  } catch {
    el("result").textContent = "Local review unavailable. No success or model identity verified.";
  } finally {
    await refresh();
  }
});
refresh();
