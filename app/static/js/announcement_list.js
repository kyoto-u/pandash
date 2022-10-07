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