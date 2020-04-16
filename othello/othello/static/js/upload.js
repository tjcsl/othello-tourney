window.onload = function () {
    $("#id_new_script").selectize();
    $("#download_script").click(function () {
        $("#change_action").val("download_submission");
        $("#submit_change_script").click();
    })
}