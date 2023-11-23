$(document).ready(function() {
    $('#likes').click(function() {
        var catid;
        catid = $(this).attr("data-catid");
        console.log("catid", catid)
		$.get('/rango/like/', {category_id: catid}, function(data){
            $('#like_count').html(data); //puts the data in id like_count
            $('#likes').hide();
        });
    });

    $('#suggestion').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest/', {suggestion: query}, function(data) {
            $('#cats').html(data) // puts the data where the id is cats
        });
    });

    $('.rango-add').click(function(){
	    var catid = $(this).attr("data-catid");
        var url = $(this).attr("data-url");
        var title = $(this).attr("data-title");
        console.log("catid", catid)
        console.log("url", url)
        console.log("title", title)
        var me = $(this)
        console.log("me", me)
	    $.get('/rango/add/', {category_id: catid, url: url, title: title}, 
                                function(data){
	                    $('#pages').html(data);
	                   me.hide();
	    });
	});
})