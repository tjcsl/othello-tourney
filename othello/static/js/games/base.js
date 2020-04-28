function on_load() {
    if($(window).width() <= 1200){ // Stack logging divs below board if on small screen, else keep them side-by-side
        $("#gameContainer div:first").insertAfter($("#gameContainer div:last"));
    }
    $("#input_parseable")
        .hover(
            function(){
                $(this).find("label").css({"text-decoration": "underline"});
                $(this).css("cursor", "pointer");
            },
            function () {
                $(this).find("label").css({"text-decoration": "none"});
            });


    $("#input_pretty")
        .hover(
            function(){
                $(this).find("label").css({"text-decoration": "underline"});
                $(this).css("cursor", "pointer");
            },
            function () {
                $(this).find("label").css({"text-decoration": "none"});
            });
}
