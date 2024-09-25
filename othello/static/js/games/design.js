function showYourselfHelp(val, selector){
    val === "1" ? $(selector).show() : $(selector).hide();
}

function helps(){
    let players = ["black", "white"];
    for(let i = 0;i<players.length;i++) {
        if ($(`#id_${players[i]}`).val() === "1") {
            $(`#${players[i]}-help`).show()
        } else {
            $(`#${players[i]}-help`).hide();
        }
    }
}

function winnerTippy(elem){
    const instance = tippy(elem);
    instance.setProps({
        content: "This player placed first in a previous Othello tournament",
        placement: 'right'
    })
    instance.show(50);
}

function tournament_winner(data, escape){
    if(data.text.includes("T-")){
        return `<div onmouseenter="winnerTippy(this)"><p>&#x1F31F; ${escape(data.text)}</p></div>`;
    }
    return `<div>${escape(data.text)}</div>`;
}

// Sorry for this terrible code
function playerSort(el) {
    let username = el.text;
    let winner = false;
    if(el.text.includes("T-")){
        winner = true;
        username = username.replace(" ", "").substring(2);
    }
    if(el.text.includes("(")){
        username = el.text.match(/\(([^)]+)\)/)[1];
    }
    // sort descending by year, if it is part of the username, and then alphabetically
    if(username.match(/^\d{4}/)){
        // first four numbers are year
        let year = username.substring(0, 4);
        year = 3000 - parseInt(year);
        username = year + username.substring(4);
    }
    if (winner){
        username = "0" + username;
    }
    return username;
}

window.onload = function () {
    helps()
    let players = $("#id_black").children().toArray();
    players = players.map(function(el) {
        return {text: el.text, username: playerSort(el)};
    });
    $("#id_black").selectize({
        options: players,
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#black-help");
        },
        sortField: [{'field': 'username', 'direction': 'asc'}],
        render:{
            option: tournament_winner,
            item: tournament_winner
        }
    });
    $("#id_white").selectize({
        options: players,
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#white-help");
        },
        sortField: [{'field': 'username', 'direction': 'asc'}],
        render:{
            option: tournament_winner,
            item: tournament_winner,
        }
    });
};
