function putGamesToPage(output) {
  var gdict = output.split("\n");
  var buf = "<button onclick=\"ajaxConfig('./list/games', putGamesToPage);\">Refresh list</button>";
  if (gdict[0] !== "") {
    buf += "<p>Choose a game from the list below to start watching<br><br>";
    for (var i=0; i<gdict.length; i++) {
      buf += '<a onclick="actuallyDoSocket2(\''+gdict[i]+'\')">';
      var dsplit = gdict[i].split(",");
      buf += dsplit[1]+" (Black) vs "+dsplit[2]+" (White) ["+dsplit[3]+"s]";
      buf += '</a><br>';
    }
    buf += "</p>";
  } else {
    buf += "<p>There are no games running currently.</p>";
  }
  document.getElementById('player-selection-text').innerHTML = buf;
}

function actuallyDoSocket2(data) {
  dsplit = data.split(",");
  //                 ai1      , ai2      , timelimit, watching
  makeSocketFromPage(dsplit[1], dsplit[2], dsplit[3], dsplit[0]);
}
