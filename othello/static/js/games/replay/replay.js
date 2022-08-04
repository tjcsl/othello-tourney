function noFileUploaded(){
    $("#black-logs-area").append(`<pre class="err_log">No Game File Uploaded</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">No Game File Uploaded</pre>`);
}

function errorParsing(){
    $("#black-logs-area").append(`<pre class="err_log">Error Parsing File at Specified Format</pre>`);
    $("#white-logs-area").append(`<pre class="err_log">Error Parsing File at Specified Format</pre>`);
}

function clearErrors(){
    $("pre.err_log").remove();
}

function parseReplay(text, isParseable){
    console.log(isParseable);
    console.log(text);
}

async function handleUpload(){
    console.log('called');
    const isParseable = $("#replayParseable").is(":checked");

    const file = document.getElementById("replayFile").files[0];
    if(!file){
        noFileUploaded();
        return;
    }
    const text = await file.text();
    parseReplay(text, isParseable);

}

window.onload = function () {
    $("#replayModal").modal('show');
    
    let rCanvas = init("", "");
    $(".canvasContainer").width($("#canvas").width());
    $(window).on('resize', function () {
        rCanvas.resize();
        $(".canvasContainer").width($("#canvas").width());
    });

    function mouseOver(event){
        highlight_tile(rCanvas, event);
    }

    $(document).on('mousemove', mouseOver);
    $("#submitReplay").click(handleUpload);
};