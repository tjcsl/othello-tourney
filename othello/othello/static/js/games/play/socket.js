const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws";
const PATH = `${PROTOCOL}://${window.location.host}/ws`;


function add_listeners(socket){
    let rCanvas = init("Yourself", "Yourself", 0,0);

    window.addEventListener('resize', () => { // Makes board reactive to browser size changes
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
        console.log("received websocket message", message.data);
        let data = JSON.parse(message.data);
        console.log(data);
        switch(data.type){
            case 'log':
                console.log(data.message);
                break;
            default:
                console.error(`Invalid message type: ${data.type}`);
                return;
        }
    }
}


window.onload = function () {
    on_load();
    let socket;
    socket = new WebSocket(`${PATH}/play/${game.id}/`);
    add_listeners(socket);
};