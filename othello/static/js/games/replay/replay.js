let rCanvas;
let gameReplay;

function noFileUploaded(){
    disableButtons();
    $("#black-logs-area").append(`<pre class="err_log">No Game File Uploaded</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">No Game File Uploaded</pre>`);
}

function errorParsing(){
    disableButtons();
    $("#black-logs-area").append(`<pre class="err_log">Error Parsing File at Specified Format</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">Error Parsing File at Specified Format</pre>`);
}

function logDisabled(){
    $("#black-logs-area").append(`<pre class="err_log">Logs Disabled During Replay</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">Logs Disabled During Replay</pre>`);
}

function enableButtons(){
    $("#stepForward").prop("disabled", false);
    $("#stepBack").prop("disabled", false);
}

function disableButtons(){
    $("#stepForward").prop("disabled", true);
    $("#stepBack").prop("disabled", true);
}

function clearErrors(){
    $("pre.err_log").remove();
}

function validateMetrics(board, player, move, bs, ws){
    if(board.length !== 64)
        return false;
    if(player !== '-' && player !== 'x' && player !== 'o')
        return false;
    if((isNaN(move) || move < 0 || move > 63) && move !== -10)
        return false;
    if(isNaN(bs) || bs < 0 || bs > 64)
        return false;
    return !(isNaN(ws) || ws < 0 || ws > 64);

}

function parseReplay(text, isParseable){
    let replay = {};
    const lines = text.split('\n');

    const players = lines[0].split(',');
    if(players.length !== 2)
        return false;
    replay.black = players[0];
    replay.white = players[1];
    replay.game = [];

    if(isParseable){
        for(let i=1;i<lines.length-1;i++){
            let state = lines[i].split(" ");
            let player = state[1];
            let move = parseInt(state[2]);
            let bs = parseInt(state[3]);
            let ws = parseInt(state[4]);

            let possible = [];
            for(let c=0;c<state[0].length;c++){
                if(state[0][c] === "*"){
                    possible.push(c);
                    state[0] = state[0].substring(0, c) + "." + state[0].substring(c+1);
                }
            }

            if(!validateMetrics(state[0], player, move, bs, ws))
                return false;

            replay.game.push({board: state[0], possible: possible, move: move, player: player, black_score: bs, white_score: ws});
        }
    }else{
        for(let i=2;i<lines.length-1;i+=11){
            let board = "";
            let scoreline = lines[i+8].split(' ');
            if(scoreline.length !== 4)
                return false;

            let scores = scoreline[0].split('-');
            if(scores.length !== 2)
                return false;

            let bs = parseInt(scores[0]);
            let ws = parseInt(scores[1]);
            let player = scoreline[1];
            let move = parseInt(scoreline[3]);

            for(let c=i;c<i+8;c++){
                let row = lines[c].substring(1).split(' ').join('');
                if(row.length !== 8)
                    return false;
                board = board+row;
            }

            let possible = [];
            for(let c=0;c<board.length;c++){
                if(board[c] === "*"){
                    possible.push(c);
                    board = board.substring(0, c) + "." + board.substring(c+1);
                }
            }

            if(!validateMetrics(board, player, move, bs, ws))
                return false;

            replay.game.push({board: board, possible: possible, move: move, player: player, black_score: bs, white_score: ws});
        }
    }
    return replay;
    // { black: name, white: name, game: [{board: '', possible: [int], move: int, player: char, black_score: int, white_score: int}]}
}

function drawBoardAtState(gameIndex){
    if(gameIndex === 0){
        drawBoard(rCanvas, gameReplay.game[0].board, gameReplay.game[0].possible, BLACK_NM, rCanvas.animArray, 36);
    }else {
        let player = gameReplay.game[gameIndex].player === BLACK_CH ? BLACK_NM : WHITE_NM;
        drawBoard(rCanvas, gameReplay.game[gameIndex].board, gameReplay.game[gameIndex].possible, player, rCanvas.animArray, gameReplay.game[gameIndex].move)
    }
}

function startReplay(){
    if(!gameReplay)
        return errorParsing();
    logDisabled();
    enableButtons();
    rCanvas.black_name = gameReplay.black;
    rCanvas.white_name = gameReplay.white;
    drawBoard(rCanvas, gameReplay.game[0].board, gameReplay.game[0].possible, BLACK_NM, rCanvas.animArray, 36);

    let gameIndex = 0;
    $("#stepForward").click(function (){
        gameIndex = Math.min(++gameIndex, gameReplay.game.length-1);
        drawBoardAtState(gameIndex);
    })
    $("#stepBack").click(function (){
        gameIndex = Math.max(--gameIndex, 0);
        drawBoardAtState(gameIndex);
    })

}

async function handleUpload(){
    rCanvas = init("", "");
    const isParseable = $("#replayParseable").is(":checked");

    const file = document.getElementById("replayFile").files[0];
    if(!file){
        noFileUploaded();
        gameReplay = false;
        return;
    }
    const text = await file.text();

    try{
        gameReplay = parseReplay(text, isParseable);
    }catch (e){
        errorParsing();
    }
    startReplay();
}

window.onload = function () {
    $("#replayModal").modal('show');
    
    rCanvas = init("", "");
    $(".canvasContainer").width($("#canvas").width());
    $(window).on('resize', function () {
        rCanvas.resize();
        $(".canvasContainer").width($("#canvas").width());
    });

    function mouseOver(event){
        highlight_tile(rCanvas, event);
    }

    $(document).on('mousemove', mouseOver);
    $("#submitReplay").click(handleUpload);
};
