girisZorunlu();

const profileForm = document.getElementById("profileForm");
const profileMessage = document.getElementById("message");

function mesajGoster(el, text, type = "info") {
    el.className = `message ${type}`;
    el.textContent = text;
}

profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        sehir: document.getElementById("sehir").value.trim(),
        ilce: document.getElementById("ilce").value.trim() || null,
        arazi_buyuklugu: document.getElementById("arazi_buyuklugu").value ? Number(document.getElementById("arazi_buyuklugu").value) : null,
        arazi_birimi: document.getElementById("arazi_birimi").value || null,
        sulama_turu: document.getElementById("sulama_turu").value || null,
        deneyim_seviyesi: document.getElementById("deneyim_seviyesi").value || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/profil/olustur`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeader()
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Profil oluşturulamadı");
        }

        mesajGoster(profileMessage, "Profil başarıyla oluşturuldu. Dashboard'a yönlendiriliyorsun...", "success");

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 800);

    } catch (error) {
        mesajGoster(profileMessage, error.message, "error");
    }
});