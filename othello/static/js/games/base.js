function on_load() {
        $("#input_parseable")
        .click(function () {
                $(this).find("button").click();
            }
        )
        .hover(
            function(){
                $(this).find("label").css({"text-decoration": "underline"});
                $(this).css("cursor", "pointer");
            },
            function () {
                $(this).find("label").css({"text-decoration": "none"});
            }
        );


    $("#input_pretty")
        .click(function () {
                $(this).find("button").click();
            }
        )
        .hover(
            function(){
                $(this).find("label").css({"text-decoration": "underline"});
                $(this).css("cursor", "pointer");
            },
            function () {
                $(this).find("label").css({"text-decoration": "none"});
            }
        );

    $("#downloadHistoryButton")
        .click(function () {
            $("#prettyHistory").text(generate_pretty_history());
            $("#parseableHistory").text(generate_parseable_history());
        })
}