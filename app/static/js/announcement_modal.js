//このjsファイルは一覧表示・時間割表示に共通して適用されています
$('.announcement_tr').on('click', function () {
    var r_links = new Array();
    var link = $(this).attr('id');
    r_links.push(link);
    var resourcedata = JSON.stringify({ "r_id": r_links })

    //モーダルにタイトル、コースサイト名、公開日時を表示する準備
    var anno_list = "announcement_pagenation";
    var IsList = location.pathname.includes(anno_list);
    if(IsList){
        var obj = { "title": $(this).find("td").find("a").html(), "subject": $(this).find("td").first().html(), "publish_date": $(this).parent().parent().find("td").last().html() }
    }else{
        var obj = { "title": $(this).find("td").first().html(), "subject": $("#announcement_card > .card-header > .row > h2").html().split("の")[0], "publish_date": $(this).parent().parent().find("td").last().html() }
    }
    
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
    $('#modal_announcement_title').html("件名："+obj["title"])
    $('#modal_announcement_subject').html("コースサイト：" + obj["subject"])
    $('#modal_announcement_publish_date').html("公開日時：" + obj["publish_date"])
    $('#modal_announcement_html_file').html("<h3>読み込み中...</h3>")
}

