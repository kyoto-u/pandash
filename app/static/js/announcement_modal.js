$('.announcement_tr > td > a').on('click', function () {
    var r_links = new Array();
    var link = $(this).attr('id');
    r_links.push(link);
    var resourcedata = JSON.stringify({ "r_id": r_links });
    var obj = { "title": $(this).html(), "subject": $(this).parent().parent().find("td").first().html(), "publish_date": $(this).parent().parent().find("td").last().html()}
    loading(obj);
    $.ajax({
        type: 'POST',
        url: '/r_announcement_clicked',
        data: resourcedata,
        contentType: 'application/json',
        success: function (response) {
            $('#modal_announcement_html_file').html(response["html_file"])
        },
        error: function (error) {
            console.log(error);
        }
    });
});

function loading(obj){
    $('#modal_announcement_title').html(obj["title"])
    $('#modal_announcement_subject').html("コースサイト：" + obj["subject"])
    $('#modal_announcement_publish_date').html("公開日時：" + obj["publish_date"])
    $('#modal_announcement_html_file').html("<h3>読み込み中...</h3>")
}
