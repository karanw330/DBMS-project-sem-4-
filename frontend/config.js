const API_URL = "http://localhost:8000/api";

function getUser() {
    const u = localStorage.getItem("user");
    return u ? JSON.parse(u) : null;
}

function requireAuth(role) {
    const user = getUser();
    if (!user) {
        window.location.href = "../auth/login.html";
        return;
    }
    if (role && user.role !== role) {
        alert("Unauthorized access");
        window.location.href = "../auth/login.html"; // Redirect to login instead of root
        return;
    }
}

function logout() {
    localStorage.removeItem("user");
    window.location.href = "../auth/login.html";
}
