const API_BASE = "https://ml-forge.onrender.com";

async function apiRequest(endpoint, method = "GET", body = null, useAuth = false) {
    const headers = { "Content-Type": "application/json" };

    if (useAuth) {
        const token = localStorage.getItem("token");
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
    }

    return data;
}