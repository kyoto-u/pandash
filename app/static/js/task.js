$(function() {
    window_load();
    window.onresize = window_load;

    function window_load(){
      var display_width = $(window).width();
      $('a.task_link').on('click', function(){
        var quiz = $(this).attr('name');
        var post_url = ''
        if (quiz=="True"){
          post_url = '/quiz_clicked';
        } else if (quiz=="False"){
          post_url = '/task_clicked';
        }
        var task_ids = new Array();
        var task_id = $(this).parent().parent().attr('id');
        $(this).parent().parent().find('i').remove();
        task_ids.push(task_id);
        var task_ids = JSON.stringify({"task_ids":task_ids});
        $.ajax({
            type: 'POST',
            url: post_url,
            data: task_ids,
            contentType: 'application/json',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
      if (display_width >= 768){
        $('#finish_form').droppable({
          accept: ".acdrag",
          tolerance: "touch",
          activeClass: "active-d", //Draggable要素がドラッグしている際に適用
          hoverClsaa: "hover-d",   //Draggable要素が上に乗った時に適用
          drop: function(event, ui){
            dr_text = ui.draggable.find('.task_title').text();
            dr_id = ui.draggable.find('.task_tag').attr("href");
            dr_sub = ui.draggable.find('.subject').text();
            assignment_id = ui.draggable.attr("id");
            var add_div_1 = $('<div></div>');
            var add_div_2 = $('<div></div>');
            var add_li = $('<li></li>');
            add_div_1.addClass("mx-auto new_task");
            add_div_2.addClass("row");
            add_li.addClass("list-group-item finished-list-item");
            add_a = $('<a></a>');
            add_button = $('<button></button>');
            add_button.attr("id", assignment_id+"btn");
            add_button.addClass("new_task_btn");
            add_i = $('<i></i>');
            add_i.addClass("fas fa-times");
            add_button.append(add_i);
            add_a.attr("href", dr_id);
            add_a.attr("id", assignment_id+"new");
            add_a.html(dr_text);
            add_li.html(dr_sub);
            add_li.append($('<br>'));
            add_li.append(add_a);
            add_div_2.append(add_li);
            add_div_2.append(add_button);
            add_div_1.append(add_div_2);
            $("#finished_taskslist").append(add_div_1);
            ui.draggable.css("display", "none");
            ui.draggable.find('td').css("display", "none")
            var a_ids = new Array();
            a_ids.push(assignment_id);
            var task_id = JSON.stringify({"task_id":a_ids});
            $.ajax({
              type: 'POST',
              url: '/task_finish',
              data: task_id,
              contentType: 'application/json',
              success: function(response){
                console.log(response);
              },
              error: function(error){
                console.log(error);
              }
            })
            $('#finished_list_num').text($('#finished_taskslist > div').length);
          }
        });
        $('.acdrag').draggable({
          helper: "clone",
          revert: "invalid",
          start: function(event, ui){
            $("#table").removeClass("table-responsive"),
            $(ui.helper).css({
              'width': $(this).width(),
              'zIndex': 1000
            });
          },
          stop: function(event, ui){
            $('.new_task_btn').on('click', function(){
              dr_id = $(this).parent().parent().find('li').find('a').attr('href');
              new_assignment_id = $(this).parent().parent().find('li').find('a').attr('id');
              assignment_id = new_assignment_id.slice(0,-3);
              old_task = $('#' + assignment_id);
              old_task.css("display", "table");
              old_task.find('td').css("display", "block");
              $(this).parent().parent().remove();
              var a_ids = new Array();
              a_ids.push(assignment_id);
              var task_id = JSON.stringify({"task_id":a_ids});
              $.ajax({
                type: 'POST',
                url: '/task_unfinish',
                data: task_id,
                contentType: 'application/json',
                success: function(response){
                  console.log(response);
                },
                error: function(error){
                  console.log(error);
                }
              });
              $('#finished_list_num').text($('#finished_taskslist > div').length);

            });
            $('.new_task').draggable({
              helper: "clone",
              revert: "invalid",
              start: function(event, ui){
                $(ui.helper).css({
                  'width': $(this).width(),
                  'zIndex': 1000
                });
              },
              stop: function(event, ui){
                $("#table").addClass("table-responsive");
              }
            }),
            $("#table").addClass("table-responsive");
          }
        });

        $('#dragArea').droppable({
          accept: ".new_task",
          tolerance: "touch",
          drop: function(event,ui){
            dr_text = ui.draggable.find('a').text();
            dr_id = ui.draggable.find('a').attr('href');
            new_assignment_id = ui.draggable.find('a').attr('id');
            assignment_id = new_assignment_id.slice(0,-3);
            old_task = $('#' + assignment_id);
            old_task.css("display", "table");
            old_task.find('td').css("display", "block");
            ui.draggable.remove();
            var a_ids = new Array();
            a_ids.push(assignment_id);
            var task_id = JSON.stringify({"task_id":a_ids});
            $.ajax({
              type: 'POST',
              url: '/task_unfinish',
              data: task_id,
              contentType: 'application/json',
              success: function(response){
                console.log(response);
              },
              error: function(error){
                console.log(error);
              }
            });
            $('#finished_list_num').text($('#finished_taskslist > div').length -1);
          }
        });
      }


    }


})

function select3a_change(value){
  var loc_str = location.href
  var loc = location.href.split("/")
  // var show_only_unfinished = loc[loc.length-2]
  // var max_time_left = loc[loc.length-1]
  new_loc = ''
  new_location = ''
  switch(value){
    case "show-only-0":
      // new_loc = '0/' + max_time_left;
      new_loc = '0/3'
      break;
    case "show-only-1":
      // new_loc = '1/' + max_time_left;
      new_loc = '1/3'
      break;
    case "max-1":
      // new_loc = show_only_unfinished + '/1';
      new_loc = '0/1'
      break;
    case "max-2":
      // new_loc = show_only_unfinished + '/2';
      new_loc = '0/2'
      break;
  }
  new_location = loc_str.substring(0, loc_str.length-3) + new_loc
  window.location.href = new_location
  return false;
}
