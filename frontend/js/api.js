const API_BASE_URL = "http://127.0.0.1:8000";

async function loginUser(mobileNumber, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            mobile_number: mobileNumber,
            password: password
        })
    });
    return await response.json();
}

document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const mobileNumber = document.getElementById("mobileNumber").value;
    const password = document.getElementById("loginPassword").value;
    const result = await loginUser(mobileNumber, password);

    if (result.error) {
        alert(result.error);
    } else {
        sessionStorage.setItem("userName", result.full_name);
        window.location.href = "pages/dashboard.html";
    }
});

async function signupUser(fullName, mobileNumber, password, preferredLanguage) {
    const response = await fetch(`${API_BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            full_name: fullName,
            mobile_number: mobileNumber,
            password: password,
            preferred_language: preferredLanguage
        })
    });
    return await response.json();
}

document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const fullName = document.getElementById("regFullName").value;
    const mobileNumber = document.getElementById("regMobileNumber").value;
    const password = document.getElementById("regPassword").value;
    const preferredLanguage = document.getElementById("regLanguage").value;
    const result = await signupUser(fullName, mobileNumber, password, preferredLanguage);

    if (result.error) {
        alert(result.error);
    } else {
        alert(result.message);
        showLogin();
    }
});