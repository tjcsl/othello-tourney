$("#expandbutton").click(() => {
    $("#linkbar").css({
        "display": function(){
            return $.inArray($(this).css("display"), ["flex", ""]) ? "flex" : "none";
        }
    });
});


$("#home")
    .hover(
        function () {
            $(this).css({"text-decoration": "underline", "cursor": "pointer"});
    },
        function () {
            $(this).css("text-decoration", "none");
    })
    .click(() => {
        window.location.href = "/";
    });