window.API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8000/api"
    : "https://dbms-project-sem-4.onrender.com/api";


function getUser() {
    const u = localStorage.getItem("user");
    return u ? JSON.parse(u) : null;
}

function requireAuth(role) {
    const user = getUser();
    if (!user) {
        window.location.href = "/frontend/index.html";
        return;
    }
    if (role && user.role !== role) {
        alert("Unauthorized access");
        window.location.href = "/frontend/index.html";
        return;
    }
}

function logout() {
    localStorage.removeItem("user");
    window.location.href = "/frontend/index.html";
}
