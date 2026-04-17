const registerForm = document.getElementById("registerForm");
const registerMessage = document.getElementById("message");

function mesajGoster(el, text, type = "info") {
    el.className = `message ${type}`;
    el.textContent = text;
}

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        ad_soyad: document.getElementById("fullName").value.trim(),
        eposta: document.getElementById("regEmail").value.trim(),
        sifre: document.getElementById("regPassword").value.trim()
    };

    try {
        const response = await fetch(`${API_BASE_URL}/kimlik/kayit-ol`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Kayıt başarısız");
        }

        mesajGoster(registerMessage, "Kayıt başarılı. Giriş sayfasına yönlendiriliyorsun...", "success");

        setTimeout(() => {
            window.location.href = "login.html";
        }, 900);

    } catch (error) {
        mesajGoster(registerMessage, error.message, "error");
    }
});