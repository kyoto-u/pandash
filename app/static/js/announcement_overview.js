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
            'class': 'ml-3 my-2'
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
        for(let i=0;i<announcements_details.length;i++){
            var tr = $('<tr></tr>');
            tr.addClass('text-white');
            var th1 = $('<td></td>');
            th1.addClass('col-8');
            th1.html(announcements_details[i]['title']);
            var th2 = $('<td></td>');
            th2.addClass('col-4');
            th2.html(announcements_details[i]['publish_date']);
            tr.append(th1);
            tr.append(th2);
            body_table.append(tr);
        };
        body_div.append(body_table);
        body_div.append(body_table);

        parent_div.append(header_div);
        parent_div.append(body_div);

        // アニメーションをつける
        $('#course_announcement').append(parent_div);

    });

})