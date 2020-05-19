const DIMENSION = 8;

const WHITE_NM = 0;
const BLACK_NM = 1;

// (need to be the same characters as used by the server)
const EMPTY_CH = '.';
const WHITE_CH = 'o';
const BLACK_CH = 'x';

// CO = "color"
const EMPTY_CO = '#117711';
const WHITE_CO = '#ffffff';
const BLACK_CO = '#000000';

const BORDER_CO    = '#663300';
const HIGHLIGHT_CO = '#fff700';
const GOODMOVE_CO  = '#33ccff';
const LASTMOVE_CO  = '#ff9900';

// Pre-load all images
const WHITE_IMG = new Image();
WHITE_IMG.src = '/static/img/white.png';
const BLACK_IMG = new Image();
BLACK_IMG.src = '/static/img/black.png';

const BORDER_IMG = new Image();
BORDER_IMG.src = '/static/img/board.png';

const TILE_IMG = new Image();
TILE_IMG.src = '/static/img/tile.png';

STONE_IMAGES = [];
for (let i = 0; i < 20; i++) {
  STONE_IMAGES[i] = new Image();
  STONE_IMAGES[i].src = `/static/img/stones/${i}.png`;
}

const OLD_TO_NEW = {11: 0, 12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7, 21: 8, 22: 9, 23: 10, 24: 11, 25: 12, 26: 13, 27: 14, 28: 15, 31: 16, 32: 17, 33: 18, 34: 19, 35: 20, 36: 21, 37: 22, 38: 23, 41: 24, 42: 25, 43: 26, 44: 27, 45: 28, 46: 29, 47: 30, 48: 31, 51: 32, 52: 33, 53: 34, 54: 35, 55: 36, 56: 37, 57: 38, 58: 39, 61: 40, 62: 41, 63: 42, 64: 43, 65: 44, 66: 45, 67: 46, 68: 47, 71: 48, 72: 49, 73: 50, 74: 51, 75: 52, 76: 53, 77: 54, 78: 55, 81: 56, 82: 57, 83: 58, 84: 59, 85: 60, 86: 61, 87: 62, 88: 63}
const NEW_TO_OLD = {0: 11, 1: 12, 2: 13, 3: 14, 4: 15, 5: 16, 6: 17, 7: 18, 8: 21, 9: 22, 10: 23, 11: 24, 12: 25, 13: 26, 14: 27, 15: 28, 16: 31, 17: 32, 18: 33, 19: 34, 20: 35, 21: 36, 22: 37, 23: 38, 24: 41, 25: 42, 26: 43, 27: 44, 28: 45, 29: 46, 30: 47, 31: 48, 32: 51, 33: 52, 34: 53, 35: 54, 36: 55, 37: 56, 38: 57, 39: 58, 40: 61, 41: 62, 42: 63, 43: 64, 44: 65, 45: 66, 46: 67, 47: 68, 48: 71, 49: 72, 50: 73, 51: 74, 52: 75, 53: 76, 54: 77, 55: 78, 56: 81, 57: 82, 58: 83, 59: 84, 60: 85, 61: 86, 62: 87, 63: 88}
const PLAYERS = {
    1: BLACK_CH,
    0: WHITE_CH,
}

let HISTORY;
let RCANVAS;

function init(black, white) {
    let canvas = document.getElementById("canvas");
    let gwidth, gheight;
    gwidth = 1000;
    gheight = 1000;


    let rCanvas = RCANVAS = new RCanvas(canvas, gwidth, gheight);
    rCanvas.resize();

    rCanvas.tomove = BLACK_NM;


    rCanvas.fullbg = new RImg(0, 0, rCanvas.rWidth, rCanvas.rHeight, BORDER_IMG);
    rCanvas.black = document.getElementById("player-black");
    rCanvas.white = document.getElementById("player-white");

    rCanvas.select = new RRect(0,0,1,1, HIGHLIGHT_CO, 0.4);
    rCanvas.lastmove = new RRect(0,0, 1,1, LASTMOVE_CO, 0.4);

    rCanvas.board = [];
    rCanvas.imgBoard = [];
    rCanvas.animArray = [];
    for (let i=0; i<DIMENSION*DIMENSION; i++) {
        rCanvas.board[i] = EMPTY_CH;
        rCanvas.animArray[i] = EMPTY_CH;
    }
    rCanvas.lBSize = 0;

    rCanvas.black_name = `Loading ${black}...`;
    rCanvas.white_name = `Loading ${white}...`;
    drawBoard(rCanvas, rCanvas.board, [], BLACK_NM, rCanvas.animArray);

    return rCanvas;
}

function drawBoard(rCanvas, board_array, possible, tomove, anim_array, move,) {

    let row_col_position = Math.min(rCanvas.rWidth, rCanvas.rHeight);
    let border = row_col_position/(11*DIMENSION+1);
    let square = 10*border;
    let border_and_square = border + square;

    rCanvas.border = border;
    rCanvas.square = square;
    rCanvas.border_and_square = border_and_square;

    rCanvas.objects = [rCanvas.fullbg];

    addTiles(rCanvas, DIMENSION, board_array, border_and_square, border, square);
    let x = move % DIMENSION,
        y = Math.trunc(move/DIMENSION);
    rCanvas.add(new RRect(border_and_square*x+border, border_and_square*y+border, square, square, LASTMOVE_CO, 0.4));
    rCanvas.add(rCanvas.lastmove);

    addPieces(rCanvas, board_array, border_and_square, border, square, anim_array);
    addPossibleMoves(rCanvas, possible, border_and_square, border, square);
    rCanvas.add(rCanvas.select);

    let counts = countPieces(DIMENSION, board_array);
    rCanvas.black.innerHTML = rCanvas.black_name+': '+counts[BLACK_NM].toString();
    rCanvas.white.innerHTML = rCanvas.white_name+': '+counts[WHITE_NM].toString();
    if(tomove === BLACK_NM){
        rCanvas.black.innerHTML = ' (*) '+rCanvas.black.innerHTML;
    }
    else if(tomove === WHITE_NM){
        rCanvas.white.innerHTML = rCanvas.white.innerHTML+' (*) ';
    }
    rCanvas.draw();
    rCanvas.lBSize = DIMENSION;
    startAnimation(rCanvas, anim_array);

}

function addTiles(rCanvas, bSize, bArray, b_and_s, border, square) {
  for (let y=0; y<bSize; y++) {
    for (let x=0; x<bSize; x++) {
      rCanvas.add(new RImg(b_and_s*x+border/2, b_and_s*y+border/2, square+border, square+border, TILE_IMG));
    }
  }
}


function addPieces(rCanvas, board_array, b_and_s, border, square, animArray) {
    if (DIMENSION !== rCanvas.lBSize) {
        rCanvas.imgBoard = [];
        }
    for(let y=0; y<DIMENSION; y++){
        for(let x=0; x<DIMENSION; x++){
            let index = DIMENSION * y + x;
            if (DIMENSION !== rCanvas.lBSize) {
                rCanvas.imgBoard[index] = new RImg(b_and_s * x + border, b_and_s * y + border, square, square, EMPTY_CO, false);
            }
            if (rCanvas.board[index] === EMPTY_CH && board_array[index] === WHITE_CH) {
                animArray[index] = 19; //set anim to full white if piece was just placed (otherwise it would defualt to 0 and flip)
            }else if(rCanvas.board[index] === EMPTY_CH && board_array[index] === BLACK_CH){
                animArray[index] = 2;
            }

            if (board_array[index] === WHITE_CH || board_array[index] === BLACK_CH) {
                rCanvas.imgBoard[index].image = STONE_IMAGES[animArray[index]];
                rCanvas.imgBoard[index].shadow =  true;
            } else if (board_array[index] === EMPTY_CH) {
                rCanvas.imgBoard[index].image = undefined; //TILE_IMG; //tile image doesn't match board
                rCanvas.imgBoard[index].shadow =  false;
            }

            rCanvas.board[index] = board_array[index];
            rCanvas.add(rCanvas.imgBoard[index]);
        }
    }
}

function addPossibleMoves(rCanvas, possible, b_and_s, border, square) {
    console.log(possible);
    possible.forEach((index) => {
        let x = index % DIMENSION,
            y = Math.trunc(index/DIMENSION);
        rCanvas.add(new RRect(b_and_s*x+border, b_and_s*y+border, square, square, GOODMOVE_CO, 0.4));
    });
}


function startAnimation(rCanvas, animArray) {
  let interval = setInterval(function() {
    let stable = true;

    for (let i=0; i<rCanvas.lBSize*rCanvas.lBSize; i++) {
      if (rCanvas.board[i] === BLACK_CH && animArray[i] > 0) {
        animArray[i] -= 1;
        rCanvas.imgBoard[i].image = STONE_IMAGES[animArray[i]];
        stable = false;
      }
      else if (rCanvas.board[i] === WHITE_CH && animArray[i] < 19) {
        animArray[i] += 1;
        rCanvas.imgBoard[i].image = STONE_IMAGES[animArray[i]];
        stable = false;
      }
    }

    if (stable) {
      clearInterval(interval);
    } else {
      rCanvas.draw();
    }
  },16);
}

function highlight_tile(rCanvas, event){
    rCanvas.getMousePos(event);
    let cy = Math.floor(rCanvas.my / rCanvas.border_and_square);
    let cx = Math.floor(rCanvas.mx / rCanvas.border_and_square);
    let ox = rCanvas.select.x;
    let oy = rCanvas.select.y;
    rCanvas.select.x = rCanvas.border_and_square*cx+rCanvas.border;
    rCanvas.select.y = rCanvas.border_and_square*cy+rCanvas.border;
    rCanvas.select.width = rCanvas.square;
    rCanvas.select.height = rCanvas.square;
    if(ox !== rCanvas.select.x || oy !== rCanvas.select.y){
        rCanvas.draw();
    }
}

function place_stone(rCanvas, event, socket){
    highlight_tile(rCanvas, event);
    let olc = rCanvas.lastClicked;
    let cy = Math.floor(rCanvas.my / rCanvas.border_and_square);
    let cx = Math.floor(rCanvas.mx / rCanvas.border_and_square);
    if (cx >= 0 && cx < rCanvas.lBSize && cy >= 0 && cy < rCanvas.lBSize){
      rCanvas.lastClicked = OLD_TO_NEW[cy * (rCanvas.lBSize+2) + cx + 3 + rCanvas.lBSize];
    }
    if (olc === -1) {
        console.log('touched spot ' + rCanvas.lastClicked);
        let resultGood = rCanvas.board[cy * rCanvas.lBSize + cx] === EMPTY_CH && HISTORY[0].possible.includes(rCanvas.lastClicked);
        console.log(resultGood)
        if (resultGood) {
            rCanvas.lastmove.x = rCanvas.border_and_square * cx + rCanvas.border;
            rCanvas.lastmove.y = rCanvas.border_and_square * cy + rCanvas.border;
            rCanvas.lastmove.width = rCanvas.square;
            rCanvas.lastmove.height = rCanvas.square;

            socket.send(JSON.stringify({
                "player": PLAYERS[rCanvas.tomove],
                "move": rCanvas.lastClicked
            }));

        }else{
            rCanvas.lastClicked = -1;
        }
    }
}

function prettyPrint(board) {
    let out = `  1 2 3 4 5 6 7 8\n`;
    for(let w=0;w<8;w++){
        out += `${w+1} `
        for(let h=0;h<8;h++){
            out += `${board[w*8+h]} `;
        }
        out += '\n';
    }
    return out
}

function generate_pretty_history() {
    let out = `${RCANVAS.black_name},${RCANVAS.white_name}\n`;
    for(let i=HISTORY.length-1;i>=0;i--){
        out += prettyPrint(HISTORY[i].board);
        out += `${HISTORY[i].board.split(BLACK_CH).length - 1}-${HISTORY[i].board.split(WHITE_CH).length - 1} ${HISTORY[i].player}\n\n`;
    }
    $("#prettyHistory").text(out);
}

function generate_parseable_history() {
    let out = `${RCANVAS.black_name},${RCANVAS.white_name}\n`;
    for(let i=HISTORY.length-1;i>=0;i--){
        let board = HISTORY[i].board;
        out += `${board} ${HISTORY[i].player} ${HISTORY[i].tile} ${board.split(BLACK_CH).length - 1} ${board.split(WHITE_CH).length - 1}\n`
    }
    $("#parseableHistory").text(out);
}
