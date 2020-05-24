let users = {};


function cannot_find(user) {
    $("#messages").append(
        `                    
        <div class="alert alert-danger alert-dismissible fade show my-2" role="alert">
            Cannot find entry for user ${user}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        `
    )
}


function readUsers(text){
    let file_users = text.trim().split('\n');
    for(let i = 0;i < file_users.length;i++){
        if(file_users[i].trim() in users)
            document.getElementById("id_exclude_users").selectize.addItem(users[file_users[i].trim()]);
        else
            cannot_find(file_users[i].trim())
    }

}


window.onload = function () {
    $("option").each(function () {
        typeof $(this).text()
        users[`${$(this).text()}`] = $(this).val()
    })

    $("#id_exclude_users").selectize();

    $("#excludeUsersFile").on('change', function () {
        let reader = new FileReader();
        reader.onload = function () {
            readUsers(reader.result);
        };
        reader.readAsText($(this).prop('files')[0], "UTF-8");
    });


}