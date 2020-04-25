const DIMENSION = 8;

const EMPTY_NM = 0;
const WHITE_NM = 1;
const BLACK_NM = 2;

// (need to be the same characters as used by the server)
const EMPTY_CH = '.';
const WHITE_CH = 'o';
const BLACK_CH = '@';
const OUTER_CH = '?';

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

// Create lookup dictionaries for easy conversion later one
const CH2NM = {
    EMPTY_CH: EMPTY_NM,
    WHITE_CH: WHITE_NM,
    BLACK_CH: BLACK_NM,
};
const NM2CO = [EMPTY_CO, WHITE_CO, BLACK_CO];


HISTORY = [];
let RCANVAS;

function init(black, white, timelimit, watching) {
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
        rCanvas.board[i] = 0;
        rCanvas.animArray[i] = 0;
    }
    rCanvas.lBSize = 0;

    rCanvas.black_name = `Loading ${black}...`;
    rCanvas.white_name = `Loading ${white}...`;
    drawBoard(rCanvas, DIMENSION, rCanvas.board, BLACK_NM, rCanvas.animArray);

    return rCanvas;
}

function drawBoard(rCanvas, board_array, tomove, anim_array) {
    console.log("drawing board", tomove);

    let row_col_position = Math.min(rCanvas.rWidth, rCanvas.rHeight);
    let border = row_col_position/(11*DIMENSION+1);
    let square = 10*border;
    let border_and_square = border + square;

    rCanvas.border = border;
    rCanvas.square = square;
    rCanvas.border_and_square = border_and_square;

    rCanvas.objects = [rCanvas.fullbg];

    addTiles(rCanvas, DIMENSION, board_array, border_and_square, border, square);
    rCanvas.add(rCanvas.lastmove);

    addPieces(rCanvas, board_array, border_and_square, border, square, anim_array);
    addPossibleMoves(rCanvas, board_array, tomove, border_and_square, border, square);
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
      if (rCanvas.board[index] === EMPTY_NM && board_array[index] === WHITE_NM) {
        animArray[index] = 19; //set anim to full white if piece was just placed (otherwise it would defualt to 0 and flip)
      }

      if (board_array[index] === WHITE_NM || board_array[index] === BLACK_NM) {
        rCanvas.imgBoard[index].image = STONE_IMAGES[animArray[index]];
        rCanvas.imgBoard[index].shadow =  true;
      } else if (board_array[index] === EMPTY_NM) {
        rCanvas.imgBoard[index].image = undefined; //TILE_IMG; //tile image doesn't match board
        rCanvas.imgBoard[index].shadow =  false;
      }

      rCanvas.board[index] = board_array[index];
      rCanvas.add(rCanvas.imgBoard[index]);
    }
  }
}

function addPossibleMoves(rCanvas, board_array, tomove, b_and_s, border, square) {
  for (var y=0; y<DIMENSION; y++) {
    for (var x=0; x<DIMENSION; x++) {
      if (getSpot(x, y, board_array, DIMENSION) === EMPTY_NM) {
          let badspot = true;
          for (let dy=-1; dy<2 && badspot; dy++) {
          for (let dx=-1; dx<2 && badspot; dx++) {
            if (!(dx === 0 && dy === 0) && findBracket(x, y, tomove, board_array, DIMENSION, dx, dy).good) {
              badspot = false;
            }
          }
        }
        if (!badspot) {
          rCanvas.add(new RRect(b_and_s*x+border, b_and_s*y+border, square, square, GOODMOVE_CO, 0.4));
        }
      }
    }
  }
}


function makeFlips(x, y, rCanvas, bSize, bArray, tomove) {
    let good = false;
    let bracketObj;
    for (let dy = -1; dy < 2; dy++) {
        for (let dx = -1; dx < 2; dx++) {
            if (!(dx === 0 && dy === 0)) {
                bracketObj = findBracket(x, y, tomove, bArray, bSize, dx, dy);
                if (bracketObj.good) {
                    let cx = x;
                    let cy = y;
                    good = true;
                    while (cx !== bracketObj.bx || cy !== bracketObj.by) {
                        bArray[cy * bSize + cx] = tomove;
                        cx += dx;
                        cy += dy;
                    }
                }
            }
        }
    }
  return good;
}


function startAnimation(rCanvas, animArray) {
  let interval = setInterval(function() {
    let stable = true;

    for (let i=0; i<rCanvas.lBSize*rCanvas.lBSize; i++) {
      if (rCanvas.board[i] === BLACK_NM && animArray[i] > 0) {
        animArray[i] -= 1;
        rCanvas.imgBoard[i].image = STONE_IMAGES[animArray[i]];
        stable = false;
      }
      else if (rCanvas.board[i] === WHITE_NM && animArray[i] < 19) {
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

function place_stone(rCanvas, event){
    highlight_tile(rCanvas, event);
    let olc = rCanvas.lastClicked;
    let cy = Math.floor(rCanvas.my / rCanvas.border_and_square);
    let cx = Math.floor(rCanvas.mx / rCanvas.border_and_square);
    if (cx >= 0 && cx < rCanvas.lBSize && cy >= 0 && cy < rCanvas.lBSize){
      rCanvas.lastClicked = cy * (rCanvas.lBSize+2) + cx + 3 + rCanvas.lBSize;
    }
    if (olc === -1) {
        console.log('touched spot ' + rCanvas.lastClicked);
        let resultGood = rCanvas.board[cy * rCanvas.lBSize + cx] === EMPTY_NM && makeFlips(cx, cy, rCanvas, rCanvas.lBSize, rCanvas.board, rCanvas.tomove);
        if (resultGood) {
            rCanvas.lastmove.x = rCanvas.border_and_square * cx + rCanvas.border;
            rCanvas.lastmove.y = rCanvas.border_and_square * cy + rCanvas.border;
            rCanvas.lastmove.width = rCanvas.square;
            rCanvas.lastmove.height = rCanvas.square;

            if (rCanvas.tomove === WHITE_NM) {
                rCanvas.animArray[cy * rCanvas.lBSize + cx] = 19;
            }

            drawBoard(rCanvas, rCanvas.board, 3 - rCanvas.tomove, rCanvas.animArray);

        }else{
            rCanvas.lastClicked = -1;
        }
    }
}

function generate_pretty_history() {
    return "pretty history"
}

function generate_parseable_history() {
    return "parsable history"
}
