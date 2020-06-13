window.onload = function () {
    $("#id_bye_user").selectize();
    $("#id_add_users").selectize();

    $("#manage_submit").click(function () {
        $(".user-remove").each(function () {
            if($(this).prop('checked'))
                $("#id_remove_users").append($(this).prop('id'))
        })
    })
}