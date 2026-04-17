girisZorunlu();

const globalMessage = document.getElementById("globalMessage");
const profilBox = document.getElementById("profilBox");
const openAISummaryBox = document.getElementById("openAISummaryBox");
const refreshDashboardBtn = document.getElementById("refreshDashboardBtn");
const saveOpenAIBtn = document.getElementById("saveOpenAIBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const loadingText = document.getElementById("loadingText");
const connectionStatus = document.getElementById("connectionStatus");

const summaryKonum = document.getElementById("summaryKonum");
const summaryHava = document.getElementById("summaryHava");
const summaryUrun = document.getElementById("summaryUrun");
const summaryToprak = document.getElementById("summaryToprak");
const summaryArazi = document.getElementById("summaryArazi");
const summaryRisk = document.getElementById("summaryRisk");

const chatToggleBtn = document.getElementById("chatToggleBtn");
const chatWidget = document.getElementById("chatWidget");
const chatCloseBtn = document.getElementById("chatCloseBtn");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatImageInput = document.getElementById("chatImageInput");
const chatImageName = document.getElementById("chatImageName");
const chatImagePreview = document.getElementById("chatImagePreview");
const chatImageClearBtn = document.getElementById("chatImageClearBtn");

let secilenResim = null;

function mesajGoster(text, type = "info") {
    globalMessage.className = `message ${type}`;
    globalMessage.textContent = text;
    globalMessage.style.display = "block";
}

function mesajGizle() {
    globalMessage.style.display = "none";
}

function yukleniyorGoster(text = "Veriler yükleniyor...") {
    loadingText.textContent = text;
    loadingOverlay.classList.remove("hidden");
}

function yukleniyorGizle() {
    loadingOverlay.classList.add("hidden");
}

function temizDeger(value) {
    if (value === null || value === undefined) return "-";
    if (String(value).toLowerCase() === "null") return "-";
    if (value === "") return "-";
    return value;
}

function riskSinifi(risk) {
    const r = String(risk || "").toLowerCase();
    if (r.includes("yuksek")) return "risk-high";
    if (r.includes("orta")) return "risk-medium";
    if (r.includes("dusuk")) return "risk-low";
    return "risk-neutral";
}

function enYuksekRiskBul(items) {
    if (!items || items.length === 0) return "Belirsiz";

    const risks = items.map(i => String(i.risk_seviyesi || "").toLowerCase());
    if (risks.some(r => r.includes("yuksek"))) return "Yüksek";
    if (risks.some(r => r.includes("orta"))) return "Orta";
    if (risks.some(r => r.includes("dusuk"))) return "Düşük";
    return "Belirsiz";
}

function detailHTML(items) {
    const temiz = items.filter(item => {
        const v = temizDeger(item.value);
        return v !== "-";
    });

    if (temiz.length === 0) {
        return `<p class="empty">Gösterilecek bilgi yok</p>`;
    }

    return temiz.map(item => `
        <div class="detail-item">
            <span class="detail-label">${item.label}</span>
            <strong class="detail-value">${temizDeger(item.value)}</strong>
        </div>
    `).join("");
}

function oneriKartHTML(items, type = "normal") {
    if (!items || items.length === 0) {
        return `<p class="empty">Gösterilecek öneri bulunmuyor</p>`;
    }

    return items.map(item => {
        if (type === "openai-history") {
            return `
                <div class="recommend-card">
                    <div class="recommend-top">
                        <span class="recommend-badge">Model: ${temizDeger(item.kaynak_model)}</span>
                        <span class="recommend-risk risk-neutral">Öncelik: ${temizDeger(item.oncelik_puani)}</span>
                    </div>
                    <h3>${temizDeger(item.ozet)}</h3>
                    <p>${temizDeger(item.genel_durum)}</p>
                    <div class="recommend-note">
                        <strong>Çiftçiye Not:</strong> ${temizDeger(item.ciftciye_not)}
                    </div>
                </div>
            `;
        }

        if (type === "ai_aciklama") {
            return `
                <div class="recommend-card">
                    <div class="recommend-top">
                        <span class="recommend-badge">${temizDeger(item.oneri_turu)}</span>
                        <span class="recommend-risk ${riskSinifi(item.risk_seviyesi)}">${temizDeger(item.risk_seviyesi)}</span>
                    </div>
                    <h3>${temizDeger(item.baslik)}</h3>
                    <p>${temizDeger(item.aciklama)}</p>
                </div>
            `;
        }

        return `
            <div class="recommend-card">
                <div class="recommend-top">
                    <span class="recommend-badge">${temizDeger(item.oneri_turu)}</span>
                    <span class="recommend-risk ${riskSinifi(item.risk_seviyesi)}">${temizDeger(item.risk_seviyesi)}</span>
                </div>
                <h3>${temizDeger(item.baslik)}</h3>
                <p>${temizDeger(item.icerik)}</p>
            </div>
        `;
    }).join("");
}

async function apiGet(path) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        headers: { ...authHeader() }
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

async function apiPost(path, body = null) {
    const options = {
        method: "POST",
        headers: { ...authHeader() }
    };

    if (body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

function summaryGuncelle(ozet) {
    const sehir = temizDeger(ozet?.profil?.sehir);
    const ilce = temizDeger(ozet?.profil?.ilce);
    summaryKonum.textContent = ilce !== "-" ? `${ilce}, ${sehir}` : sehir;

    const sicaklik = temizDeger(ozet?.hava?.sicaklik_max);
    const yagis = temizDeger(ozet?.hava?.yagis_ihtimali_max);
    summaryHava.textContent = sicaklik !== "-" ? `${sicaklik}°C / Yağış %${yagis}` : "-";

    const urunAdlari = (ozet?.urunler || [])
        .map(u => temizDeger(u?.urun_adi))
        .filter(ad => ad !== "-");
    summaryUrun.textContent = urunAdlari.length ? urunAdlari.join(", ") : "-";
    summaryToprak.textContent = temizDeger(ozet?.toprak?.toprak_turu);

    const arazi = temizDeger(ozet?.profil?.arazi_buyuklugu);
    const birim = temizDeger(ozet?.profil?.arazi_birimi);
    summaryArazi.textContent = arazi !== "-" ? `${arazi} ${birim !== "-" ? birim : ""}`.trim() : "-";

    summaryRisk.textContent = enYuksekRiskBul(ozet?.bugunku_oneriler || []);
}

async function dashboardYukle() {
    try {
        connectionStatus.textContent = "Veriler Alınıyor";
        yukleniyorGoster("Dashboard verileri yükleniyor...");

        const ozet = await apiGet("/dashboard/ozet");

        profilBox.innerHTML = detailHTML([
            { label: "Konum", value: temizDeger(ozet?.profil?.ilce) !== "-" ? `${ozet?.profil?.ilce}, ${ozet?.profil?.sehir}` : ozet?.profil?.sehir },
            { label: "Arazi", value: temizDeger(ozet?.profil?.arazi_buyuklugu) !== "-" ? `${ozet?.profil?.arazi_buyuklugu} ${temizDeger(ozet?.profil?.arazi_birimi) !== "-" ? ozet?.profil?.arazi_birimi : ""}`.trim() : "-" },
            { label: "Sulama Türü", value: ozet?.profil?.sulama_turu },
            { label: "Deneyim", value: ozet?.profil?.deneyim_seviyesi },
            {
                label: "Aktif Ürünler",
                value: (ozet?.urunler || []).length
                    ? ozet.urunler.map(u => u.urun_adi).join(", ")
                    : "-"
            },
            { label: "Toprak Türü", value: ozet?.toprak?.toprak_turu }
        ]);

        summaryGuncelle(ozet);

        try {
            const gecmis = await apiGet("/openai-oneri/gecmis");

            if (gecmis.length > 0) {
                openAISummaryBox.innerHTML = detailHTML([
                    { label: "Genel Durum", value: gecmis[0].genel_durum },
                    { label: "Özet", value: gecmis[0].ozet },
                    { label: "Öncelik", value: gecmis[0].oncelik_puani },
                    { label: "Model", value: gecmis[0].kaynak_model }
                ]);
            } else {
                openAISummaryBox.innerHTML = `<p class="empty">Henüz kayıtlı OpenAI özeti yok</p>`;
            }
        } catch {
            openAISummaryBox.innerHTML = `<p class="empty">OpenAI özeti alınamadı</p>`;
        }

        mesajGizle();
        connectionStatus.textContent = "Sistem Hazır";
    } catch (error) {
        mesajGoster(error.message, "error");
        connectionStatus.textContent = "Bağlantı Sorunu";
    } finally {
        yukleniyorGizle();
    }
}

function chatMesajiEkle(icerik, rol = "bot") {
    const div = document.createElement("div");
    div.className = `chat-message ${rol}`;
    div.textContent = icerik;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function chatResimTemizle() {
    secilenResim = null;
    chatImageInput.value = "";
    chatImageName.textContent = "Resim seçilmedi";
    chatImagePreview.src = "";
    chatImagePreview.classList.add("hidden");
    chatImageClearBtn.classList.add("hidden");
}

chatImageInput.addEventListener("change", () => {
    const file = chatImageInput.files?.[0];
    if (!file) {
        chatResimTemizle();
        return;
    }

    if (!file.type.startsWith("image/")) {
        mesajGoster("Lütfen geçerli bir resim dosyası seç.", "error");
        chatResimTemizle();
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        mesajGoster("Resim boyutu en fazla 5 MB olmalı.", "error");
        chatResimTemizle();
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        const result = String(reader.result || "");
        const splitResult = result.split(",");
        if (splitResult.length < 2) {
            mesajGoster("Resim okunamadı.", "error");
            chatResimTemizle();
            return;
        }

        secilenResim = {
            dosya_adi: file.name,
            mime_turu: file.type,
            base64_veri: splitResult[1]
        };

        chatImageName.textContent = file.name;
        chatImagePreview.src = result;
        chatImagePreview.classList.remove("hidden");
        chatImageClearBtn.classList.remove("hidden");
        mesajGizle();
    };
    reader.readAsDataURL(file);
});

chatImageClearBtn.addEventListener("click", chatResimTemizle);

chatToggleBtn.addEventListener("click", () => {
    chatWidget.classList.toggle("hidden");
});

chatCloseBtn.addEventListener("click", () => {
    chatWidget.classList.add("hidden");
});

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const soru = chatInput.value.trim();
    if (!soru) return;

    chatMesajiEkle(secilenResim ? `${soru}\n\n[Resim eklendi: ${secilenResim.dosya_adi}]` : soru, "user");
    chatInput.value = "";

    try {
        yukleniyorGoster("Danışman cevap hazırlıyor...");

        const response = await fetch(`${API_BASE_URL}/danisman/sor`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeader()
            },
            body: JSON.stringify({
                soru,
                resim_base64: secilenResim?.base64_veri || null,
                resim_mime_turu: secilenResim?.mime_turu || null,
                resim_dosya_adi: secilenResim?.dosya_adi || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Danışman cevabı alınamadı");
        }

        chatMesajiEkle(data.cevap, "bot");
        chatResimTemizle();
    } catch (error) {
        chatMesajiEkle(`Hata: ${error.message}`, "bot");
    } finally {
        yukleniyorGizle();
    }
});

refreshDashboardBtn.addEventListener("click", async () => {
    try {
        yukleniyorGoster("Güncel analiz hazırlanıyor...");
        mesajGoster("Dashboard verileri yenileniyor...", "info");
        await apiPost("/dashboard/yenile");
        await dashboardYukle();
        mesajGoster("Dashboard başarıyla yenilendi.", "success");
    } catch (error) {
        mesajGoster(error.message, "error");
    } finally {
        yukleniyorGizle();
    }
});

saveOpenAIBtn.addEventListener("click", async () => {
    try {
        yukleniyorGoster("OpenAI önerisi üretiliyor ve kaydediliyor...");
        mesajGoster("OpenAI önerisi kaydediliyor...", "info");
        await apiPost("/openai-oneri/bugun-kaydet");
        await dashboardYukle();
        mesajGoster("OpenAI önerisi kaydedildi.", "success");
    } catch (error) {
        mesajGoster(error.message, "error");
    } finally {
        yukleniyorGizle();
    }
});

dashboardYukle();