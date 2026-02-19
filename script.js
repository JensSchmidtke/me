const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");

const fallbackPlaces = [
  { name: "Leipzig", country: "Germany", lat: 51.3406321, lon: 12.3747329 },
  { name: "Wermelskirchen", country: "Germany", lat: 51.1406481, lon: 7.2156901 },
  { name: "Haifa", country: "Israel", lat: 32.8191218, lon: 34.9983856 },
  { name: "Jerusalem", country: "Israel", lat: 31.7788472, lon: 35.2257856 },
  { name: "Amman", country: "Jordan", lat: 31.9515694, lon: 35.9239625 },
  { name: "Lansing", country: "USA", lat: 42.7338254, lon: -84.5546295 },
  { name: "Storrs", country: "USA", lat: 41.8084314, lon: -72.2495231 },
  { name: "Qingdao", country: "China", lat: 36.0663249, lon: 120.3777659 },
  { name: "Pemba", country: "Mozambique", lat: -12.9735551, lon: 40.5215098 },
  { name: "Medellin", country: "Colombia", lat: 6.2697325, lon: -75.6025597 }
];


const pinsContainer = document.getElementById("map-pins");

function lonToX(lon) {
  return ((lon + 180) / 360) * 100;
}

function latToY(lat) {
  return ((90 - lat) / 180) * 100;
}

function renderPins(places) {
  pinsContainer.innerHTML = "";

  places.forEach((place) => {
    const pin = document.createElement("div");
    pin.className = "map-pin";
    pin.style.left = `${lonToX(place.lon)}%`;
    pin.style.top = `${latToY(place.lat)}%`;
    pin.title = `${place.name}, ${place.country}`;
    const label = document.createElement("span");
    label.className = "map-pin-label";
    label.textContent = `${place.name}, ${place.country}`;
    pin.appendChild(label);
    pinsContainer.appendChild(pin);
  });
}

function parseCitiesCsv(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length <= 1) return [];

  const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const nameIndex = headers.indexOf("city");
  const countryIndex = headers.indexOf("country");
  const latIndex = headers.indexOf("latitude");
  const lonIndex = headers.indexOf("longitude");

  if ([nameIndex, countryIndex, latIndex, lonIndex].some((i) => i === -1)) {
    return [];
  }

  return lines.slice(1).map((line) => {
    const cols = line.split(",").map((c) => c.trim());
    return {
      name: cols[nameIndex],
      country: cols[countryIndex],
      lat: Number(cols[latIndex]),
      lon: Number(cols[lonIndex]),
    };
  }).filter((place) => place.name && place.country && Number.isFinite(place.lat) && Number.isFinite(place.lon));
}

async function loadPlaces() {
  try {
    const response = await fetch("cities_with_coordinates.csv");
    if (!response.ok) throw new Error("Failed to load CSV");
    const text = await response.text();
    const places = parseCitiesCsv(text);
    return places.length ? places : fallbackPlaces;
  } catch (error) {
    return fallbackPlaces;
  }
}

function setActiveTab(tabId) {
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === tabId));
  panels.forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setActiveTab(tab.dataset.tab));
});

loadPlaces().then(renderPins);
