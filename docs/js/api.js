const API_BASE_URL = "https://jeevanpath-ai-520218359207.asia-south1.run.app";

async function loginUser(mobileNumber, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            mobile_number: mobileNumber,
            password: password
        })
    });

    return await response.json();
}


document.getElementById("loginForm").addEventListener(
    "submit",
    async function (e) {

        e.preventDefault();

        const mobileNumber =
            document.getElementById("mobileNumber").value.trim();

        const password =
            document.getElementById("loginPassword").value;

        try {

            const result =
                await loginUser(mobileNumber, password);

            if (result.error) {

                alert(result.error);
                return;
            }

            sessionStorage.setItem(
                "userName",
                result.full_name
            );

            sessionStorage.setItem(
                "preferredLanguage",
                result.preferred_language || "English"
            );

            window.location.href =
                "pages/dashboard.html";

        } catch (error) {

            console.error(error);

            alert(
                "Unable to connect to the server. Please check if the backend is running."
            );
        }
    }
);


async function signupUser(
    fullName,
    mobileNumber,
    password,
    preferredLanguage
) {

    const response = await fetch(
        `${API_BASE_URL}/signup`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: fullName,
                mobile_number: mobileNumber,
                password: password,
                preferred_language: preferredLanguage
            })
        }
    );

    return await response.json();
}


document.getElementById("registerForm").addEventListener(
    "submit",
    async function (e) {

        e.preventDefault();

        const fullName =
            document.getElementById("regFullName").value.trim();

        const mobileNumber =
            document.getElementById("regMobileNumber").value.trim();

        const password =
            document.getElementById("regPassword").value;

        const preferredLanguage =
            document.getElementById("regLanguage").value;

        try {

            const result = await signupUser(
                fullName,
                mobileNumber,
                password,
                preferredLanguage
            );

            if (result.error) {

                alert(result.error);
                return;
            }

            alert(result.message);

            showLogin();

        } catch (error) {

            console.error(error);

            alert(
                "Unable to connect to the server. Please check if the backend is running."
            );
        }
    }
);