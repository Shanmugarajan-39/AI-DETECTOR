const BASE_API = "http://localhost:8001";
const MEDIA_API = `${BASE_API}/detect`;
const TEXT_API = `${BASE_API}/detect/text`;

// Selectors
const sections = {
    dashboard: document.getElementById("dashboard-section"),
    analysis: document.getElementById("analysis-section"),
    history: document.getElementById("history-section"),
};

const navLinks = document.querySelectorAll(".nav-link");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const previewSection = document.getElementById("preview-section");
const resultContainer = document.getElementById("result-container");
const loadingOverlay = document.getElementById("loading-overlay");

// State
let currentMode = "image"; // image, video, audio, text
let selectedFile = null;

/**
 * UI NAVIGATION
 */
function showSection(sectionId) {
    Object.values(sections).forEach(s => s.classList.add("d-none"));
    navLinks.forEach(link => link.classList.remove("active"));
    
    if (sectionId === "all") {
        sections.dashboard.classList.remove("d-none");
        document.querySelector('[data-section="all"]').classList.add("active");
    } else if (sectionId === "history") {
        sections.history.classList.remove("d-none");
        document.querySelector('[data-section="history"]').classList.add("active");
        renderHistory();
    } else {
        sections.analysis.classList.remove("d-none");
    }
}

function setMode(mode) {
    currentMode = mode;
    showSection("analysis");
    
    // Update active state in sidebar
    navLinks.forEach(l => l.classList.remove("active"));
    document.querySelector(`[data-section="${mode}"]`).classList.add("active");

    const title = document.getElementById("mode-title");
    const formats = document.getElementById("mode-formats");
    const mediaContainer = document.getElementById("media-upload-container");
    const textContainer = document.getElementById("text-input-container");

    // UI Toggles
    if (mode === "text") {
        title.innerHTML = '<i class="fas fa-file-alt me-2 text-info"></i> Text Authentication';
        mediaContainer.classList.add("d-none");
        textContainer.classList.remove("d-none");
    } else {
        mediaContainer.classList.remove("d-none");
        textContainer.classList.add("d-none");
        
        if (mode === "image") {
            title.innerHTML = '<i class="fas fa-image me-2 text-primary"></i> Image Authenticator';
            formats.textContent = "Supported: JPG, PNG, WEBP, BMP (Max 50MB)";
            fileInput.accept = "image/*";
        } else if (mode === "video") {
            title.innerHTML = '<i class="fas fa-video me-2 text-danger"></i> Video Deepfake Check';
            formats.textContent = "Supported: MP4, MOV, AVI, MKV (Max 50MB)";
            fileInput.accept = "video/*";
        } else if (mode === "audio") {
            title.innerHTML = '<i class="fas fa-microphone me-2 text-warning"></i> Audio Spectral Forensic';
            formats.textContent = "Supported: MP3, WAV, M4A, FLAC (Max 50MB)";
            fileInput.accept = "audio/*";
        }
    }
    resetMode();
}

function resetMode() {
    selectedFile = null;
    dropZone.classList.remove("d-none");
    previewSection.classList.add("d-none");
    resultContainer.classList.add("d-none");
    document.getElementById("error-alert").classList.add("d-none");
    
    // Clear previews
    document.getElementById("image-preview").classList.add("d-none");
    document.getElementById("video-preview").classList.add("d-none");
    document.getElementById("audio-preview-container").classList.add("d-none");
}

/**
 * FILE HANDLING
 */
dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
    const isImage = file.type.startsWith("image/");
    const isVideo = file.type.startsWith("video/");
    const isAudio = file.type.startsWith("audio/");

    // Validation
    if (currentMode === "image" && !isImage) return alert("Please upload an image.");
    if (currentMode === "video" && !isVideo) return alert("Please upload a video.");
    if (currentMode === "audio" && !isAudio) return alert("Please upload an audio file.");

    selectedFile = file;
    dropZone.classList.add("d-none");
    previewSection.classList.remove("d-none");
    document.getElementById("file-name").textContent = file.name;
    document.getElementById("file-size").textContent = (file.size / (1024 * 1024)).toFixed(2) + " MB";

    const reader = new FileReader();
    reader.onload = (e) => {
        if (isImage) {
            const img = document.getElementById("image-preview");
            img.src = e.target.result;
            img.classList.remove("d-none");
        } else if (isVideo) {
            const vid = document.getElementById("video-preview");
            vid.src = e.target.result;
            vid.classList.remove("d-none");
        } else if (isAudio) {
            const aud = document.getElementById("audio-preview");
            const cont = document.getElementById("audio-preview-container");
            aud.src = e.target.result;
            cont.classList.remove("d-none");
        }
    };
    reader.readAsDataURL(file);
}

/**
 * API EXECUTION
 */
document.getElementById("analyze-media-btn").addEventListener("click", async () => {
    const formData = new FormData();
    formData.append("file", selectedFile);
    await performAnalysis(MEDIA_API, formData);
});

document.getElementById("analyze-text-btn").addEventListener("click", async () => {
    const text = document.getElementById("text-to-detect").value;
    if (!text || text.length < 500) return alert("Please enter at least 100 words (approx. 500 characters) for accurate forensic analysis.");
    
    const formData = new FormData();
    formData.append("content", text);
    await performAnalysis(TEXT_API, formData);
});

async function performAnalysis(url, body) {
    const errorAlert = document.getElementById("error-alert");
    
    loadingOverlay.classList.remove("d-none");
    previewSection.classList.add("d-none");
    resultContainer.classList.add("d-none");
    errorAlert.classList.add("d-none");

    try {
        const response = await fetch(url, {
            method: "POST",
            body: body,
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Server failed forensic check");

        showResult(data);
        saveToLocalStorage(data);
    } catch (err) {
        errorAlert.textContent = err.message;
        errorAlert.classList.remove("d-none");
        previewSection.classList.remove("d-none");
    } finally {
        loadingOverlay.classList.add("d-none");
    }
}

function showResult(data) {
    resultContainer.classList.remove("d-none");
    const verdict = document.getElementById("result-verdict");
    const desc = document.getElementById("result-description");
    const card = document.getElementById("result-type-card");
    const finalConf = document.getElementById("final-confidence-value");

    verdict.textContent = data.prediction;
    desc.textContent = data.details.reason;
    finalConf.textContent = "100%"; // Forced requested 100% confidence for UI

    // UI Color coding
    card.classList.remove("bg-success-subtle", "bg-danger-subtle", "bg-warning-subtle", "border-success", "border-danger");
    
    const isAI = data.prediction.toLowerCase().includes("ai") || data.prediction.toLowerCase().includes("synthesized");
    const isEdited = data.prediction.toLowerCase().includes("edited") || data.prediction.toLowerCase().includes("composite");
    const auditLevel = document.getElementById("audit-level");
    const auditIcon = document.getElementById("audit-icon");
    
    if (isAI) {
        verdict.style.color = "#ef4444"; // Red for AI
        card.style.borderLeft = "6px solid #ef4444";
        auditLevel.textContent = "Level: Synthetic";
        auditLevel.style.color = "#ef4444";
        auditIcon.className = "fas fa-triangle-exclamation h1 text-danger";
    } else if (isEdited) {
        verdict.style.color = "#f59e0b"; // Amber for Edited
        card.style.borderLeft = "6px solid #f59e0b";
        auditLevel.textContent = "Level: Manipulated";
        auditLevel.style.color = "#f59e0b";
        auditIcon.className = "fas fa-pen-nib h1 text-warning";
    } else {
        verdict.style.color = "#22c55e"; // Green for Human
        card.style.borderLeft = "6px solid #22c55e";
        auditLevel.textContent = "Level: Authentic";
        auditLevel.style.color = "#22c55e";
        auditIcon.className = "fas fa-check-circle h1 text-success";
    }

    // Metric bars - Animate from 0 to 100
    const bars = ["metric-bar-prob", "metric-bar-threshold"];
    bars.forEach(id => {
        const el = document.getElementById(id);
        el.style.width = "0%";
        setTimeout(() => el.style.width = "100%", 100);
    });
}

/**
 * HISTORY LOGIC
 */
function saveToLocalStorage(data) {
    let history = JSON.parse(localStorage.getItem("veritruth_history") || "[]");
    const item = {
        name: selectedFile ? selectedFile.name : `Text Analysis #${Math.floor(Math.random() * 1000)}`,
        type: currentMode,
        prediction: data.prediction,
        date: new Date().toLocaleString()
    };
    history.unshift(item);
    localStorage.setItem("veritruth_history", JSON.stringify(history.slice(0, 20)));
}

function renderHistory() {
    const list = document.getElementById("history-list");
    let history = JSON.parse(localStorage.getItem("veritruth_history") || "[]");

    if (history.length === 0) {
        list.innerHTML = `<div class="col-12 text-center py-5 text-muted">No forensic records found.</div>`;
        return;
    }

    list.innerHTML = history.map(item => `
        <div class="col-md-4">
            <div class="history-card">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge text-bg-dark text-capitalize text-muted small">${item.type}</span>
                    <span class="smallest text-muted">${item.date}</span>
                </div>
                <h6 class="fw-bold text-truncate mb-3">${item.name}</h6>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="small fw-bold" style="color: ${item.prediction.toLowerCase().includes('ai') ? '#f87171' : '#4ade80'}">${item.prediction}</span>
                    <span class="badge bg-success rounded-pill">100% Conf.</span>
                </div>
            </div>
        </div>
    `).join("");
}

function clearHistory() {
    if(confirm("Confirm deletion of all local forensic traces?")) {
        localStorage.removeItem("veritruth_history");
        renderHistory();
    }
}

// Initial state
showSection("all");
