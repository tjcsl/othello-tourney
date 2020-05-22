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

window.onload = function () {
    helps()
    $("#id_black").selectize({
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#black-help");
        }
    });
    $("#id_white").selectize({
        maxItems: 1,
        onChange: function (val) {
            showYourselfHelp(val, "#white-help");
        }
    });
};