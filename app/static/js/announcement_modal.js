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

//前のページボタンをクリックしたときの処理
$("#pills-previous-tab").on('click',function(){
    var page_now = $("a.page-link.active").attr("id");
    var page_now_num = Number(page_now.split("-")[2]);
    if(page_now_num != 1){
        $(this).attr("href","#pills-page-"+String(page_now_num - 1))
    }
});

//前のページボタンを押した後、タブ遷移したあとの処理
$("#pills-previous-tab").on("shown.bs.tab",function(event){
    var page_now = event.target["href"].split("#")[1]
    $("#" + page_now + "-tab").attr("class","page-link nav-link page-num-link active show")
    if(page_now == "pills-page-1"){
        $(this).attr("class","page-link nav-link disabled")
        $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5 d-none")
    }else{
        $(this).attr("class", "page-link nav-link")
    }
    $("#pills-next-tab").attr("class", "page-link nav-link")
    $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5")
});

//ページ数が１のときに次のページボタンを無効化する処理
$("#pills-next-tab").ready(function(){
    var max_page_num = $("a.page-num-link").length;
    if(max_page_num == 1){
        $("#pills-next-tab").attr("class","page-link nav-link disabled")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5 d-none")
    }
})

//次のページボタンをクリックしたときの処理
$("#pills-next-tab").on('click', function () {
    var page_now = $("a.page-link.active").attr("id");
    var page_now_num = Number(page_now.split("-")[2]);
    var max_page_num = $("a.page-num-link").length;
    if (page_now_num != max_page_num) {
        $(this).attr("href", "#pills-page-" + String(page_now_num + 1))
        
    }
});

//次のページボタンを押した後、タブ遷移したあとの処理
$("#pills-next-tab").on("shown.bs.tab", function (event) {
    var page_now = event.target["href"].split("#")[1]
    var max_page_num = $("a.page-num-link").length;

    $("#" + page_now + "-tab").attr("class", "page-link nav-link page-num-link active show")
    if (page_now == "pills-page-" + String(max_page_num)) {
        $(this).attr("class", "page-link nav-link disabled")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5 d-none")
    } else {
        $(this).attr("class", "page-link nav-link")
    }
    $("#pills-previous-tab").attr("class", "page-link nav-link")
    $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5")
});

//数字タブボタンを押してタブ遷移をしたあとの処理
$("a.page-num-link").on("shown.bs.tab",function(event){
    var page_now = event.target["href"].split("#")[1]
    var max_page_num = $("a.page-num-link").length;
    if (page_now == "pills-page-1") {
        $("#pills-previous-tab").attr("class", "page-link nav-link disabled")
        $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5 d-none")
        $("#pills-next-tab").attr("class", "page-link nav-link")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5")
    } else if (page_now == "pills-page-" + String(max_page_num)){
        $("#pills-previous-tab").attr("class", "page-link nav-link")
        $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5")
        $("#pills-next-tab").attr("class", "page-link nav-link disabled")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5 d-none")
    }else{
        $("#pills-previous-tab").attr("class", "page-link nav-link")
        $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5")
        $("#pills-next-tab").attr("class", "page-link nav-link")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5")
    }
});

//テーブル下部の前へ戻るボタンの処理
$("#alternative-previous-button").on("click",function(){
    var page_now = "#" + $("div.tab-pane.active").attr("id");
    var page_now_num = Number(page_now.split("-")[2]);
    if (page_now_num != 1) {
        var next_page = "#pills-page-" + String(page_now_num - 1)
        $(page_now).attr("class", "tab-pane fade")
        $(next_page).tab("show")
        $(page_now + "-tab").attr("class", "page-link nav-link page-num-link")
        $(next_page + "-tab").attr("class", "page-link nav-link page-num-link active")

        if (next_page == "#pills-page-1") {
            $("#pills-previous-tab").attr("class", "page-link nav-link disabled")
            $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5 d-none")
        }
        $("#pills-next-tab").attr("class", "page-link nav-link")
        $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5")

    }
    window.scrollTo(100, 0);
})

//テーブル下部の次のページボタンの処理
$("#alternative-next-button").on("click", function () {
    var page_now = "#" + $("div.tab-pane.active").attr("id");
    var page_now_num = Number(page_now.split("-")[2]);
    var max_page_num = $("a.page-num-link").length;
    if (page_now_num != max_page_num) {
        var next_page = "#pills-page-" + String(page_now_num + 1)
        $(page_now).attr("class", "tab-pane fade")
        $(next_page).tab("show")
        $(page_now + "-tab").attr("class", "page-link nav-link page-num-link")
        $(next_page + "-tab").attr("class", "page-link nav-link page-num-link active")

        if(next_page == "#pills-page-" + String(max_page_num)){
            $("#pills-next-tab").attr("class", "page-link nav-link disabled")
            $("#alternative-next-button").attr("class", "btn btn-link ml-auto px-5 d-none")
        }
        $("#pills-previous-tab").attr("class", "page-link nav-link")
        $("#alternative-previous-button").attr("class", "btn btn-link mr-auto px-5")


    }
    window.scrollTo(100, 0);
})

