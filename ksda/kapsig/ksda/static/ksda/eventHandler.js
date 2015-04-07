function addComment(id){
	var text = document.getElementById("comment-" + String(id)).value;
	
	 $.ajax({
	 	type: "GET",
        url: "/ksda/get-comment-html?id=" + id + "&text=" + text,
        success: function( result ) {
                $("#comment-group-" + String(id)).append(result);
        }
    });
}