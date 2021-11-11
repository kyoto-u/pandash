

$(function () {
    //お問い合わせテーブルにカーソルが乗ったときの処理
    $(".inquery_row").on("mouseover", function () {
        $(this).css("background-color","gainsboro");
    });

    //カーソルが離れたときの処理
    $(".inquery_row").on("mouseleave", function () {
        $(this).css("background-color", "");
    });
});


