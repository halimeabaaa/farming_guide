const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("message");

function mesajGoster(el, text, type = "info") {
    el.className = `message ${type}`;
    el.textContent = text;
}

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
        const body = new URLSearchParams();
        body.append("username", email);
        body.append("password", password);

        const response = await fetch(`${API_BASE_URL}/kimlik/giris-yap`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Giriş başarısız");
        }

        tokenKaydet(data.access_token);

        // Ilk giris mi kontrol et
        const profilResponse = await fetch(`${API_BASE_URL}/profil/benim-profilim`, {
            headers: {
                ...authHeader()
            }
        });

        if (profilResponse.status === 404) {
            mesajGoster(loginMessage, "İlk giriş algılandı. Profil oluşturma ekranına yönlendiriliyorsun...", "success");
            setTimeout(() => {
                window.location.href = "onboarding.html";
            }, 700);
            return;
        }

        if (!profilResponse.ok) {
            const profilData = await profilResponse.json();
            throw new Error(profilData.detail || "Profil kontrolü yapılamadı");
        }

        mesajGoster(loginMessage, "Giriş başarılı. Dashboard'a yönlendiriliyorsun...", "success");

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 700);

    } catch (error) {
        mesajGoster(loginMessage, error.message, "error");
    }
});