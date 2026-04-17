girisZorunlu();

const globalMessage = document.getElementById("globalMessage");
const accountForm = document.getElementById("accountForm");
const profileForm = document.getElementById("profileForm");
const productForm = document.getElementById("productForm");
const productSubmitBtn = document.getElementById("productSubmitBtn");
const urunListesiBox = document.getElementById("urunListesiBox");
const newProductModeBtn = document.getElementById("newProductModeBtn");
let duzenlenenUrunId = null;
let kullaniciUrunleri = [];

function mesajGoster(text, type = "info") {
    globalMessage.className = `message ${type}`;
    globalMessage.textContent = text;
}

async function apiGet(path) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        headers: {
            ...authHeader()
        }
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

async function apiPut(path, body) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            ...authHeader()
        },
        body: JSON.stringify(body)
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

async function apiPost(path, body) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...authHeader()
        },
        body: JSON.stringify(body)
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

async function apiDelete(path) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "DELETE",
        headers: {
            ...authHeader()
        }
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "İstek başarısız");
    return data;
}

function urunFormunuTemizle() {
    duzenlenenUrunId = null;
    document.getElementById("urun_adi").value = "";
    document.getElementById("urun_cesidi").value = "";
    document.getElementById("ekim_tarihi").value = "";
    document.getElementById("tahmini_hasat_tarihi").value = "";
    document.getElementById("buyume_asamasi").value = "";
    productSubmitBtn.textContent = "Ürün Bilgilerini Kaydet";
}

function urunKartHTML(urun) {
    const urunCesidi = urun.urun_cesidi || "-";
    const buyumeAsamasi = urun.buyume_asamasi || "-";
    const ekimTarihi = urun.ekim_tarihi || "-";
    const hasatTarihi = urun.tahmini_hasat_tarihi || "-";

    return `
        <div class="detail-item">
            <span class="detail-label">${urun.urun_adi}</span>
            <strong class="detail-value">Çeşit: ${urunCesidi} | Aşama: ${buyumeAsamasi}</strong>
            <span class="detail-label">Ekim: ${ekimTarihi} | Hasat: ${hasatTarihi}</span>
            <div class="btn-row" style="margin-top: 10px;">
                <button type="button" class="btn-secondary urun-duzenle-btn" data-id="${urun.id}">Düzenle</button>
                <button type="button" class="btn-danger urun-sil-btn" data-id="${urun.id}">Sil</button>
            </div>
        </div>
    `;
}

function urunListesiniRenderEt() {
    if (!kullaniciUrunleri.length) {
        urunListesiBox.innerHTML = `<p class="empty">Henüz ürün eklenmedi. İlk ürünü aşağıdan ekleyebilirsin.</p>`;
        return;
    }

    urunListesiBox.innerHTML = kullaniciUrunleri
        .slice()
        .reverse()
        .map(urunKartHTML)
        .join("");

    urunListesiBox.querySelectorAll(".urun-duzenle-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const urunId = Number(btn.dataset.id);
            const urun = kullaniciUrunleri.find((u) => u.id === urunId);
            if (!urun) return;

            duzenlenenUrunId = urun.id;
            document.getElementById("urun_adi").value = urun.urun_adi || "";
            document.getElementById("urun_cesidi").value = urun.urun_cesidi || "";
            document.getElementById("ekim_tarihi").value = urun.ekim_tarihi || "";
            document.getElementById("tahmini_hasat_tarihi").value = urun.tahmini_hasat_tarihi || "";
            document.getElementById("buyume_asamasi").value = urun.buyume_asamasi || "";
            productSubmitBtn.textContent = "Seçili Ürünü Güncelle";
        });
    });

    urunListesiBox.querySelectorAll(".urun-sil-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const urunId = Number(btn.dataset.id);
            try {
                await apiDelete(`/urun/sil/${urunId}`);
                if (duzenlenenUrunId === urunId) {
                    urunFormunuTemizle();
                }
                mesajGoster("Ürün silindi.", "success");
                await urunleriYukleVeRenderEt();
            } catch (error) {
                mesajGoster(error.message, "error");
            }
        });
    });
}

async function urunleriYukleVeRenderEt() {
    try {
        kullaniciUrunleri = await apiGet("/urun/listele");
        urunListesiniRenderEt();
    } catch {
        urunListesiBox.innerHTML = `<p class="empty">Ürün listesi alınamadı.</p>`;
    }
}

async function verileriYukle() {
    try {
        const hesap = await apiGet("/hesap/benim-bilgilerim");
        const profil = await apiGet("/profil/benim-profilim");

        document.getElementById("ad_soyad").value = hesap.ad_soyad || "";
        document.getElementById("eposta").value = hesap.eposta || "";

        document.getElementById("sehir").value = profil.sehir || "";
        document.getElementById("ilce").value = profil.ilce || "";
        document.getElementById("arazi_buyuklugu").value = profil.arazi_buyuklugu ?? "";
        document.getElementById("arazi_birimi").value = profil.arazi_birimi || "";
        document.getElementById("sulama_turu").value = profil.sulama_turu || "";
        document.getElementById("deneyim_seviyesi").value = profil.deneyim_seviyesi || "";

        await urunleriYukleVeRenderEt();
    } catch (error) {
        mesajGoster(error.message, "error");
    }
}

accountForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        ad_soyad: document.getElementById("ad_soyad").value.trim(),
        eposta: document.getElementById("eposta").value.trim(),
        sifre: document.getElementById("sifre").value.trim() || null
    };

    try {
        await apiPut("/hesap/guncelle", payload);
        document.getElementById("sifre").value = "";
        mesajGoster("Kullanıcı bilgileri güncellendi.", "success");
    } catch (error) {
        mesajGoster(error.message, "error");
    }
});

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
        await apiPut("/profil/guncelle", payload);
        mesajGoster("Profil bilgileri güncellendi.", "success");
    } catch (error) {
        mesajGoster(error.message, "error");
    }
});

productForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        urun_adi: document.getElementById("urun_adi").value.trim(),
        urun_cesidi: document.getElementById("urun_cesidi").value.trim() || null,
        ekim_tarihi: document.getElementById("ekim_tarihi").value || null,
        tahmini_hasat_tarihi: document.getElementById("tahmini_hasat_tarihi").value || null,
        buyume_asamasi: document.getElementById("buyume_asamasi").value || null
    };

    try {
        if (duzenlenenUrunId) {
            await apiPut(`/urun/guncelle/${duzenlenenUrunId}`, payload);
            mesajGoster("Seçili ürün güncellendi.", "success");
        } else {
            await apiPost("/urun/ekle", payload);
            mesajGoster("Yeni ürün eklendi.", "success");
        }
        urunFormunuTemizle();
        await urunleriYukleVeRenderEt();
    } catch (error) {
        mesajGoster(error.message, "error");
    }
});

newProductModeBtn.addEventListener("click", () => {
    urunFormunuTemizle();
});

verileriYukle();