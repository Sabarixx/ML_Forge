const token = localStorage.getItem("token");

// Redirect to login if no token found
if (!token) {
    window.location.href = "index.html";
}

// ===== LOGOUT =====
document.getElementById("logoutBtn").addEventListener("click", function () {
    localStorage.removeItem("token");
    window.location.href = "index.html";
});

// ===== LOAD DATASETS (runs on page load) =====
async function loadDatasets() {
    try {
        const datasets = await apiRequest("/datasets/", "GET", null, true);
        renderDatasetList(datasets);
        renderDatasetDropdown(datasets);
    } catch (err) {
        console.error("Failed to load datasets:", err.message);
    }
}

function renderDatasetList(datasets) {
    const listEl = document.getElementById("datasetList");
    const countEl = document.getElementById("datasetCount");
    countEl.textContent = `${datasets.length} total`;

    if (datasets.length === 0) {
        listEl.innerHTML = `<li class="empty-state">No datasets yet</li>`;
        return;
    }

    listEl.innerHTML = datasets.map(d => `
        <li>
            <div class="dataset-name">📄 ${d.filename}</div>
            <div class="dataset-meta">ID: ${d.id} • Uploaded ${new Date(d.upload_date).toLocaleDateString()}</div>
        </li>
    `).join("");
}

function renderDatasetDropdown(datasets) {
    const select = document.getElementById("datasetIdInput");
    select.innerHTML = `<option value="">Select a dataset...</option>` +
        datasets.map(d => `<option value="${d.id}">${d.filename} (ID: ${d.id})</option>`).join("");
}

// ===== UPLOAD DATASET =====
document.getElementById("dropzone").addEventListener("click", function () {
    document.getElementById("csvFile").click();
});

document.getElementById("csvFile").addEventListener("change", function () {
    const fileName = this.files[0]?.name;
    if (fileName) {
        document.querySelector(".dropzone-hint").textContent = fileName;
    }
});

document.getElementById("uploadBtn").addEventListener("click", async function () {
    const fileInput = document.getElementById("csvFile");
    const uploadMsg = document.getElementById("uploadMsg");

    if (!fileInput.files.length) {
        uploadMsg.textContent = "Please choose a CSV file first.";
        uploadMsg.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE}/datasets/upload`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData,
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Upload failed");

        uploadMsg.textContent = `Uploaded! ${data.rows} rows, ${data.columns.length} columns.`;
        uploadMsg.style.color = "green";
        loadDatasets(); // refresh the list
    } catch (err) {
        uploadMsg.textContent = err.message;
        uploadMsg.style.color = "red";
    }
});

// ===== TRAIN MODELS =====
document.getElementById("trainBtn").addEventListener("click", async function () {
    const datasetId = document.getElementById("datasetIdInput").value;
    const targetColumn = document.getElementById("targetColumnInput").value;
    const trainMsg = document.getElementById("trainMsg");

    if (!datasetId || !targetColumn) {
        trainMsg.textContent = "Please select a dataset and enter a target column.";
        trainMsg.style.color = "red";
        return;
    }

    trainMsg.textContent = "Training all 4 models, please wait...";
    trainMsg.style.color = "#2563eb";

    try {
        const data = await apiRequest("/experiments/train", "POST", {
            dataset_id: parseInt(datasetId),
            target_column: targetColumn,
        }, true);

        trainMsg.textContent = "Training complete!";
        trainMsg.style.color = "green";
        renderResults(data.results);
    } catch (err) {
        trainMsg.textContent = err.message;
        trainMsg.style.color = "red";
    }
});

// ===== RENDER RESULTS (table + chart) =====
let chartInstance = null;

function renderResults(results) {
    document.getElementById("emptyResults").style.display = "none";

    const table = document.getElementById("resultsTable");
    table.style.display = "table";
    const tbody = table.querySelector("tbody");
    tbody.innerHTML = "";

    const labels = [];
    const accuracyData = [];

    for (const [modelName, scores] of Object.entries(results)) {
        tbody.innerHTML += `
            <tr>
                <td>${modelName}</td>
                <td>${(scores.accuracy * 100).toFixed(1)}%</td>
                <td>${(scores.precision * 100).toFixed(1)}%</td>
                <td>${(scores.recall * 100).toFixed(1)}%</td>
            </tr>
        `;
        labels.push(modelName);
        accuracyData.push(scores.accuracy * 100);
    }

    const canvas = document.getElementById("resultsChart");
    canvas.style.display = "block";

    if (chartInstance) {
        chartInstance.destroy(); // remove old chart before drawing a new one
    }

    chartInstance = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Accuracy (%)",
                data: accuracyData,
                backgroundColor: "#2563eb",
            }],
        },
        options: {
            scales: { y: { beginAtZero: true, max: 100 } },
        },
    });
}

// ===== INITIAL LOAD =====
loadDatasets();