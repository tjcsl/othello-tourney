let rCanvas;
let gameReplay;

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

function convertGameDataToReplay(gameData) {
    if (!gameData || !gameData.moves) {
        return null;
    }

    let replay = {
        black: gameData.black,
        white: gameData.white,
        game: []
    };

    for (let i = gameData.moves.length - 1; i >= 0; i--) {
        let move = gameData.moves[i];
        let board = move.board;
        let blackCount = (board.match(/x/g) || []).length;
        let whiteCount = (board.match(/o/g) || []).length;

        replay.game.push({
            board: board,
            possible: move.possible || [],
            move: move.tile,
            player: move.player,
            black_score: blackCount,
            white_score: whiteCount
        });
    }

    return replay;
}

function drawBoardAtState(gameIndex){
    if(gameIndex === 0){
        drawBoard(rCanvas, gameReplay.game[0].board, gameReplay.game[0].possible, BLACK_NM, rCanvas.animArray, 36);
    }else {
        let player = gameReplay.game[gameIndex].player === 'x' ? BLACK_NM : WHITE_NM;
        drawBoard(rCanvas, gameReplay.game[gameIndex].board, gameReplay.game[gameIndex].possible, player, rCanvas.animArray, gameReplay.game[gameIndex].move)
    }
}

function startMatchReplay(){
    const gameDataElement = document.getElementById('gameData');
    if (!gameDataElement) {
        console.error('No game data found');
        return;
    }

    const gameData = JSON.parse(gameDataElement.textContent);
    if (!gameData) {
        console.error('Invalid game data');
        return;
    }

    gameReplay = convertGameDataToReplay(gameData);
    if (!gameReplay) {
        console.error('Failed to convert game data');
        return;
    }

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

window.onload = function () {
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

    startMatchReplay();
};