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

window.onload = function () {
    helps()
    $("#id_black").selectize({
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#black-help");
        },
        sortField: [{'field': 'text', 'direction': 'desc'}],
        render:{
            option: tournament_winner,
            item: tournament_winner
        }
    });
    $("#id_white").selectize({
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#white-help");
        },
        sortField: [{'field': 'text', 'direction': 'desc'}],
        render:{
            option: tournament_winner,
            item: tournament_winner,
        }
    });
};
