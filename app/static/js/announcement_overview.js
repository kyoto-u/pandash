$(function (){
    window_load();
    window.onresize = window_load;

    function window_load(){
        var display_width = $(window).width();
    }

    $('td.tcell_announce_overview').on('click', function(){
        // もとの表示を消す
        $('#announcement_card').fadeOut('fast').queue(function(){
            $('#announcement_card').remove();
        })

        var element_id = $(this).attr('id');
        var course = announcements[element_id]
        var subject = course["subject"]
        var announcements_details = course["announcements"];
        var parent_div = $('<div></div>',{
            'id': 'announcement_card',
            'class': 'card text-white',
            'style': 'min-height: 100vh; max-height: 100vh;'
        });
        var header_div = $('<div></div>',{
            'class': 'card-header',
            'style': 'background-color:rgb(90, 98, 107)'
        });
        var title_div = $('<div></div>',{
            'class': 'row'
        });
        var title_h2 = $('<h2></h2>',{
            'class': 'ml-3 my-2 active_course',
            'name': element_id
        });
        title_h2.html(subject + "のお知らせ");
        title_div.append(title_h2);
        header_div.append(title_div);

        var body_div = $('<div></div>',{
            'class': 'card-body bg-secondary',
            'style': 'overflow-x:auto; overflow-y:hidden',
            'id': 'card-body'
        });
        var body_table = $('<table></table>',{
            'class': 'table'
        });
        var tr1 = $('<tr></tr>');
        tr1.addClass('text-white');
        var th1 = $('<th></th>');
        th1.addClass('col-8');
        th1.html('件名');
        var th2 = $('<th></th>');
        th2.addClass('col-4');
        th2.html('公開日時');
        tr1.append(th1);
        tr1.append(th2);
        body_table.append(tr1)
        for(let i=0;i<announcements_details.length;i++){
            var tr2 = $('<tr></tr>',{
                'class': 'announcement_tr',
                'id': announcements_details[i]['announcement_id'],
                'data-toggle': 'modal',
                'data-target': '#modal_announcement',
                'name': i,
                'style': 'color:white'
            });
            var td1 = $('<td></td>');
            td1.addClass('col-8');
            var a_link = $('<a></a>',{
                'href': '#',
                'style': 'color:inherit'
            });
            a_link.html(announcements_details[i]['title']);
            td1.append(a_link);
            var td2 = $('<td></td>');
            td2.addClass('col-4');
            td2.html(announcements_details[i]['publish_date']);
            tr2.append(td1);
            tr2.append(td2);
            body_table.append(tr2);
        };
        body_div.append(body_table);
        body_div.append(body_table);

        parent_div.append(header_div);
        parent_div.append(body_div);

        // アニメーションをつける
        $('#course_announcement').append(parent_div);

        // mouse over
        var targets = document.getElementsByClassName("announcement_tr");
        for (var i = 0; i < targets.length; i++) {
            targets[i].addEventListener("mouseover", function () {
                this.setAttribute("style", "color:black; background-color:whitesmoke;");
            });
    
            targets[i].addEventListener("mouseleave", function () {
                this.setAttribute("style", "color:white;");
            });
        }
        for (var i = 0; i < targets.length; i++) {
            targets[i].setAttribute("style", "color: white;");
        };

    });

    // ？トリガーが不安定
    $('tr.announcement_tr').on('click', function(){
        var element_id = $('.active_course').attr('name');
        var index = $(this).attr('name');
        var course = announcements[element_id];
        var subject = course["subject"];
        var announcements_detail = course["announcements"][index];

        var r_links = new Array();
        var link = $(this).attr('id');
        r_links.push(link);
        var resourcedata = JSON.stringify({ "r_id": r_links });

        // モーダルにタイトル、コースサイト名、公開日時を表示する準備
        // var anno_list = "announcement_pagenation";
        // var IsList = location.pathname.includes(anno_list);
        // if(IsList){
        //     var obj = { "title": $(this).find("td").find("a").html(), "subject": $(this).find("td").first().html(), "publish_date": $(this).parent().parent().find("td").last().html() }
        // }else{
        //     var obj = { "title": $(this).find("td").first().html(), "subject": $("#announcement_card > .card-header > .row > h2").html().split("の")[0], "publish_date": $(this).parent().parent().find("td").last().html() }
        // }
    
        $('#modal_announcement_title').html("件名："+announcements_detail['title']);
        $('#modal_announcement_subject').html("コースサイト：" + subject);
        $('#modal_announcement_publish_date').html("公開日時：" + announcements_detail["publish_date"]);
        $('#modal_announcement_html_file').html("<h3>"+ announcements_detail["html_file"] +"</h3>");

        $.ajax({
            type: 'POST',
            url: '/r_announcement_clicked',
            data: resourcedata,
            contentType: 'application/json',
            success: function (response) {
                $('#modal_announcement_html_file').html(response["html_file"]);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

})