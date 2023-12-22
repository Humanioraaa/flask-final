const registerButton = document.getElementById("register");
const loginButton = document.getElementById("login");
const container = document.getElementById("container");
const registerButtonmobile = document.getElementById("register-mobile");
const loginButtonmobile = document.getElementById("login-mobile");

registerButton.addEventListener("click", () => {
    container.classList.add("right-panel-active");
});

loginButton.addEventListener("click", () => {
    container.classList.remove("right-panel-active");
});

registerButtonmobile.addEventListener("click", () => {
    container.classList.add("right-panel-active");
});

loginButtonmobile.addEventListener("click", () => {
    container.classList.remove("right-panel-active");
});
