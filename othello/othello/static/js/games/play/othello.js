function inBounds(spotx, spoty, bSize) {
  return 0 <= spotx && spotx < bSize && 0 <= spoty && spoty < bSize;
}

function getSpot(spotx, spoty, board, bSize) {
  return board[spoty*bSize+spotx];
}

function findBracket(spotx, spoty, player, board, bSize, dirx, diry) {
  let x = spotx + dirx;
  let y = spoty + diry;
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

function countPieces(dim, bArray) {
  let bCount = 0;
  let wCount = 0;
  for(let i=0; i<dim*dim; i++){
    if (bArray[i] === WHITE_NM) {
      wCount++;
    }
    else if (bArray[i] === BLACK_NM) {
      bCount++;
    }
  }
  let counts = [];
  counts[BLACK_NM] = bCount;
  counts[WHITE_NM] = wCount;
  return counts;
}