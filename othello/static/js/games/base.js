function on_load() {
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

    $(".area-log-container").on('click', function () {
        if($(this).children(".area-log").css('display') !== 'none')
            $(this).children(".area-log").hide();
        else
            $(this).children(".area-log").show();
    });
}
