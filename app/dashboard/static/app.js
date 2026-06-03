const statusCards = document.getElementById("status-cards");
const eventsTableBody = document.querySelector("#events-table tbody");
const lastUpdated = document.getElementById("last-updated");
const eventsCount = document.getElementById("events-count");

function formatValue(value) {
  if (value === undefined || value === null) {
    return "N/A";
  }
  return String(value);
}

function summarizeVision(vision) {
  const counts = { person: 0, helmet: 0, no_helmet: 0, other: 0 };
  if (!vision || typeof vision !== "object") {
    return counts;
  }

  Object.values(vision).forEach((items) => {
    if (!Array.isArray(items)) {
      return;
    }
    items.forEach((item) => {
      const label = String(item.label || "").toLowerCase();
      if (label.includes("person")) {
        counts.person += 1;
      } else if (label.includes("helmet")) {
        if (label.includes("no")) {
          counts.no_helmet += 1;
        } else {
          counts.helmet += 1;
        }
      } else {
        counts.other += 1;
      }
    });
  });
  return counts;
}

function renderCurrent(data) {
  if (!data || data.message === "no_data") {
    statusCards.innerHTML = `<div class="card"><h3>No live data</h3><p>Waiting for the monitoring system to publish events.</p></div>`;
    return;
  }

  const sensorData = data.sensor_data || {};
  const visionData = data.vision_data || {};
  const visionCounts = summarizeVision(visionData);
  const isAlert =
    String(data.decision || "")
      .toLowerCase()
      .includes("high") ||
    String(data.reason || "")
      .toLowerCase()
      .includes("no_helmet");

  statusCards.innerHTML = `
    <div class="card">
      <h3>Decision</h3>
      <p>${formatValue(data.decision)}</p>
      <small>${formatValue(data.reason)}</small>
    </div>
    <div class="card">
      <h3>Sensor readings</h3>
      <p>Gas ${formatValue(sensorData.gas)}, Temp ${formatValue(sensorData.temperature)}, Vib ${formatValue(sensorData.vibration)}</p>
      <small>Updated from latest event</small>
    </div>
    <div class="card">
      <h3>Vision summary</h3>
      <p>People ${visionCounts.person}, Helmets ${visionCounts.helmet}, Missing ${visionCounts.no_helmet}</p>
      <small>Frame detections from latest event</small>
    </div>
    <div class="card">
      <h3>Status</h3>
      <p class="status-pill ${isAlert ? "alert" : "safe"}">${isAlert ? "ALERT" : "Normal"}</p>
      <small>Live state</small>
    </div>
  `;

  lastUpdated.textContent = new Date().toLocaleTimeString();
}

function renderEvents(events) {
  if (!Array.isArray(events)) {
    eventsTableBody.innerHTML = "";
    eventsCount.textContent = "";
    return;
  }

  eventsCount.textContent = `${events.length} recent entries`;
  eventsTableBody.innerHTML = events
    .map((event) => {
      const sensor = event.sensor_data || {};
      return `
        <tr>
          <td>${formatValue(event.timestamp)}</td>
          <td>${formatValue(event.decision)}</td>
          <td>${formatValue(event.reason)}</td>
          <td>${formatValue(sensor.gas)}</td>
          <td>${formatValue(sensor.temperature)}</td>
          <td>${formatValue(sensor.vibration)}</td>
        </tr>
      `;
    })
    .join("");
}

async function fetchCurrent() {
  try {
    const response = await fetch("/api/current");
    if (response.status === 204) {
      renderCurrent({ message: "no_data" });
      return;
    }
    const data = await response.json();
    renderCurrent(data);
  } catch (error) {
    console.error("Failed to load current state", error);
    statusCards.innerHTML = `<div class="card"><h3>Dashboard error</h3><p>Unable to read live state.</p></div>`;
  }
}

async function fetchEvents() {
  try {
    const response = await fetch("/api/events?limit=25");
    const data = await response.json();
    renderEvents(data);
  } catch (error) {
    console.error("Failed to load events", error);
    eventsTableBody.innerHTML =
      "<tr><td colspan=6>Unable to load event history.</td></tr>";
  }
}

function refreshAll() {
  fetchCurrent();
  fetchEvents();
}

window.addEventListener("load", () => {
  refreshAll();
  setInterval(refreshAll, 3000);
});
