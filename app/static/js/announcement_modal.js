// announcement_listのモーダル表示に対応 

// announcements = [{'announcement_id': 'ddd', 'checked': 1, 
// 'title': 'ddd', 'html_file': 'ddd_body', 'subject': 'ccc', 
// 'classschedule': 'mon3', 'course_id': 'ccc', 
// 'publisher': 'xxxx', 'time_ms': 999999, 
// 'publish_date': '1970/01/01 09:16:39'}]

$('.announcement_tr').on('click', function () {
    var announcement_id = $(this).attr('id');
    var index = 0;
    $.each(announcements, function(key, value){
        if(value.announcement_id == announcement_id){
            return false;
        }
        index += 1;
    })
    // announcementsのリストを外したもの
    announcement = announcements[index];

    $('#modal_announcement_title').html("件名："+announcement['title']);
    $('#modal_announcement_subject').html("コースサイト：" + announcement['subject']);
    $('#modal_announcement_publish_date').html("公開日時：" + announcement["publish_date"]);
    $('#modal_announcement_html_file').html(announcement["html_file"]);

    var ancdata = JSON.stringify({"announcement_ids": [announcement_id]});

    $.ajax({
        type: 'POST',
        url: '/announcement_clicked',
        data: ancdata,
        contentType: 'application/json',
        success: function (response) {
            $('#modal_announcement_html_file').html(response["html_file"])
        },
        error: function (error) {
            console.log(error);
        }
    });
});

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

