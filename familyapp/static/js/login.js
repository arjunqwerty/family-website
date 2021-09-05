function changeRegister() {
    document.getElementById("loginbox").classList.add("wow");
    document.getElementById("loginbox").classList.add("animated");
    document.getElementById("loginbox").classList.remove("fadeInLeft");
    document.getElementById("loginbox").classList.add("fadeOutLeft");
    document.getElementById("loginbox").children.item(0).children.item(1).children.item(0).children.item(1).value = "";
    document.getElementById("loginbox").children.item(0).children.item(1).children.item(1).children.item(1).value = "";
    document.getElementById("registerbox").classList.remove("fadeOutRight");
    document.getElementById("registerbox").classList.add("fadeInRight");
    document.getElementById("loginbox").addEventListener("transitionend", displayNone("loginbox"));
    document.getElementById("registerbox").addEventListener("transitionstart", displayInitial("registerbox"));
}
function changeLogin() {
    document.getElementById("registerbox").classList.remove("fadeInRight");
    document.getElementById("registerbox").classList.add("fadeOutRight");
    document.getElementById("registerbox").children.item(0).children.item(1).children.item(0).children.item(1).value = "";
    document.getElementById("registerbox").children.item(0).children.item(1).children.item(1).children.item(1).value = "";
    document.getElementById("registerbox").children.item(0).children.item(1).children.item(2).children.item(1).value = "";
    document.getElementById("loginbox").classList.remove("fadeOutLeft");
    document.getElementById("loginbox").classList.add("fadeInLeft");
    document.getElementById("registerbox").addEventListener("transitionend", displayNone("registerbox"));
    document.getElementById("loginbox").addEventListener("transitionstart", displayInitial("loginbox"));
}
function displayNone(elementid) {
    document.getElementById(elementid).style.display = "none";
}
function displayInitial(elementid) {
    document.getElementById(elementid).style.display = "initial";
}
