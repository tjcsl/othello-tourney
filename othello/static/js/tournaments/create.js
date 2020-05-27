let users = {};


function readUsers(text){
    let file_users = text.trim().split('\n');
    for(let i = 0;i < file_users.length;i++){
        if(file_users[i].trim() in users)
            document.getElementById("id_include_users").selectize.addItem(users[file_users[i].trim()]);
        else
            add_error(`Cannot find entry for user ${file_users[i].trim()}`)
    }

}


window.onload = function () {
    $("option").each(function () {
        typeof $(this).text()
        users[`${$(this).text()}`] = $(this).val()
    })

    $("#id_include_users").selectize();

    $("#includeUsersFile").on('change', function () {
        let reader = new FileReader();
        reader.onload = function () {
            readUsers(reader.result);
        };
        reader.readAsText($(this).prop('files')[0], "UTF-8");
    });


}