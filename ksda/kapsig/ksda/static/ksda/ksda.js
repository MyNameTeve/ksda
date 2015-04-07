window.setInterval(function () {
    $.ajax({
        url: "/ksda/get-stream-json",
        dataType : "html",
        success: function( result ) {
                $("#list-group").prepend(result);
        }
    });
}, 5000);


