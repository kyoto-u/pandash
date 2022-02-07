$('.announcement_tr > td > a').on('click', function () {
    alert("clicked")
    var r_links = new Array();
    var link = $(this).attr('id');
    r_links.push(link);
    var resourcedata = JSON.stringify({ "r_id": r_links });
    $.ajax({
        type: 'POST',
        url: '/r_announcement_clicked',
        data: resourcedata,
        contentType: 'application/json',
        success: function (response) {
            alert(response["title"])
            $('#modal_announcement_title').html(response["title"])
            $('#modal_announcement_subject').html(response["subject"])
            $('#modal_announcement_publish_date').html(response["publish_date"])
            $('#modal_announcement_html_file').html(response["html_file"])
        },
        error: function (error) {
            console.log(error);
        }
    });
});
