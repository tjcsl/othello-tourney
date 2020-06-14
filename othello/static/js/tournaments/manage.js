window.onload = function () {
    $("#id_bye_user").selectize();
    $("#id_add_users").selectize();

    $("#manage_submit").click(function (e) {
        let users = []
        $(".user-remove").each(function () {
            if($(this).prop('checked'))
                users.push($(this).prop('id'))
        })
        $("#id_remove_users").val(users);
    })
}