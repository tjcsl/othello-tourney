tippy("#name-help", {
    content: "Give your script a label so it will be easier to identify later (e.g. \"negamax with alpha beta\")",
    placement: "bottom",
});

tippy("#watch-help", {
    content: "Reload the page to refresh the list",
    placement: "top"
});

tippy("#pretty-help", {
    content: "Prints board in readable format, line below board is [black_score]-[white_score] [player] to [move]",
    placement: "top",
});

tippy("#parseable-help", {
    content: "Prints board in parseable format, format is [board] [player] [move] [black_score] [white_score]",
    placement: "top",
});

tippy(".yourself", {
    content: "Choosing the \"Yourself\" player will allow you to manually choose a move. \"Yourself\" players will have " +
        "5 minutes to choose a move regardless of the specified time limit. Other players will adhere to the time limit.",
    placement: "right"
})

tippy(".score", {
    content: "The score shown assumes that the game ended with 64 tokens on the board. " +
        "This doesn't always happen, so the score here might be wrong.",
    placement: "right"
})

tippy("#include_users_file_help", {
    content: "Upload a CSV file with each included user in a separate entry, users should be split by newline." +
        " Users read from this file will be added to the above field.",
    placement: "right"
})

tippy("#runoff-help", {
    content: "Enables time hoarding every move. " +
         "(ex. If the time limit is 5s but your script takes 4s one turn, you will get 6s next round)",
    placement: "right"
})

tippy("#bye-help", {
    content: "If are an odd amount of players participating in the tournament, the odd person out will be matched against this player." +
        "This player should very likely be an AI implementing a random choice algorithm",
    placement: "right"
})

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
}

if(!String.prototype.replaceAt){
    String.prototype.replaceAt = function(index, replacement) {
        return this.substr(0, index) + replacement + this.substr(index + replacement.length);
    }
}

function add_error(message){
    $("#messages").append(
        `
        <div class="alert alert-danger alert-dismissible fade show my-2" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        `
    )
}


function download(filename, text) {
  let element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
$(document).ready(function() {
    setTimeout(function (){
        $(".alert").alert('close');
    }, 10000);
});
