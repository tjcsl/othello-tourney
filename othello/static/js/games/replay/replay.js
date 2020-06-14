
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

    $("#replayFile").on('change', function (e) {
        let reader = new FileReader();
        reader.onload = function () {
            try{
                parseReplay(reader.result);
            }catch (e) {
                alert("Could not parse replay file, are you sure this file is parseable?")
            }
        };
        reader.readAsText($(this).prop('files')[0], "UTF-8");
        $("#uploadModal").modal('hide');
    })
}

function parseReplay(file){
    let moves = file.trim().split('\n');
    let players = moves[0].split(",")
    for(let i=1;i<moves.length;i++) {
        let parts = moves[i].split(" ");
        let possible = [];
        let board = parts[0];
        for(let j=0;j<parts[0].length;j++){
            if(parts[0][j] === "*") {
                possible.push(j);
                board = board.replaceAt(j, ".")
            }
        }
        HISTORY.unshift({
            board: board,
            player: parts[1],
            tile: parts[2],
            possible: possible
        })
    }
    return players;
}


window.onload = function () {
    HISTORY = []
    on_load();
    add_listeners();
    $("#uploadModal").modal({backdrop: 'static', keyboard: false})
};