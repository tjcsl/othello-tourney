const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws";
const PATH = `${PROTOCOL}://${window.location.host}`;


function add_listeners(socket){
    let rCanvas = init(game.black, game.white, 0,0);

    window.addEventListener('resize', function() { // Makes board reactive to browser size changes
        rCanvas.resize();
    });

    document.addEventListener('mousemove', (event) => { // Highlight tile underneath cursor
        highlight_tile(rCanvas, event);
    });

    socket.onopen = () => {
        console.log("socket is connected");
        document.addEventListener('click', (event) => {
            rCanvas.lastClicked = -1;
            place_stone(rCanvas, event);
        });
    };

    socket.onclose = function () {
        console.log("disconnected from socket");
        $("#err_log").text("[Disconnected from socket]")
    };

    socket.onmessage = function (message) {
        let data = JSON.parse(message.data);
        switch(data.type){
            case 'game.log':
                console.log(`LOG: ${data.message}`);
                break;
            case 'game.update':
                console.log(`STATE: ${data.new_move.board}, ${data.game_over}, ${JSON.stringify(data.new_move)}`);
                if(data.new_move.tile === -10){
                    console.log("starting game");
                    rCanvas.black_name = data.black;
                    rCanvas.white_name = data.white;
                    console.log(JSON.stringify(data))
                    drawBoard(rCanvas, data.new_move.board, data.new_move.possible, BLACK_NM, rCanvas.animArray);
                }else{
                    console.log("got move");
                }
                break
            default:
                console.error(`Invalid message type: ${data.type}`);
                return;
        }
    }
}


window.onload = function () {
    on_load();
    let socket;
    socket = is_watching ? new WebSocket(`${PATH}/watch/${game.id}`) : new WebSocket(`${PATH}/play/${game.id}`);
    add_listeners(socket);
};