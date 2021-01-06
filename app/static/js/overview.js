$(function() {
    $("#finish_form").droppable({
      accept: ".taskcard",
      scroll: false,
      tolerance: "touch",
      activeClass: "active-d", //Draggable要素がドラッグしている際に適用
      hoverClsaa: "hover-d",   //Draggable要素が上に乗った時に適用
      drop: function(event, ui){
        dr_text = ui.draggable.find("a").text();
        dr_id = ui.draggable.find("a").attr("href");
        dr_sub = ui.draggable.parent().find('.course').text();
        if(dr_sub.length==0){
          dr_sub = ui.draggable.parent().parent().find('.othcourse').text();
        }
        var add_div_1 = $('<div></div>');
        var add_div_2 = $('<div></div>');
        var add_li = $('<li></li>');
        add_div_1.addClass("mx-auto new_card");
        add_div_2.addClass("row");
        add_li.addClass("list-group-item finished-list-item");
        add_a = $('<a></a>');
        add_button = $('<button></button>');
        add_i = $('<i></i>');
        add_i.addClass("fas fa-times");
        add_button.append(add_i);
        add_a.attr("href", dr_id);
        add_a.html(dr_text);
        add_li.html(dr_sub);
        add_li.append($('<br>'));
        add_li.append(add_a);
        add_div_2.append(add_li);
        add_div_2.append(add_button);
        add_div_1.append(add_div_2);
        console.log(add_div_1);
        $("#finished_taskslist").append(add_div_1);
        ui.draggable.css("display", "none")
        var dr_ids = new Array();
        dr_ids.push(dr_id);
        var task_id = JSON.stringify({"task_id":dr_ids});
        $.ajax({
          type: "POST",
          url: "/task_finish",
          data: task_id,
          contentType: "application/json",
          success: function(response){
            console.log(response);
          },
          error: function(error){
            console.log(error);
          }
        })
      }
    });
    $(".taskcard").draggable({
      helper: "clone",
      revert: "invalid",
      start: function(event, ui){
        $("#overview_table").removeClass("table-responsive"),
        $(ui.helper).css({
          'width': $(this).width(),
          'zIndex': 1000,
          // 見やすいよう，背景色をつけておく
          'background-color': "#99cc00"
        })
      },
      stop: function(event, ui){
        $("#overview_table").addClass("table-responsive");
        $(".new_card").draggable({
          helper: "clone",
          revert: "invalid",
          start: function(event, ui){
            $("#overview_table").removeClass("table-responsive"),
            $(ui.helper).css({
              'width': $(this).width(),
              'zIndex': 1000
            })
          },
          stop: function(event, ui){
            $("#overview_table").addClass("table-responsive");
          }
        });
      }
    });

    $("#all_table").droppable({
      accept: ".new_card",
      scroll: false,
      tolerance: "touch",
      drop: function(event, ui){
        dr_text = ui.draggable.find('a').text();
        dr_id = ui.draggable.find('a').attr('href');
        old_task = $('#' + dr_id);
        old_task.css("display", "block");
        ui.draggable.remove();
        var dr_ids = new Array();
        dr_ids.push(dr_id);
        var task_id = JSON.stringify({"task_id":dr_ids});
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
        })
      }

      
    })


})
