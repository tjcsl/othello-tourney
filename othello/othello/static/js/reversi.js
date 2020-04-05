// Warning: I was bad when I wrote this code, and as such, it has
// hard-to-follow logic and zero comments except for commented-out code.
// As I go over it again, I will try to comment it but no promises.

// Start at the drawBoard function for stuff to make the most sense

// Define magic constants used throughout program
EMPTY_NM = 0;
WHITE_NM = 1;
BLACK_NM = 2;

// (need to be the same characters as used by the server)
EMPTY_CH = '.';
WHITE_CH = 'o';
BLACK_CH = '@';
OUTER_CH = '?';

// CO = "color"
EMPTY_CO = '#117711';
WHITE_CO = '#ffffff';
BLACK_CO = '#000000';

BORDER_CO    = '#663300';
HIGHLIGHT_CO = '#fff700';
GOODMOVE_CO  = '#33ccff';
LASTMOVE_CO  = '#ff9900';

// Pre-load all images
WHITE_IMG = new Image();
WHITE_IMG.src = './static/images/white.png';
BLACK_IMG = new Image();
BLACK_IMG.src = './static/images/black.png';

BORDER_IMG = new Image();
BORDER_IMG.src = './static/images/board.png';

TILE_IMG = new Image();
TILE_IMG.src = './static/images/tile.png';

STONE_IMAGES = [];
for (var i = 0; i < 20; i++) {
  STONE_IMAGES[i] = new Image();
  STONE_IMAGES[i].src = './static/images/stones/'+i+'.png';
}

// Create lookup dictionaries for easy conversion later one
CH2NM = {};
CH2NM[EMPTY_CH] = EMPTY_NM;
CH2NM[WHITE_CH] = WHITE_NM;
CH2NM[BLACK_CH] = BLACK_NM;

NM2CO = [];
NM2CO[EMPTY_NM] = EMPTY_CO;
NM2CO[WHITE_NM] = WHITE_CO;
NM2CO[BLACK_NM] = BLACK_CO;

HISTORY = []
RCANVAS = null;


function addPieces(rCanvas, bSize, bArray, un, bd, sq, animArray) {
  if (bSize !== rCanvas.lBSize) {
    rCanvas.imgBoard = [];
  }
  for(var y=0; y<bSize; y++){
    for(var x=0; x<bSize; x++){
      var index = bSize*y+x;
      if (bSize !== rCanvas.lBSize) {
        var new_image = new RImg(un*x+bd, un*y+bd, sq, sq, EMPTY_CO, false);
        rCanvas.imgBoard[index] = new_image;
      }
      if (rCanvas.board[index] === EMPTY_NM && bArray[index] === WHITE_NM) {
        animArray[index] = 19; //set anim to full white if piece was just placed (otherwise it would defualt to 0 and flip)
      }

      if (bArray[index] === WHITE_NM || bArray[index] === BLACK_NM) {
        rCanvas.imgBoard[index].image = STONE_IMAGES[animArray[index]];
        rCanvas.imgBoard[index].shadow =  true;
      } else if (bArray[index] == EMPTY_NM) {
        rCanvas.imgBoard[index].image = undefined; //TILE_IMG; //tile image doesn't match board
        rCanvas.imgBoard[index].shadow =  false;
      }

      rCanvas.board[index] = bArray[index];
      rCanvas.add(rCanvas.imgBoard[index]);
    }
  }
}

function countPieces(bSize, bArray) {
  var bCount = 0; var wCount = 0;
  for(var i=0; i<bSize*bSize; i++){
    if (bArray[i] === WHITE_NM) {
      wCount++;
    }
    else if (bArray[i] === BLACK_NM) {
      bCount++;
    }
  }
  var counts = [];
  counts[BLACK_NM] = bCount;
  counts[WHITE_NM] = wCount;
  return counts;
}

function inBounds(spotx, spoty, bSize) {
  return 0 <= spotx && spotx < bSize && 0 <= spoty && spoty < bSize;
}

function getSpot(spotx, spoty, board, bSize) {
  return board[spoty*bSize+spotx];
}

function findBracket(spotx, spoty, player, board, bSize, dirx, diry) {
  var x = spotx + dirx;
  var y = spoty + diry;
  opp = 3 - player;

  if (!inBounds(x, y, bSize) || getSpot(x, y, board, bSize) === player) {
    return false;
  }

  while (inBounds(x, y, bSize) && getSpot(x, y, board, bSize) === opp) {
    x += dirx;
    y += diry;
  }
  return {good:(inBounds(x, y, bSize) && getSpot(x, y, board, bSize) === player), bx: x, by: y};
}

function addPossibleMoves(rCanvas, bSize, bArray, tomove, un, bd, sq) {
  for (var y=0; y<bSize; y++) {
    for (var x=0; x<bSize; x++) {
      if (getSpot(x, y, bArray, bSize) === EMPTY_NM) {
        var badspot = true;
        for (var dy=-1; dy<2 && badspot; dy++) {
          for (var dx=-1; dx<2 && badspot; dx++) {
            if (!(dx === 0 && dy === 0) && findBracket(x, y, tomove, bArray, bSize, dx, dy).good) {
              badspot = false;
            }
          }
        }
        if (!badspot) {
          rCanvas.add(new RRect(un*x+bd, un*y+bd, sq, sq, GOODMOVE_CO, 0.4));
        }
      }
    }
  }
}

function addTiles(rCanvas, bSize, bArray, un, bd, sq) {
  for (var y=0; y<bSize; y++) {
    for (var x=0; x<bSize; x++) {
      rCanvas.add(new RImg(un*x+bd/2, un*y+bd/2, sq+bd, sq+bd, TILE_IMG));
    }
  }
}

function makeFlips(x, y, rCanvas, bSize, bArray, tomove) {
  var good = false;
  for (var dy=-1; dy<2; dy++) {
    for (var dx=-1; dx<2; dx++) {
      if (!(dx === 0 && dy === 0)) {
        bracketObj = findBracket(x, y, tomove, bArray, bSize, dx, dy);
        if (bracketObj.good) {
          var cx = x;
          var cy = y;
          good = true;
          while (cx !== bracketObj.bx || cy !== bracketObj.by) {
            bArray[cy*bSize+cx] = tomove;
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
  var interval = setInterval(function() {
    var stable = true;

    for (var i=0; i<rCanvas.lBSize*rCanvas.lBSize; i++) {
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

function drawBoard(rCanvas, bSize, bArray, tomove, animArray){
  console.log('redrawing board');
  // OK so I used two-letter variable names when writing this initially
  // because I was stupid. Here's a key as best as I can figure now:
  // rc == "row-column", should be the length of the square area we are
  //          working in
  // bd == "border", the width of the borders between squares on the board
  // sq == "square", the width/height of a square on the board
  // un == "united border+square", the total width+height of a square
  //          including it's surrouding border
  var rc = Math.min(rCanvas.rWidth, rCanvas.rHeight);
  var bd = rc/(11*bSize+1); //from sq*s+bd*(s+1)=w, sq=10*bd
  var sq = 10*bd;
  var un = bd+sq;

  rCanvas.bd = bd;
  rCanvas.sq = sq;
  rCanvas.un = un;

  // I originally designed the board to be arbitrarily resizable,
  // not entirely sure why, so each time the board updates, we destroy
  // all of the objects on it...
  rCanvas.objects = [];

  // ...and add new ones using the helper methods defined above
  rCanvas.add(rCanvas.fullbg);
  addTiles(rCanvas, bSize, bArray, un, bd, sq);

  rCanvas.add(rCanvas.lastmove);

  addPieces(rCanvas, bSize, bArray, un, bd, sq, animArray);
  addPossibleMoves(rCanvas, bSize, bArray, tomove, un, bd, sq);
  rCanvas.add(rCanvas.select);

  var counts = countPieces(bSize, bArray);
  rCanvas.black.innerHTML = rCanvas.black_name+': '+counts[BLACK_NM].toString();
  rCanvas.white.innerHTML = rCanvas.white_name+': '+counts[WHITE_NM].toString();
  if(tomove === BLACK_NM){
    rCanvas.black.innerHTML = ' (*) '+rCanvas.black.innerHTML;
  }
  else if(tomove === WHITE_NM){
    rCanvas.white.innerHTML = rCanvas.white.innerHTML+' (*) ';
  }
  rCanvas.draw();
  rCanvas.lBSize = bSize;
  startAnimation(rCanvas, animArray);
}

function bStringToBArray(bString){
  bString = bString.replace(/\?/g, '');
  var bArray = [];
  for(var i=0; i<bString.length; i++){
    bArray[i] = CH2NM[bString.charAt(i)];
  }
  return bArray;
}

function resize(canvas, gWidth, gHeight){
  var availWidth = canvas.parentNode.offsetWidth*9/10;
  var availHeight = (window.innerHeight - canvas.parentNode.offsetTop)*9/10;
  if(availWidth*gHeight < availHeight*gWidth){
    canvas.width = availWidth;
    canvas.height = canvas.width * gHeight / gWidth;
  }
  else{
    canvas.height = availHeight;
    canvas.width = canvas.height * gWidth / gHeight;
  }
}

// Begin history downloading code (not great in another file b/c it uses
// so much stuff from this file, yeah it sucks)

var tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function replaceTag(tag) {
    return tagsToReplace[tag] || tag;
}

function safe_tags_replace(str) {
    return str.replace(/[&<>]/g, replaceTag);
}

function add_to_history(data) {
  HISTORY[HISTORY.length] = data;
}

function _prettyPrint(bArray, bSize) {
  var out = " ";
  for (var i=1; i<=bSize; i++) {
    out += " " + i;
  }
  out += "\r\n";
  for (var y=1; y<bSize+1; y++) {
    out += y;
    for (var x=1; x<bSize+1; x++) {
      out += " " + bArray[y*(bSize+2)+x];
    }
    out += "\r\n";
  }
  return out;
}

function prettyPrint(data, olddata, bSize) {
  var out = "";
  out += _prettyPrint(data.board, bSize);
  counts = countPieces(bSize, bStringToBArray(data.board));
  out += counts[BLACK_NM]+"-"+counts[WHITE_NM]+"\r\n\r\n";
  return out;
};

function uglyPrint(bArray, bSize) {
  return bArray.join("");
};

function parseablePrint(data, olddata, bSize) {
  // looks like the data is already in a pretty good format?
  console.log(olddata);
  var move = "-";
  if (olddata !== undefined) {
    for (var cx=1; cx<bSize+1; cx++) {
      for (var cy=1; cy<bSize+1; cy++) {
        var index = cy*(bSize+2)+cx;
        if (olddata.board[index] === EMPTY_CH && data.board[index] !== EMPTY_CH) {
          move = index;
        }
      }
    }
  }
  var counts = countPieces(bSize, bStringToBArray(data.board));

  var out = data.board;
  out += " "+ data.tomove;
  out += " ";
  out += counts[BLACK_NM]-counts[WHITE_NM];
  out += " " + move + "\r\n"
  return out;
};

function printHistory(history, ai_name1, ai_name2, bSize, printFunc) {
  var out = ai_name1 + "," + ai_name2 + "\r\n";
  var counts;
  console.log("Starting to print history");
  for (var i=0; i<history.length; i++) {
    out += printFunc(history[i], history[i-1], bSize);
  }
  return out;
};

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
};

function prettyHistoryDownload() {
  var text = printHistory(HISTORY, RCANVAS.black_name, RCANVAS.white_name, RCANVAS.lBSize, prettyPrint);
  download(RCANVAS.black_name+"_"+RCANVAS.white_name+".txt", text);
}

function parseableHistoryDownload() {
  var text = printHistory(HISTORY, RCANVAS.black_name, RCANVAS.white_name, RCANVAS.lBSize, parseablePrint);
  download(RCANVAS.black_name+"_"+RCANVAS.white_name+"_formatted.txt", text);
}

function historyDownload() {
  var format = document.querySelector('input[name="downloadFormat"]:checked').value;
  console.log(format);
  if (format === "pretty") { prettyHistoryDownload(); }
  else if (format === "parseable") { parseableHistoryDownload(); }
}

function init(socket, ai_name1, ai_name2, timelimit, watching){
  document.getElementById('gameContainer').style.display = "flex";
  document.getElementById('player-selection-text').style.display = "none";

  var canvas = document.getElementById('canvas');
  var gWidth = 1000;
  var gHeight = 1000;

  var rCanvas = new RCanvas(canvas, gWidth, gHeight);
  RCANVAS = rCanvas;
  rCanvas.resize();
  window.addEventListener('resize', function(){
    rCanvas.resize();
  });

  rCanvas.fullbg = new RImg(
    0, 0,
    rCanvas.rWidth, rCanvas.rWidth,
    BORDER_IMG
  );
  rCanvas.black = document.getElementById("player-black");
  rCanvas.white = document.getElementById("player-white");

  var selected = new RRect(0, 0, 1, 1, HIGHLIGHT_CO, 0.4);
  rCanvas.select = selected;

  var lastmove = new RRect(0, 0, 1, 1, LASTMOVE_CO, 0.4);
  rCanvas.lastmove = lastmove;

  rCanvas.board = [];
  rCanvas.imgBoard = [];
  var animArray = []
  var dSize = 8;
  for (var i=0; i<dSize*dSize; i++) {
    rCanvas.board[i] = 0;
    animArray[i] = 0;
  }
  rCanvas.lBSize = 0;

  rCanvas.black_name = "Loading "+ai_name1+"...";
  rCanvas.white_name = "Loading "+ai_name2+"...";
  drawBoard(rCanvas, dSize, rCanvas.board, BLACK_NM, animArray);

  function augmentedMouseMove(event) {
    rCanvas.getMousePos(event);
    var cy = Math.floor(rCanvas.my / rCanvas.un);
    var cx = Math.floor(rCanvas.mx / rCanvas.un);
    var ox = selected.x;
    var oy = selected.y;
    selected.x = rCanvas.un*cx+rCanvas.bd;
    selected.y = rCanvas.un*cy+rCanvas.bd;
    selected.width = rCanvas.sq;
    selected.height = rCanvas.sq;
    if(ox !== selected.x || oy !== selected.y){
      rCanvas.draw();
    }
  }
  document.addEventListener('mousemove', augmentedMouseMove);

  clickHandler = function(event){
    augmentedMouseMove(event);
    var olc = rCanvas.lastClicked;
    var cy = Math.floor(rCanvas.my / rCanvas.un);
    var cx = Math.floor(rCanvas.mx / rCanvas.un);
    if (cx >= 0 && cx < rCanvas.lBSize && cy >= 0 && cy < rCanvas.lBSize){
      rCanvas.lastClicked = cy * (rCanvas.lBSize+2) + cx + 3 + rCanvas.lBSize;
    }
    if (olc === -1){
      console.log('touched spot '+rCanvas.lastClicked);
      var resultGood = rCanvas.board[cy*rCanvas.lBSize+cx]===EMPTY_NM && makeFlips(cx, cy, rCanvas, rCanvas.lBSize, rCanvas.board, rCanvas.tomove);
      if (resultGood) {
        lastmove.x = rCanvas.un*cx+rCanvas.bd;
        lastmove.y = rCanvas.un*cy+rCanvas.bd;
        lastmove.width = rCanvas.sq;
        lastmove.height = rCanvas.sq;

        if (rCanvas.tomove === WHITE_NM) { animArray[cy*rCanvas.lBSize+cx] = 19; }

        drawBoard(rCanvas, rCanvas.lBSize, rCanvas.board, 3 - rCanvas.tomove, animArray);

        console.log('sending move');
        socket.send(JSON.stringify({
          'type': "movereply",
          'move': rCanvas.lastClicked
        }));
      } else {
        rCanvas.lastClicked = -1;
      }
    }
  };

  on_reply = function(data){
    rCanvas.black_name = data.black;
    rCanvas.white_name = data.white;
    rCanvas.tomove = CH2NM[data.tomove];
    add_to_history(data);
    var bArray = bStringToBArray(data.board);
    var bSize = parseInt(data.bSize);
    if (bSize === rCanvas.lBSize) {
      for (var cx=0; cx<bSize; cx++) {
        for (var cy=0; cy<bSize; cy++) {
          var index = cy*bSize+cx;
          if (rCanvas.board[index] === EMPTY_NM && bArray[index] !== EMPTY_NM) {
            lastmove.x = rCanvas.un*cx+rCanvas.bd;
            lastmove.y = rCanvas.un*cy+rCanvas.bd;
            lastmove.width = rCanvas.sq;
            lastmove.height = rCanvas.sq;
          }
        }
      }
    }
    drawBoard(rCanvas, bSize, bArray, CH2NM[data.tomove], animArray);
  }

  on_moverequest = function(data){
    console.log('move requested');
    rCanvas.lastClicked = -1;
  };

  on_gameend = function(data){
    //Clean up tasks, end socket
    document.removeEventListener('click', clickHandler);
    socket.close();
    // Handle winner conditions
    var black_text = "";
    var white_text = "";
    if (data.winner === BLACK_CH) {
      black_text = " [Winner] " + black_text;
      if (data.forfeit) {
        white_text = " [Errored] " + white_text;
        if(data.err_msg){
            document.getElementById('text').innerHTML = '<pre><code>' + data.err_msg + '</code></pre>';
            return;
        }
      }
    } else if (data.winner === WHITE_CH) {
      white_text = " [Winner] " + white_text;
      if (data.forfeit) {
        black_text = " [Errored] " + black_text;
        if(data.err_msg){
            document.getElementById('text').innerHTML = '<pre><code>' + data.err_msg + '</code></pre>';
            return;
        }
      }
    } else if (data.winner === EMPTY_CH) {
      black_text = "[Tie] " + black_text;
      white_text = "[Tie] " + white_text;
    } else {
      if (data.forfeit) {
        black_text = " [Game Over] " + black_text;
        white_text = " [Game Over] " + white_text;
      } else {
        black_text = " [Server error] " + black_text;
        white_text = " [Server error] " + white_text;
      }
    }
    //Add text signifying that the game is over
    rCanvas.black.innerHTML = black_text + rCanvas.black.innerHTML;
    rCanvas.white.innerHTML = rCanvas.white.innerHTML + white_text;
  };

  on_gameerror = function (data) {
    document.getElementById("err_log").innerHTML += safe_tags_replace(data.error + "\n");
  };

  socket.onmessage = function(message) {
    // Decode the JSON
    console.log("Got websocket message " + message.data);
    var data = JSON.parse(message.data);
    // Handle errors
    //if (data.error) {
    //  alert(data.error);
    //  return;
    //}
    switch (data.type) {
      case 'reply':
        on_reply(data);
        break;
      case 'moverequest':
        on_moverequest(data);
        break;
      case 'gameend':
        on_gameend(data);
        break;
      case 'gameerror':
        on_gameerror(data);
        break;
      default:
        console.log("Unsupported message type "+ data.msg_type);
        return;
    }
  }

  socket.onopen = function() {
    console.log("Did connect to socket");
    if (!watching) {
      document.addEventListener('click', clickHandler);
    }
  }
  socket.onclose = function() {
    console.log("Did disconnect from socket");
    on_gameerror({error: "[Disconnected from server]"});
  }
}

function makeSocketFromPage(ai_name1, ai_name2, timelimit, watching){
  var socket;
  if (watching) {
    socket = new WebSocket(PATH+"watch/watching="+watching);
  } else {
    socket = new WebSocket(PATH+"play/black="+ai_name1+",white="+ai_name2+",t="+timelimit);
  }

  console.log('made socket');
  init(socket, ai_name1, ai_name2, timelimit, watching);
  console.log('finished initing socket');
}
