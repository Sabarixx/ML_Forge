const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault(); // stops the page from refreshing on form submit

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorMsg = document.getElementById("errorMsg");

        try {
            const data = await apiRequest("/auth/login", "POST", { email, password });
            localStorage.setItem("token", data.access_token);
            window.location.href = "dashboard.html"; // redirect after login
        } catch (err) {
            errorMsg.textContent = err.message;
        }
    });
}

const signupForm = document.getElementById("signupForm");
if (signupForm) {
    signupForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorMsg = document.getElementById("errorMsg");

        try {
            const data = await apiRequest("/auth/signup", "POST", { email, password });
            localStorage.setItem("token", data.access_token);
            window.location.href = "dashboard.html";
        } catch (err) {
            errorMsg.textContent = err.message;
        }
    });
}