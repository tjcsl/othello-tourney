tippy("#name-help", {
    content: "Give your script a label so it will be easier to identify later (e.g. \"negamax with alpha beta\")",
    placement: "bottom",
});

tippy("#watch-help", {
    content: "Reload the page to refresh the list",
    placement: "top"
});

tippy("#pretty-help", {
    content: "Prints board in readable format, line below board is [black_score]-[white_score] [player]",
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

tippy("#inlude_users_file_help", {
    content: "Upload a CSV file with each included user in a separate entry, users should be split by newline." +
        " Users read from this file will be added to the above field.",
    placement: "right"
})

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
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
