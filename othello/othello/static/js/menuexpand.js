var expandbutton = document.getElementById("expandbutton");
var linkbar = document.getElementById("linkbar");
if (expandbutton) {
  expandbutton.addEventListener("click", function(e) {
    if (linkbar.style.display == "" || linkbar.style.display == "flex") {
      linkbar.style.display = "none"; 
    } else {
      linkbar.style.display = "flex";
    }
  });
}
