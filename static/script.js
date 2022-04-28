function toggleDescription(id) {
var elem = document.getElementById(id);
    if (elem){
        if (elem.style.display === "none") {
            elem.style.display = "block";
        } else {
            elem.style.display = "none";
        }
    }
}