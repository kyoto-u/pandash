

$(function () {

    $("div.inquery_form").css("display","none")

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
        $("div.inquery_form").css("display","none");
        $("div.inquery_form#"+inq_id).css("display","block");
    });


});


