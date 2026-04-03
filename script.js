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

const fallbackTeaching = [
  {
    semester: "Winter 2024/25",
    title: "Academic Writing",
    description: "Bachelor's Program, German as a Second Language",
    program: "University of Leipzig",
  },
  {
    semester: "Spring 2023",
    title: "Introduction to German Culture after 1945",
    description: "Master's Program in German and European Studies",
    program: "University of Haifa",
  },
  {
    semester: "Spring 2015",
    title: "Second and Foreign Language Learning (LLT 361)",
    description: "Second Language Studies Program",
    program: "Michigan State University",
  },
  {
    semester: "Spring 2026",
    title: "Rater training - Speaking and Writing C1",
    description: "Workshop given at the Goethe Institute",
    program: "Goethe-Institute",
  },
];


const pinsContainer = document.getElementById("map-pins");
const teachingGrid = document.getElementById("teaching-grid");
const photoSections = document.getElementById("photo-sections");

function lonToX(lon) {
  return ((lon + 180) / 360) * 100;
}

function latToY(lat) {
  return ((90 - lat) / 180) * 100;
}

function renderPins(places) {
  if (!pinsContainer) return;
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

function parseCsvLine(line) {
  const cells = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const next = line[i + 1];
    if (char === "\"" && inQuotes && next === "\"") {
      current += "\"";
      i += 1;
      continue;
    }
    if (char === "\"") {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === "," && !inQuotes) {
      cells.push(current.trim());
      current = "";
      continue;
    }
    current += char;
  }

  cells.push(current.trim());
  return cells;
}

function parseTeachingCsv(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length <= 1) return [];

  const headers = parseCsvLine(lines[0]).map((h) => h.trim().toLowerCase());
  const semesterIndex = headers.indexOf("semester");
  const titleIndex = headers.indexOf("course title");
  const descriptionIndex = headers.indexOf("course description");
  const programIndex = headers.indexOf("program");

  if ([semesterIndex, titleIndex, descriptionIndex, programIndex].some((i) => i === -1)) {
    return [];
  }

  return lines.slice(1).map((line) => {
    const cols = parseCsvLine(line);
    return {
      semester: cols[semesterIndex] || "",
      title: cols[titleIndex] || "",
      description: cols[descriptionIndex] || "",
      program: cols[programIndex] || "",
    };
  }).filter((row) => row.semester && row.title);
}

function renderTeaching(items) {
  if (!teachingGrid) return;
  teachingGrid.innerHTML = "";

  const limit = Number(teachingGrid.dataset.limit || 0);
  const visibleItems = Number.isFinite(limit) && limit > 0 ? items.slice(0, limit) : items;

  visibleItems.forEach((item) => {
    const card = document.createElement("div");
    card.className = "teaching-card";

    const term = document.createElement("div");
    term.className = "teaching-term";
    term.textContent = item.semester;

    const title = document.createElement("h3");
    title.textContent = item.title;

    const description = document.createElement("p");
    const program = item.program ? ` — ${item.program}` : "";
    description.textContent = `${item.description}${program}`.trim();

    card.appendChild(term);
    card.appendChild(title);
    card.appendChild(description);
    teachingGrid.appendChild(card);
  });
}

async function loadTeaching() {
  try {
    const response = await fetch("teaching.csv");
    if (!response.ok) throw new Error("Failed to load teaching CSV");
    const text = await response.text();
    const items = parseTeachingCsv(text);
    return items.length ? items : fallbackTeaching;
  } catch (error) {
    return fallbackTeaching;
  }
}

function setActiveTab(tabId) {
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === tabId));
  panels.forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
}

if (tabs.length && panels.length) {
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => setActiveTab(tab.dataset.tab));
  });
}

if (pinsContainer) {
  loadPlaces().then(renderPins);
}

if (teachingGrid) {
  loadTeaching().then(renderTeaching);
}

function renderPhotoSection(title, items) {
  if (!photoSections) return;
  const section = document.createElement("section");
  section.className = "photo-section";

  const heading = document.createElement("h3");
  heading.textContent = title;

  const grid = document.createElement("div");
  grid.className = "photo-grid";

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "photo-empty";
    empty.textContent = "No photos yet.";
    section.appendChild(heading);
    section.appendChild(empty);
    photoSections.appendChild(section);
    return;
  }

  items.forEach((item) => {
    const figure = document.createElement("figure");
    figure.className = "photo-tile";

    const media = document.createElement("div");
    media.className = "photo-media";

    const img = document.createElement("img");
    img.src = item.src;
    img.alt = item.alt || `${title} photo`;
    img.loading = "lazy";

    media.appendChild(img);
    figure.appendChild(media);
    if (item.caption !== undefined) {
      const caption = document.createElement("figcaption");
      caption.textContent = item.caption;
      figure.appendChild(caption);
    }
    grid.appendChild(figure);
  });

  section.appendChild(heading);
  section.appendChild(grid);
  photoSections.appendChild(section);
}

async function loadPhotos() {
  try {
    const response = await fetch("photos.json");
    if (!response.ok) throw new Error("Failed to load photos");
    const data = await response.json();
    return data && typeof data === "object" ? data : {};
  } catch (error) {
    return {};
  }
}

if (photoSections) {
  loadPhotos().then((data) => {
    Object.entries(data).forEach(([section, items]) => {
      const normalized = Array.isArray(items)
        ? items.map((entry) => {
          if (typeof entry === "string") {
            return { src: `photos/${section}/${entry}`, alt: `${section} photo`, caption: "" };
          }
          if (entry && typeof entry === "object") {
            const file = entry.file || entry.src || "";
            return {
              src: file.startsWith("photos/") ? file : `photos/${section}/${file}`,
              alt: entry.alt || `${section} photo`,
              caption: entry.caption ?? "",
            };
          }
          return null;
        }).filter(Boolean)
        : [];

      renderPhotoSection(section, normalized);
    });
  });
}
