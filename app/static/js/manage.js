

$(function () {

    $("td.contents").css("display","none");
    $("td.replied_contents").css("display","none");

    //お問い合わせテーブルにカーソルが乗ったときの処理
    $(".inquery_row").on("mouseover", function () {
        $(this).css("background-color","gainsboro");
    });

    //カーソルが離れたときの処理
    $(".inquery_row").on("mouseleave", function () {
        $(this).css("background-color", "");
    });

    $(".inquery_row").on("click", function(){
        inq_id = $(this).attr('id');
        td = $(this).children("td");
        date = td[0].innerHTML;
        title = td[1].innerHTML;
        content = td[2].innerHTML;
        replied_content = td[3].innerHTML;

        $(".inquery_form").attr("id", inq_id);
        $("#inquery_title")[0].innerHTML = title;
        $("#inquery_content")[0].innerHTML = content;
        $("#reply_textarea")[0].innerHTML = replied_content;
        
    });

    $("#reply_send_button").on("click", function(){
        var reply_content = $("#reply_textarea").val();
        var form_id = $(".inquery_form").attr("id");
        var reply_content_json = JSON.stringify({"reply_content":reply_content,"form_id":form_id});
        $.ajax({
            type: 'POST',
            url: '/manage_reply',
            data: reply_content_json,
            contentType: 'application/json',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });


});


