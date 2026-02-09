const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8000/api"
    : "https://your-backend-url.onrender.com/api"; // CHANGE THIS to your actual backend URL


function getUser() {
    const u = localStorage.getItem("user");
    return u ? JSON.parse(u) : null;
}

function requireAuth(role) {
    const user = getUser();
    if (!user) {
        window.location.href = "../index.html";
        return;
    }
    if (role && user.role !== role) {
        alert("Unauthorized access");
        window.location.href = "../index.html"; // Redirect to login instead of root
        return;
    }
}

function logout() {
    localStorage.removeItem("user");
    window.location.href = "../index.html";
}
