
function add_listeners(){
    let rCanvas = init('', '');
    $(".canvasContainer").width($("#canvas").width());
    $(window).on('resize', function () {
        rCanvas.resize();
        $(".canvasContainer").width($("#canvas").width());
    });

    function mouseOver(event){
        highlight_tile(rCanvas, event);
    }

    $(document).on('mousemove', mouseOver);

    $("#downloadModal")
        .on('show.bs.modal', function () {
            $("#prettyHistory").text(generate_pretty_history());
            $("#parseableHistory").text(generate_parseable_history());
            $(document).off('mousemove');
            $(document).off('click');
        })
        .on('hide.bs.modal', function () {
            $(document).on('mousemove', mouseOver);
            $("#downloadHistoryButton").click(function () {
                $("#downloadModal").modal('show');
            });
        });

    $("#pretty_download")
        .click(function () {
            download(`${rCanvas.black_name}_${rCanvas.white_name}.txt`, $("#prettyHistory").text());
        });

    $("#parseable_download")
        .click(function () {
            download(`${rCanvas.black_name}_${rCanvas.white_name}_formatted.txt`, $("#parseableHistory").text());
        });

    $("#replayForm").submit(function (e) {
        if($("#replayFile").val() !== ""){
            $("#uploadModal").modal('hide');
        }
        e.preventDefault();
        e.stopPropagation();
    })
}


window.onload = function () {
    HISTORY = []
    on_load();
    add_listeners();
    $("#uploadModal").modal({backdrop: 'static', keyboard: false})
};