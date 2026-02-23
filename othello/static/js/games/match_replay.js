let rCanvas;
let gameReplay;

let currentIndex = 0;
let playInterval = null;

function logDisabled() {
    $("#black-logs-area").append(`<pre class="err_log">Logs Disabled During Replay</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">Logs Disabled During Replay</pre>`);
}

function clearErrors() {
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

function drawBoardAtState(gameIndex) {
    if (gameIndex === 0) {
        drawBoard(rCanvas, gameReplay.game[0].board, gameReplay.game[0].possible, BLACK_NM, rCanvas.animArray, 36);
    } else {
        let player = gameReplay.game[gameIndex].player === 'x' ? BLACK_NM : WHITE_NM;
        drawBoard(rCanvas, gameReplay.game[gameIndex].board, gameReplay.game[gameIndex].possible, player, rCanvas.animArray, gameReplay.game[gameIndex].move);
    }
}

function startMatchReplay() {
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
    rCanvas.black_name = gameReplay.black;
    rCanvas.white_name = gameReplay.white;

    generateMoveList();
    goToMove(0);

    $(document).on("click", ".move-item", function () {
        stopPlayback();
        let index = parseInt($(this).data("index"));
        if (!isNaN(index)) {
            goToMove(index);
        }
    });

    $("#jumpStart").click(() => {
        stopPlayback();
        goToMove(0);
    });

    $("#prevMove").click(() => {
        stopPlayback();
        goToMove(currentIndex - 1);
    });

    $("#nextMove").click(() => {
        stopPlayback();
        goToMove(currentIndex + 1);
    });

    $("#jumpEnd").click(() => {
        stopPlayback();
        goToMove(gameReplay.game.length - 1);
    });

    $("#playMoves").click(() => {
        if (playInterval) {
            stopPlayback();
        } else {
            startPlayback();
        }
    });

    $(document).keydown(function (e) {
        switch (e.which) {
            case 37: // Left
                stopPlayback();
                goToMove(currentIndex - 1);
                break;
            case 39: // Right
                stopPlayback();
                goToMove(currentIndex + 1);
                break;
            default:
                return;
        }
    });
}

function generateMoveList() {
    const moveList = $("#moveList");
    moveList.empty();

    for (let i = 1; i < gameReplay.game.length; i += 2) {
        const blackMove = gameReplay.game[i];
        const whiteMove = gameReplay.game[i + 1];

        const blackText = blackMove.move === -1 ? "Pass" : blackMove.move;
        const whiteText = whiteMove ? (whiteMove.move === -1 ? "Pass" : whiteMove.move) : "";
        const roundNum = Math.floor(i / 2) + 1;

        moveList.append(`
            <li class="list-group-item d-flex p-1">
                <div class="text-muted mr-2" style="width: 25px; font-size: 0.85rem;">${roundNum}.</div>
                <div class="move-item flex-fill text-center pointer" data-index="${i}" style="cursor:pointer">
                    ${blackText}
                </div>
                <div class="move-item flex-fill text-center pointer" data-index="${i + 1 || ''}" style="cursor:pointer">
                    ${whiteText}
                </div>
            </li>
        `);
    }
}

function highlightMove(index) {
    $(".move-item").removeClass("active bg-primary text-white");
    const activeElem = $(`.move-item[data-index='${index}']`);
    
    if (activeElem.length) {
        activeElem.addClass("active bg-primary text-white");
        
        const container = $("#moveList").parent();
        const scrollPos = container.scrollTop();
        const containerHeight = container.height();
        const elemTop = activeElem.position().top;
        const elemHeight = activeElem.outerHeight();

        if (elemTop < 0 || (elemTop + elemHeight) > containerHeight) {
            container.animate({
                scrollTop: scrollPos + elemTop - (containerHeight / 2)
            }, 100);
        }
    }
}

function goToMove(index) {
    currentIndex = Math.max(0, Math.min(index, gameReplay.game.length - 1));
    drawBoardAtState(currentIndex);
    highlightMove(currentIndex);
}

function startPlayback() {
    if (playInterval) return;

    $("#playMoves").text("⏸");
    playInterval = setInterval(() => {
        if (currentIndex >= gameReplay.game.length - 1) {
            stopPlayback();
            return;
        }
        goToMove(currentIndex + 1);
    }, 1000);
}

function stopPlayback() {
    $("#playMoves").text("▶");
    clearInterval(playInterval);
    playInterval = null;
}

window.onload = function () {
    rCanvas = init("", "");
    $(".canvasContainer").width($("#canvas").width());
    $(window).on('resize', function () {
        rCanvas.resize();
        $(".canvasContainer").width($("#canvas").width());
    });

    function mouseOver(event) {
        highlight_tile(rCanvas, event);
    }

    $(document).on('mousemove', mouseOver);

    startMatchReplay();
};