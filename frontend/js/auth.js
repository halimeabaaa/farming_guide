function tokenAl() {
    return localStorage.getItem("access_token");
}

function tokenKaydet(token) {
    localStorage.setItem("access_token", token);
}

function tokenSil() {
    localStorage.removeItem("access_token");
}

function authHeader() {
    const token = tokenAl();
    return token ? { "Authorization": `Bearer ${token}` } : {};
}

function girisZorunlu() {
    if (!tokenAl()) {
        window.location.href = "login.html";
    }
}

function cikisYap() {
    tokenSil();
    window.location.href = "login.html";
}