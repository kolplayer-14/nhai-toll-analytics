async function getJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error("Request failed: " + url);
  return res.json();
}

async function loadSummary() {
  const s = await getJSON("/api/summary");
  document.getElementById("plazas").textContent = s.total_plazas;
  document.getElementById("states").textContent = s.total_states;
  document.getElementById("avgFee").textContent = "Rs. " + s.avg_car_fee;
  document.getElementById("maxFee").textContent = "Rs. " + s.max_car_fee;

  const meta = s.meta || {};
  document.getElementById("source").textContent =
    meta.source === "sample"
      ? "Data source: SAMPLE data (add data.gov.in API key for live data)"
      : "Data source: " + (meta.source || "unknown");
  document.getElementById("report").textContent = JSON.stringify(meta, null, 2);

  // show charts (timestamp stops the browser using old cached images)
  const box = document.getElementById("charts");
  box.innerHTML = "";
  (meta.charts || []).forEach(name => {
    const img = document.createElement("img");
    img.src = "/charts/" + name + "?t=" + Date.now();
    img.alt = name;
    box.appendChild(img);
  });
}

async function loadStates() {
  const select = document.getElementById("stateSelect");
  const states = await getJSON("/api/states");
  states.forEach(st => {
    const opt = document.createElement("option");
    opt.value = st;
    opt.textContent = st;
    select.appendChild(opt);
  });
  select.addEventListener("change", loadTable);
}

async function loadTable() {
  const state = document.getElementById("stateSelect").value;
  const rows = await getJSON("/api/tolls?limit=200&state=" + encodeURIComponent(state));
  document.getElementById("tbody").innerHTML = rows.map(r => `
    <tr><td>${r.toll_plaza_name}</td><td>${r.state}</td><td>${r.nh_number}</td>
    <td>${r.stretch_length_km}</td><td>${r.fee_car}</td><td>${r.fee_lcv}</td>
    <td>${r.fee_bus_truck}</td></tr>`).join("");
}

document.getElementById("refreshBtn").addEventListener("click", async (e) => {
  e.target.disabled = true;
  e.target.textContent = "Refreshing…";
  try {
    await getJSON("/api/refresh", { method: "POST" });
    await loadSummary();
    await loadTable();
  } finally {
    e.target.disabled = false;
    e.target.textContent = "Refresh data";
  }
});

(async function init() {
  await loadSummary();
  await loadStates();
  await loadTable();
})();
